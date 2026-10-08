# 目录与模块导航

## 日常使用

从仓库根目录运行 `python arpose.py monitor`，即可打开实验监控、上传和回放窗口。
只查看位姿用 `python arpose.py visualizer`。
其他功能见[中文首页](../README.zh-CN.md)，参数见 `python arpose.py <工具名> --help`。

## 修改代码时从哪里看

| 功能 | iPhone：`ios/` | 电脑：`desktop/` |
| --- | --- | --- |
| App 入口和页面 | `ARPositionApp.swift`、`ContentView.swift`、`AppSettingsView.swift` | `experiment_replay_ui.py`、`udp_pose_visualizer.py` |
| ARKit 位姿与发送 | `PositionViewModel.swift`、`ARPoseUDPSender.swift` | `udp_pose_receiver.py` |
| 视频发送与接收 | `ARLowLatencyVideoSender.swift`、`ARUltraWideFrameAccess.swift` | `udp_video_debug_ui.py` |
| 双路磁传感器协议 | `MagneticSensorProtocol.swift`、`PoseMagneticPacket.swift`、`MagneticSensorHotspotGateway.swift` | `pose_magnetic_receiver.py` |
| 录制、历史记录、上传 | `ARSessionVideoRecorder.swift`、`PoseDataSessionRecorder.swift`、`CaptureLibraryStore.swift`、`CaptureUploadService.swift`、`CaptureHistoryView.swift` | `capture_upload_server.py`、`experiment_data.py` |
| ArUco 夹爪标定与离线处理 | — | `aruco_gripper_tracker.py`、`aruco_config_ui.py`、`offline_gripper_processor.py` |
| Zarr 数据导出 | — | `experiment_zarr.py`、`export_capture_to_zarr.py`、`zarr_exporter_ui.py` |
| AnySkin 调试 | — | `anyskin_serial_mapper.py`、`anyskin_udp_monitor.py`、`anyskin_hotspot_sender.py` |
| 轨迹验证与网络诊断 | — | `pose_tracking_validator.py`、`trajectory_aligner.py`、`udp_packet_loss_monitor.py` |

`desktop/` 中的脚本和共享模块保留原名称及相互导入方式，便于对照上游修改。
`runtime_paths.py` 统一源码与 EXE 的默认数据目录；配置仍在根目录 `config/`，实验仍在 `uploads/`。

## 开发约定

- 新的手机代码放入 `ios/`，同时更新根目录 `project.yml` 的 source 列表。
- 新的电脑功能放入 `desktop/`；需要用户直接启动的工具在 `arpose.py` 注册。
- 启动与打包脚本放入 `scripts/`，通过脚本自身位置定位仓库。
- 自动化测试放入 `tests/`，执行 `python -m unittest discover -s tests -t .`。
- `scripts/test_upload.py` 是需要上传服务器的手动检查，不参加自动化测试。
- 使用说明放入 `docs/`；中英文首页只保留入门步骤与导航。
- 原发布说明位于 `docs/releases/`；实验数据、构建产物和日志不提交到 Git。

## 整理范围

本次完成目录归类、统一启动入口、默认路径集中管理和文档导航，保留手机源码及数据格式。
原来的 `python xxx.py` 改为 `python desktop/xxx.py`，平台脚本改为 `scripts/` 下的同名文件。
轨迹对齐小工具原来写死了示例文件名，现在通过参数指定数据：

```powershell
python arpose.py align-trajectory --iphone-csv "uploads/实验/pose.csv" --robot-csv "机器人轨迹.csv"
```

从根目录执行 `xcodegen generate` 的方式保持一致；生成工程会引用 `ios/` 下的文件。

目录整理并未拆分所有大文件：实验回放界面、轨迹标定和 iPhone 状态管理仍包含较多逻辑。
进一步拆分应按接收、录制、数据处理和界面职责逐步进行，并配合对应的回归测试。
Windows 可以验证 Python 逻辑和配置路径，iPhone 构建仍需要在 Mac 上验证。
