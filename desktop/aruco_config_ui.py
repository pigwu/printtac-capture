from __future__ import annotations

import time
from collections import deque
import shutil
import sys
from pathlib import Path

from runtime_paths import get_app_base_dir

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from aruco_gripper_tracker import (
    ArucoEstimator,
    CameraIntrinsics,
    CyclicCalibrationSummary,
    TrackerConfig,
    calculate_distance_calibration,
    summarize_cyclic_calibration,
)


class ArucoConfigWidget(QWidget):
    """Compact two-point calibration UI for per-frame gripper distance."""

    apply_requested = pyqtSignal(object)

    def __init__(self, config_path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = get_app_base_dir()
        self.last_raw_distance_m: float | None = None
        self.last_marker_depths_m: dict[str, float] = {}
        self.recent_raw_samples: deque[tuple[float, float]] = deque(maxlen=30)
        self.distance_scale = 1.0
        self.distance_offset_m = 0.0
        self.calibration_collecting = False
        self.calibration_samples_m: list[float] = []
        self.calibration_collection_summary: CyclicCalibrationSummary | None = None
        self._ensure_initial_config(config_path)
        self._build_ui(config_path)
        self.load_configuration(show_dialog=False)

    @staticmethod
    def _ensure_initial_config(config_path: Path) -> None:
        if config_path.is_file() or not getattr(sys, "frozen", False):
            return
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        bundled = bundle_root / "config" / "umi_gripper_aruco.json"
        if bundled.is_file():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bundled, config_path)

    @staticmethod
    def _double_spin(
        minimum: float,
        maximum: float,
        decimals: int,
        step: float,
        suffix: str = "",
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        spin.setSingleStep(step)
        if suffix:
            spin.setSuffix(suffix)
        return spin

    def _raw_point_spin(self) -> QDoubleSpinBox:
        spin = self._double_spin(-1.0, 5000.0, 4, 0.1, " mm")
        spin.setSpecialValueText("Not recorded")
        spin.setValue(-1.0)
        spin.setToolTip("Filled automatically after recording open/close cycles. You can also edit the raw X-axis width manually.")
        return spin

    def _build_ui(self, config_path: Path) -> None:
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)

        summary = QLabel(
            "Measure the gripper opening in each frame using the UMI-FT method. Attach markers 0 and 1 to the two moving jaws. "
            "The raw width is the difference between their camera X coordinates. Quick setup: use the current depth → "
            "close and capture the minimum → open and capture the maximum → save and apply."
        )
        summary.setWordWrap(True)
        summary.setStyleSheet(
            "padding:10px; background:#263238; color:#ffffff; border-radius:5px; font-size:14px;"
        )
        layout.addWidget(summary)

        live_box = QGroupBox("Current Frame")
        live = QGridLayout(live_box)
        self.live_status_label = QLabel("Waiting for monitoring to start")
        self.live_status_label.setWordWrap(True)
        live.addWidget(self.live_status_label, 0, 0, 1, 3)
        self.current_raw_label = QLabel("--")
        self.current_gap_label = QLabel("--")
        self.filtered_gap_label = QLabel("--")
        for column, (title, value) in enumerate(
            [
                ("Raw camera X width", self.current_raw_label),
                ("Calibrated opening", self.current_gap_label),
                ("Filtered opening", self.filtered_gap_label),
            ]
        ):
            title_label = QLabel(title)
            title_label.setStyleSheet("color:#607d8b;")
            value.setStyleSheet("font-size:20px; font-weight:600;")
            live.addWidget(title_label, 1, column)
            live.addWidget(value, 2, column)
        self.live_detail_label = QLabel("Detected IDs: --")
        self.live_detail_label.setWordWrap(True)
        live.addWidget(self.live_detail_label, 3, 0, 1, 3)
        layout.addWidget(live_box)

        marker_box = QGroupBox("1. Marker Settings")
        marker_layout = QGridLayout(marker_box)
        self.dictionary_combo = QComboBox()
        self.dictionary_combo.setEditable(True)
        self.dictionary_combo.addItems(["DICT_4X4_50", "DICT_5X5_50", "DICT_6X6_50"])
        self.marker_size_mm = self._double_spin(0.1, 500.0, 3, 0.1, " mm")
        self.marker_ids_edit = QLineEdit("0,1")
        self.nominal_depth_mm_spin = self._double_spin(1.0, 1000.0, 3, 0.5, " mm")
        self.nominal_depth_mm_spin.setValue(72.0)
        self.depth_tolerance_mm_spin = self._double_spin(0.1, 200.0, 3, 0.5, " mm")
        self.depth_tolerance_mm_spin.setValue(8.0)
        for column, (label, widget, tip) in enumerate(
            [
                ("Dictionary", self.dictionary_combo, "The included PDF uses DICT_4X4_50."),
                ("Black outer edge length", self.marker_size_mm, "The printed marker should measure 16.000 mm along its black outer edge."),
                ("Two marker IDs", self.marker_ids_edit, "Default: 0,1. Both markers must be detected in the same frame."),
            ]
        ):
            marker_layout.addWidget(QLabel(label), 0, column)
            marker_layout.addWidget(widget, 1, column)
            widget.setToolTip(tip)
        marker_layout.addWidget(QLabel("Nominal marker depth"), 2, 0)
        marker_layout.addWidget(self.nominal_depth_mm_spin, 3, 0)
        marker_layout.addWidget(QLabel("Depth tolerance"), 2, 1)
        marker_layout.addWidget(self.depth_tolerance_mm_spin, 3, 1)
        depth_hint = QLabel("UMI-FT default: 72 ± 8 mm. Adjust to the actual camera-to-marker depth for your mounting.")
        depth_hint.setWordWrap(True)
        depth_hint.setStyleSheet("color:#546e7a;")
        marker_layout.addWidget(depth_hint, 2, 2)
        self.use_current_depth_button = QPushButton("Use Current Depth and Apply")
        self.use_current_depth_button.setToolTip(
            "Use the midpoint of the two current marker depths, with a tolerance of at least ±20 mm."
        )
        self.use_current_depth_button.clicked.connect(self.use_current_marker_depth)
        marker_layout.addWidget(self.use_current_depth_button, 3, 2)
        layout.addWidget(marker_box)

        calibration_box = QGroupBox("2. Quick Two-Point Calibration")
        calibration = QGridLayout(calibration_box)
        calibration.addWidget(QLabel("Position"), 0, 0)
        calibration.addWidget(QLabel("Actual opening (caliper)"), 0, 1)
        calibration.addWidget(QLabel("Recorded X width"), 0, 2)
        calibration.addWidget(QLabel("Hold still for 1 s, then click"), 0, 3)

        self.minimum_gap_mm_spin = self._double_spin(0.0, 2000.0, 3, 0.1, " mm")
        self.maximum_gap_mm_spin = self._double_spin(0.0, 2000.0, 3, 0.1, " mm")
        self.minimum_raw_mm_spin = self._raw_point_spin()
        self.maximum_raw_mm_spin = self._raw_point_spin()
        self.calibration_min_cycles_spin = QSpinBox()
        self.calibration_min_cycles_spin.setRange(2, 20)
        self.calibration_min_cycles_spin.setValue(5)

        calibration.addWidget(QLabel("Minimum opening"), 1, 0)
        calibration.addWidget(self.minimum_gap_mm_spin, 1, 1)
        calibration.addWidget(self.minimum_raw_mm_spin, 1, 2)
        self.capture_minimum_button = QPushButton("Capture Minimum")
        self.capture_minimum_button.clicked.connect(self.capture_minimum_point)
        calibration.addWidget(self.capture_minimum_button, 1, 3)
        calibration.addWidget(QLabel("Maximum opening"), 2, 0)
        calibration.addWidget(self.maximum_gap_mm_spin, 2, 1)
        calibration.addWidget(self.maximum_raw_mm_spin, 2, 2)
        self.capture_maximum_button = QPushButton("Capture Maximum")
        self.capture_maximum_button.clicked.connect(self.capture_maximum_point)
        calibration.addWidget(self.capture_maximum_button, 2, 3)

        self.quick_calibration_status_label = QLabel(
            "Enter the minimum and maximum openings measured with calipers, then hold the gripper at each endpoint and capture it."
        )
        self.quick_calibration_status_label.setWordWrap(True)
        self.quick_calibration_status_label.setStyleSheet("color:#1565c0;")
        calibration.addWidget(self.quick_calibration_status_label, 3, 0, 1, 4)

        quick_apply_button = QPushButton("Finish: Save and Apply Calibration")
        quick_apply_button.setStyleSheet("font-weight:600; padding:6px 16px;")
        quick_apply_button.clicked.connect(self.finish_quick_calibration)
        calibration.addWidget(quick_apply_button, 4, 0, 1, 4)

        self.show_cyclic_calibration_checkbox = QCheckBox("Optional: Record open/close cycles for robust calibration")
        calibration.addWidget(self.show_cyclic_calibration_checkbox, 5, 0, 1, 4)
        self.cyclic_calibration_widget = QWidget()
        cyclic = QGridLayout(self.cyclic_calibration_widget)
        cyclic.setContentsMargins(0, 0, 0, 0)
        cyclic.addWidget(QLabel("Minimum complete cycles"), 0, 0)
        cyclic.addWidget(self.calibration_min_cycles_spin, 0, 1)
        self.start_collection_button = QPushButton("Start Recording")
        self.finish_collection_button = QPushButton("Finish and Calculate")
        self.finish_collection_button.setEnabled(False)
        self.clear_collection_button = QPushButton("Clear Recording")
        self.start_collection_button.clicked.connect(self.start_calibration_collection)
        self.finish_collection_button.clicked.connect(self.finish_calibration_collection)
        self.clear_collection_button.clicked.connect(self.clear_calibration_collection)
        controls = QHBoxLayout()
        controls.addWidget(self.start_collection_button)
        controls.addWidget(self.finish_collection_button)
        controls.addWidget(self.clear_collection_button)
        cyclic.addLayout(controls, 1, 0, 1, 3)
        self.collection_status_label = QLabel("Recording has not started")
        self.collection_status_label.setWordWrap(True)
        cyclic.addWidget(self.collection_status_label, 2, 0, 1, 3)

        calculate_button = QPushButton("Recalculate from the Endpoints Above")
        calculate_button.clicked.connect(self.calculate_two_point_calibration)
        cyclic.addWidget(calculate_button, 3, 0, 1, 3)
        self.cyclic_calibration_widget.setVisible(False)
        self.show_cyclic_calibration_checkbox.toggled.connect(
            self.cyclic_calibration_widget.setVisible
        )
        calibration.addWidget(self.cyclic_calibration_widget, 6, 0, 1, 4)
        self.calibration_result_label = QLabel("Two-point calibration incomplete")
        self.calibration_result_label.setWordWrap(True)
        self.calibration_result_label.setStyleSheet(
            "padding:7px; background:#eceff1; border-radius:4px;"
        )
        calibration.addWidget(self.calibration_result_label, 7, 0, 1, 4)
        formula = QLabel(
            "Quick capture uses the median of about 1 second of stable frames to reduce jitter. Record repeated open/close cycles if greater robustness is needed."
        )
        formula.setWordWrap(True)
        formula.setStyleSheet("color:#546e7a;")
        calibration.addWidget(formula, 8, 0, 1, 4)
        layout.addWidget(calibration_box)

        output_box = QGroupBox("3. Output and Save")
        output = QGridLayout(output_box)
        self.enabled_checkbox = QCheckBox("Enable per-frame ArUco measurement and UDP output")
        self.enabled_checkbox.setChecked(True)
        self.output_host_edit = QLineEdit("127.0.0.1")
        self.output_port_spin = QSpinBox()
        self.output_port_spin.setRange(1, 65535)
        self.output_port_spin.setValue(5570)
        self.smoothing_alpha_spin = self._double_spin(0.01, 1.0, 3, 0.05)
        self.smoothing_alpha_spin.setValue(1.0)
        self.smoothing_alpha_spin.setToolTip("1.0 disables smoothing. Lower values give smoother output with more delay.")
        output.addWidget(self.enabled_checkbox, 0, 0, 1, 3)
        for column, (label, widget) in enumerate(
            [
                ("UDP receiver IP", self.output_host_edit),
                ("UDP port", self.output_port_spin),
                ("EMA smoothing factor", self.smoothing_alpha_spin),
            ]
        ):
            output.addWidget(QLabel(label), 1, column)
            output.addWidget(widget, 2, column)
        layout.addWidget(output_box)

        self.show_advanced_checkbox = QCheckBox("Advanced: configuration file, APV1 intrinsics and detection thresholds")
        layout.addWidget(self.show_advanced_checkbox)
        self.advanced_box = QGroupBox("Advanced Settings")
        advanced = QVBoxLayout(self.advanced_box)

        file_layout = QHBoxLayout()
        self.config_path_edit = QLineEdit(str(config_path))
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_configuration)
        load_button = QPushButton("Reload")
        load_button.clicked.connect(self.load_configuration)
        file_layout.addWidget(QLabel("Configuration file"))
        file_layout.addWidget(self.config_path_edit, 1)
        file_layout.addWidget(browse_button)
        file_layout.addWidget(load_button)
        advanced.addLayout(file_layout)

        camera_box = QGroupBox("Legacy APV1 Fallback Intrinsics (leave disabled for APV2)")
        camera = QGridLayout(camera_box)
        self.manual_intrinsics_checkbox = QCheckBox("Use manual intrinsics")
        camera.addWidget(self.manual_intrinsics_checkbox, 0, 0, 1, 6)
        self.fx_spin = self._double_spin(0.0, 20000.0, 4, 1.0)
        self.fy_spin = self._double_spin(0.0, 20000.0, 4, 1.0)
        self.cx_spin = self._double_spin(-20000.0, 20000.0, 4, 1.0)
        self.cy_spin = self._double_spin(-20000.0, 20000.0, 4, 1.0)
        self.image_width_spin = QSpinBox()
        self.image_width_spin.setRange(1, 16384)
        self.image_width_spin.setValue(1280)
        self.image_height_spin = QSpinBox()
        self.image_height_spin.setRange(1, 16384)
        self.image_height_spin.setValue(720)
        for index, (label, widget) in enumerate(
            [
                ("fx", self.fx_spin),
                ("fy", self.fy_spin),
                ("cx", self.cx_spin),
                ("cy", self.cy_spin),
                ("Width", self.image_width_spin),
                ("Height", self.image_height_spin),
            ]
        ):
            row = 1 + index // 3
            column = (index % 3) * 2
            camera.addWidget(QLabel(label), row, column)
            camera.addWidget(widget, row, column + 1)
        self.distortion_edit = QLineEdit("0,0,0,0,0")
        camera.addWidget(QLabel("Distortion coefficients"), 3, 0)
        camera.addWidget(self.distortion_edit, 3, 1, 1, 5)
        self.manual_intrinsics_checkbox.toggled.connect(self._set_intrinsics_enabled)
        self._set_intrinsics_enabled(False)
        advanced.addWidget(camera_box)

        quality_box = QGroupBox("Detection Quality Thresholds")
        quality = QFormLayout(quality_box)
        self.max_reprojection_spin = self._double_spin(0.1, 50.0, 3, 0.1, " px")
        self.min_perimeter_spin = self._double_spin(4.0, 10000.0, 1, 5.0, " px")
        quality.addRow("Maximum reprojection error", self.max_reprojection_spin)
        quality.addRow("Minimum marker perimeter", self.min_perimeter_spin)
        advanced.addWidget(quality_box)
        self.advanced_box.setVisible(False)
        self.show_advanced_checkbox.toggled.connect(self.advanced_box.setVisible)
        layout.addWidget(self.advanced_box)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save Only")
        save_button.clicked.connect(lambda: self.save_configuration(apply=False))
        apply_button = QPushButton("Save and Apply")
        apply_button.setStyleSheet("font-weight:600; padding:6px 16px;")
        apply_button.clicked.connect(lambda: self.save_configuration(apply=True))
        buttons.addStretch(1)
        buttons.addWidget(save_button)
        buttons.addWidget(apply_button)
        layout.addLayout(buttons)
        self.config_status = QLabel("Configuration not loaded")
        self.config_status.setWordWrap(True)
        layout.addWidget(self.config_status)
        layout.addStretch(1)

    def _set_intrinsics_enabled(self, enabled: bool) -> None:
        for widget in (
            self.fx_spin,
            self.fy_spin,
            self.cx_spin,
            self.cy_spin,
            self.image_width_spin,
            self.image_height_spin,
        ):
            widget.setEnabled(enabled)

    def resolved_config_path(self) -> Path:
        path = Path(self.config_path_edit.text().strip()).expanduser()
        if not path.is_absolute():
            path = self.project_root / path
        return path.resolve()

    def browse_configuration(self) -> None:
        selected, _ = QFileDialog.getSaveFileName(
            self,
            "Select ArUco Measurement Configuration",
            str(self.resolved_config_path()),
            "JSON (*.json)",
        )
        if selected:
            self.config_path_edit.setText(selected)

    @staticmethod
    def _raw_spin_m(spin: QDoubleSpinBox) -> float | None:
        return None if spin.value() < 0.0 else spin.value() / 1000.0

    def current_config(self) -> TrackerConfig:
        marker_ids = tuple(
            int(value.strip())
            for value in self.marker_ids_edit.text().replace(";", ",").split(",")
            if value.strip()
        )
        if len(marker_ids) != 2:
            raise ValueError("Gripper measurement requires exactly two marker IDs")

        minimum_raw_m = self._raw_spin_m(self.minimum_raw_mm_spin)
        maximum_raw_m = self._raw_spin_m(self.maximum_raw_mm_spin)
        minimum_gap_m = self.minimum_gap_mm_spin.value() / 1000.0
        maximum_gap_m = self.maximum_gap_mm_spin.value() / 1000.0
        if minimum_raw_m is not None and maximum_raw_m is not None:
            self.distance_scale, self.distance_offset_m = calculate_distance_calibration(
                minimum_raw_m,
                minimum_gap_m,
                maximum_raw_m,
                maximum_gap_m,
            )
            self._refresh_calibration_result()

        fallback = None
        if self.manual_intrinsics_checkbox.isChecked():
            fallback = CameraIntrinsics(
                fx=self.fx_spin.value(),
                fy=self.fy_spin.value(),
                cx=self.cx_spin.value(),
                cy=self.cy_spin.value(),
                image_width=self.image_width_spin.value(),
                image_height=self.image_height_spin.value(),
            )
        distortion = np.asarray(
            [float(value.strip()) for value in self.distortion_edit.text().split(",") if value.strip()],
            dtype=np.float64,
        ).reshape(-1, 1)
        if distortion.size not in (4, 5, 8, 12, 14):
            raise ValueError("Enter 4, 5, 8, 12 or 14 distortion coefficients")

        config = TrackerConfig(
            dictionary_name=self.dictionary_combo.currentText().strip(),
            marker_size_m=self.marker_size_mm.value() / 1000.0,
            marker_ids=marker_ids,
            distortion_coefficients=distortion,
            fallback_intrinsics=fallback,
            max_reprojection_error_px=self.max_reprojection_spin.value(),
            min_marker_perimeter_px=self.min_perimeter_spin.value(),
            tracking_enabled=self.enabled_checkbox.isChecked(),
            output_host=self.output_host_edit.text().strip(),
            output_port=self.output_port_spin.value(),
            distance_scale=self.distance_scale,
            distance_offset_m=self.distance_offset_m,
            distance_smoothing_alpha=self.smoothing_alpha_spin.value(),
            distance_measurement_mode="camera_x",
            nominal_marker_depth_m=self.nominal_depth_mm_spin.value() / 1000.0,
            marker_depth_tolerance_m=self.depth_tolerance_mm_spin.value() / 1000.0,
            calibration_min_raw_m=minimum_raw_m,
            calibration_min_gap_m=minimum_gap_m,
            calibration_max_raw_m=maximum_raw_m,
            calibration_max_gap_m=maximum_gap_m,
            calibration_min_cycles=self.calibration_min_cycles_spin.value(),
        )
        if not config.output_host:
            raise ValueError("UDP receiver IP must not be empty")
        if config.tracking_enabled:
            ArucoEstimator(config)
        return config

    def set_config(self, config: TrackerConfig) -> None:
        self.enabled_checkbox.setChecked(config.tracking_enabled)
        self.dictionary_combo.setCurrentText(config.dictionary_name)
        self.marker_size_mm.setValue(config.marker_size_m * 1000.0)
        self.marker_ids_edit.setText(",".join(str(value) for value in config.marker_ids))
        self.output_host_edit.setText(config.output_host)
        self.output_port_spin.setValue(config.output_port)
        self.smoothing_alpha_spin.setValue(config.distance_smoothing_alpha)
        self.nominal_depth_mm_spin.setValue(config.nominal_marker_depth_m * 1000.0)
        self.depth_tolerance_mm_spin.setValue(config.marker_depth_tolerance_m * 1000.0)
        self.calibration_min_cycles_spin.setValue(config.calibration_min_cycles)
        self.distance_scale = config.distance_scale
        self.distance_offset_m = config.distance_offset_m
        self.minimum_gap_mm_spin.setValue(config.calibration_min_gap_m * 1000.0)
        self.maximum_gap_mm_spin.setValue(config.calibration_max_gap_m * 1000.0)
        self.minimum_raw_mm_spin.setValue(
            -1.0 if config.calibration_min_raw_m is None else config.calibration_min_raw_m * 1000.0
        )
        self.maximum_raw_mm_spin.setValue(
            -1.0 if config.calibration_max_raw_m is None else config.calibration_max_raw_m * 1000.0
        )
        fallback = config.fallback_intrinsics
        self.manual_intrinsics_checkbox.setChecked(fallback is not None)
        if fallback is not None:
            self.fx_spin.setValue(fallback.fx)
            self.fy_spin.setValue(fallback.fy)
            self.cx_spin.setValue(fallback.cx)
            self.cy_spin.setValue(fallback.cy)
            self.image_width_spin.setValue(fallback.image_width)
            self.image_height_spin.setValue(fallback.image_height)
        self.distortion_edit.setText(
            ",".join(f"{float(value):.9g}" for value in config.distortion_coefficients.reshape(-1))
        )
        self.max_reprojection_spin.setValue(config.max_reprojection_error_px)
        self.min_perimeter_spin.setValue(config.min_marker_perimeter_px)
        self._refresh_calibration_result()

    def _refresh_calibration_result(self) -> None:
        complete = (
            self._raw_spin_m(self.minimum_raw_mm_spin) is not None
            and self._raw_spin_m(self.maximum_raw_mm_spin) is not None
        )
        prefix = "Two-point calibration complete" if complete else "Two-point calibration incomplete"
        self.calibration_result_label.setText(
            f"{prefix} | scale={self.distance_scale:.8f} | offset={self.distance_offset_m * 1000.0:.4f} mm"
        )
        self.calibration_result_label.setStyleSheet(
            "padding:7px; border-radius:4px; "
            + ("background:#e8f5e9; color:#2e7d32;" if complete else "background:#fff8e1; color:#ef6c00;")
        )

    def load_configuration(self, _checked: bool = False, show_dialog: bool = True) -> None:
        try:
            path = self.resolved_config_path()
            self.set_config(TrackerConfig.load(path))
            self.config_status.setText(f"Loaded: {path}")
            self.config_status.setStyleSheet("color:#2e7d32;")
        except Exception as exc:
            self.config_status.setText(f"Failed to load: {exc}")
            self.config_status.setStyleSheet("color:#c62828;")
            if show_dialog:
                QMessageBox.critical(self, "ArUco Configuration Error", str(exc))

    def save_configuration(self, apply: bool) -> None:
        try:
            config = self.current_config()
            path = self.resolved_config_path()
            config.save(path)
            self.config_status.setText(f"Saved: {path}" + ("; applying configuration" if apply else ""))
            self.config_status.setStyleSheet("color:#2e7d32;")
            if apply:
                self.apply_requested.emit(config)
        except Exception as exc:
            self.config_status.setText(f"Failed to save: {exc}")
            self.config_status.setStyleSheet("color:#c62828;")
            QMessageBox.critical(self, "Cannot Save ArUco Configuration", str(exc))

    def use_current_marker_depth(self, _checked: bool = False) -> None:
        depths_mm = [
            value * 1000.0
            for value in self.last_marker_depths_m.values()
            if np.isfinite(value) and value > 0.0
        ]
        if len(depths_mm) < 2:
            QMessageBox.warning(
                self,
                "No Depth Available",
                "Make both markers visible in the 0.5× view, then click 'Use Current Depth and Apply'.",
            )
            return
        nominal_mm = float(np.median(depths_mm))
        maximum_deviation_mm = max(abs(value - nominal_mm) for value in depths_mm)
        tolerance_mm = max(20.0, maximum_deviation_mm + 10.0)
        self.nominal_depth_mm_spin.setValue(nominal_mm)
        self.depth_tolerance_mm_spin.setValue(tolerance_mm)
        self.quick_calibration_status_label.setText(
            f"Depth set to {nominal_mm:.1f} ± {tolerance_mm:.1f} mm; saving and applying."
        )
        self.quick_calibration_status_label.setStyleSheet("color:#2e7d32; font-weight:600;")
        self.save_configuration(apply=True)

    def _stable_recent_raw_point(self) -> tuple[float, int, float] | None:
        cutoff = time.monotonic() - 1.25
        values = np.asarray(
            [value for timestamp, value in self.recent_raw_samples if timestamp >= cutoff],
            dtype=np.float64,
        )
        if values.size < 4:
            QMessageBox.warning(
                self,
                "Not Enough Stable Frames",
                "Wait for 'Measuring each frame', hold the gripper still for about 1 second, then try again.",
            )
            return None
        point_m = float(np.median(values))
        spread_m = float(np.percentile(values, 90.0) - np.percentile(values, 10.0))
        if spread_m > 0.0015:
            QMessageBox.warning(
                self,
                "Gripper Still Moving",
                f"Recent measurements vary by about {spread_m * 1000.0:.2f} mm. Hold still for about 1 second and try again.",
            )
            return None
        return point_m, int(values.size), spread_m

    def capture_minimum_point(self, _checked: bool = False) -> None:
        self._capture_quick_point(self.minimum_raw_mm_spin, "minimum")

    def capture_maximum_point(self, _checked: bool = False) -> None:
        self._capture_quick_point(self.maximum_raw_mm_spin, "maximum")

    def _capture_quick_point(self, target: QDoubleSpinBox, label: str) -> None:
        stable = self._stable_recent_raw_point()
        if stable is None:
            return
        point_m, sample_count, spread_m = stable
        target.setValue(point_m * 1000.0)
        self.quick_calibration_status_label.setText(
            f"Captured {label}: {point_m * 1000.0:.3f} mm ({sample_count} frames, variation "
            f"{spread_m * 1000.0:.3f} mm)."
        )
        self.quick_calibration_status_label.setStyleSheet("color:#2e7d32; font-weight:600;")
        if (
            self._raw_spin_m(self.minimum_raw_mm_spin) is not None
            and self._raw_spin_m(self.maximum_raw_mm_spin) is not None
            and self.maximum_gap_mm_spin.value() > self.minimum_gap_mm_spin.value()
        ):
            self.calculate_two_point_calibration(show_dialog=False)

    def finish_quick_calibration(self, _checked: bool = False) -> None:
        if self.calculate_two_point_calibration(show_dialog=True):
            self.save_configuration(apply=True)

    def start_calibration_collection(self, _checked: bool = False) -> None:
        if self.maximum_gap_mm_spin.value() <= self.minimum_gap_mm_spin.value():
            QMessageBox.warning(self, "Invalid Opening", "The maximum actual opening must be greater than the minimum.")
            return
        self.calibration_samples_m.clear()
        self.calibration_collection_summary = None
        self.calibration_collecting = True
        self.start_collection_button.setEnabled(False)
        self.finish_collection_button.setEnabled(True)
        self.collection_status_label.setText(
            f"Recording: complete at least {self.calibration_min_cycles_spin.value()} cycles of fully closed → fully open → fully closed."
        )
        self.collection_status_label.setStyleSheet("color:#1565c0; font-weight:600;")

    def clear_calibration_collection(self, _checked: bool = False) -> None:
        self.calibration_collecting = False
        self.calibration_samples_m.clear()
        self.calibration_collection_summary = None
        self.start_collection_button.setEnabled(True)
        self.finish_collection_button.setEnabled(False)
        self.collection_status_label.setText("Recording cleared; saved calibration endpoints are unchanged")
        self.collection_status_label.setStyleSheet("color:#546e7a;")

    def _update_collection_summary(self) -> None:
        if len(self.calibration_samples_m) < 10:
            self.collection_status_label.setText(
                f"Recording: {len(self.calibration_samples_m)} valid frames; waiting for the full opening range"
            )
            return
        try:
            summary = summarize_cyclic_calibration(self.calibration_samples_m)
        except ValueError as exc:
            self.calibration_collection_summary = None
            self.collection_status_label.setText(
                f"Recording: {len(self.calibration_samples_m)} valid frames; {exc}"
            )
            return
        self.calibration_collection_summary = summary
        self.collection_status_label.setText(
            f"Recording: {summary.sample_count} frames, approximately {summary.cycle_count} complete cycles; "
            f"robust endpoints {summary.minimum_raw_m * 1000.0:.3f}–"
            f"{summary.maximum_raw_m * 1000.0:.3f} mm"
        )

    def finish_calibration_collection(self, _checked: bool = False) -> None:
        self._update_collection_summary()
        summary = self.calibration_collection_summary
        required_cycles = self.calibration_min_cycles_spin.value()
        if summary is None or summary.cycle_count < required_cycles:
            measured_cycles = 0 if summary is None else summary.cycle_count
            message = (
                f"Detected approximately {measured_cycles} complete cycles; at least {required_cycles} are required. "
                "Continue fully opening and closing the gripper, then click 'Finish and Calculate' again."
            )
            QMessageBox.warning(self, "Not Enough Calibration Cycles", message)
            self.collection_status_label.setText(message)
            self.collection_status_label.setStyleSheet("color:#ef6c00; font-weight:600;")
            return

        self.calibration_collecting = False
        self.start_collection_button.setEnabled(True)
        self.finish_collection_button.setEnabled(False)
        self.minimum_raw_mm_spin.setValue(summary.minimum_raw_m * 1000.0)
        self.maximum_raw_mm_spin.setValue(summary.maximum_raw_m * 1000.0)
        if not self.calculate_two_point_calibration(show_dialog=True):
            return
        self.collection_status_label.setText(
            f"Recording complete: {summary.sample_count} frames, {summary.cycle_count} complete cycles; "
            "robust minimum and maximum X widths have been filled in"
        )
        self.collection_status_label.setStyleSheet("color:#2e7d32; font-weight:600;")

    def calculate_two_point_calibration(
        self,
        _checked: bool = False,
        show_dialog: bool = True,
    ) -> bool:
        minimum_raw_m = self._raw_spin_m(self.minimum_raw_mm_spin)
        maximum_raw_m = self._raw_spin_m(self.maximum_raw_mm_spin)
        if minimum_raw_m is None or maximum_raw_m is None:
            message = "Click 'Capture Minimum' and 'Capture Maximum' first, or enter both raw X widths manually."
            if show_dialog:
                QMessageBox.warning(self, "Missing Calibration Points", message)
            self.config_status.setText(message)
            self.config_status.setStyleSheet("color:#ef6c00;")
            return False
        try:
            self.distance_scale, self.distance_offset_m = calculate_distance_calibration(
                minimum_raw_m,
                self.minimum_gap_mm_spin.value() / 1000.0,
                maximum_raw_m,
                self.maximum_gap_mm_spin.value() / 1000.0,
            )
        except ValueError as exc:
            if show_dialog:
                QMessageBox.warning(self, "Cannot Calculate Two-Point Calibration", str(exc))
            self.config_status.setText(f"Calibration failed: {exc}")
            self.config_status.setStyleSheet("color:#c62828;")
            return False
        self._refresh_calibration_result()
        self.config_status.setText("Two-point calibration calculated. Click 'Save and Apply' to use it for per-frame opening measurements.")
        self.config_status.setStyleSheet("color:#1565c0;")
        return True

    def update_live_result(self, result: dict) -> None:
        status = str(result.get("status", "--"))
        measurement = result.get("measurement") or {}
        depths = measurement.get("marker_depth_m") or {}
        self.last_marker_depths_m = {
            str(marker_id): float(value)
            for marker_id, value in depths.items()
            if isinstance(value, (int, float)) and np.isfinite(value) and value > 0.0
        }
        nominal_depth_m = measurement.get("nominal_marker_depth_m")
        depth_tolerance_m = measurement.get("marker_depth_tolerance_m")
        allowed_depth_text = ""
        if isinstance(nominal_depth_m, (int, float)) and isinstance(
            depth_tolerance_m, (int, float)
        ):
            minimum_depth_mm = (float(nominal_depth_m) - float(depth_tolerance_m)) * 1000.0
            maximum_depth_mm = (float(nominal_depth_m) + float(depth_tolerance_m)) * 1000.0
            allowed_depth_text = f"; allowed range: {minimum_depth_mm:.1f}–{maximum_depth_mm:.1f} mm"
        translations = {
            "tracking_gripper_distance": "Measuring each frame",
            "insufficient_markers_for_distance": "Both markers must be visible",
            "marker_depth_out_of_range": "Marker depth is outside the allowed range",
            "missing_intrinsics": "Camera intrinsics missing; use APV2",
            "no_markers": "Neither configured marker ID was detected",
            "processor_error": "Processing error",
        }
        status_detail = allowed_depth_text if status == "marker_depth_out_of_range" else ""
        self.live_status_label.setText(
            f"{translations.get(status, status)}{status_detail} ({status})"
        )
        color = "#2e7d32" if status == "tracking_gripper_distance" else "#ef6c00"
        if status in {"processor_error", "missing_intrinsics", "marker_depth_out_of_range"}:
            color = "#c62828"
        self.live_status_label.setStyleSheet(f"color:{color}; font-weight:600;")

        ids = result.get("detected_ids") or []
        errors = [
            marker.get("reprojection_error_px")
            for marker in (result.get("markers") or {}).values()
            if isinstance(marker, dict) and marker.get("reprojection_error_px") is not None
        ]
        error_text = f"{max(errors):.3f} px" if errors else "--"
        output_error = result.get("output_error")
        output_text = (
            f"Send error: {output_error}"
            if output_error
            else f"{self.output_host_edit.text().strip()}:{self.output_port_spin.value()}"
        )
        depth_text = ", ".join(
            f"ID {marker_id}={float(value) * 1000.0:.2f} mm"
            for marker_id, value in depths.items()
            if isinstance(value, (int, float))
        )
        self.live_detail_label.setText(
            f"Detected IDs: {', '.join(str(value) for value in ids) if ids else '--'} | "
            f"Depth: {depth_text or '--'}{allowed_depth_text} | Reprojection error: {error_text} | UDP: {output_text}"
        )

        distance = result.get("gripper_distance") or {}
        raw_m = distance.get("raw_marker_x_distance_m")
        if status == "tracking_gripper_distance" and isinstance(raw_m, (int, float)):
            self.last_raw_distance_m = float(raw_m)
            self.recent_raw_samples.append((time.monotonic(), self.last_raw_distance_m))
            self.current_raw_label.setText(f"{self.last_raw_distance_m * 1000.0:.4f} mm")
            if self.calibration_collecting:
                self.calibration_samples_m.append(self.last_raw_distance_m)
                self._update_collection_summary()
        else:
            self.last_raw_distance_m = None
            self.current_raw_label.setText("--")
        calibrated_mm = distance.get("calibrated_mm")
        filtered_mm = distance.get("filtered_mm")
        calibration_complete = distance.get("calibration_complete") is True
        self.current_gap_label.setText(
            f"{float(calibrated_mm):.4f} mm"
            if calibration_complete and isinstance(calibrated_mm, (int, float))
            else "Not calibrated"
            if distance
            else "--"
        )
        self.filtered_gap_label.setText(
            f"{float(filtered_mm):.4f} mm"
            if calibration_complete and isinstance(filtered_mm, (int, float))
            else "Not calibrated"
            if distance
            else "--"
        )
