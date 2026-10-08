# ARPoseStreamer

用 iPhone 采集 ARKit 位姿、视频和可选的双路磁传感器数据，在电脑上实时查看、接收上传、回放并导出 Zarr。

[English](README.md) · [详细使用说明](docs/USAGE.md) · [安装 iPhone App](docs/INSTALL_IPHONE_APP.md)

## 先运行起来

在仓库根目录打开终端，安装依赖：

```powershell
python -m pip install -r requirements_visualizer.txt
```

**实验采集、上传和回放，优先使用这个入口：**

```powershell
python arpose.py monitor --phone-ip 172.20.10.1
```

这里的地址是 iPhone 热点地址；普通局域网下改成手机实际 IP。手机 App 仍需要在 Mac 上通过 Xcode 构建和签名，见[安装说明](docs/INSTALL_IPHONE_APP.md)。

如果只看位姿轨迹：

```powershell
python arpose.py visualizer
```

在手机设置里将 Host IP 填为电脑 IP，位姿端口填 `5555`，然后开启 Streaming。实验采集使用 Start Experiment / Stop & Save Experiment。

macOS 将上面的 `python` 换成 `python3`。不要同时启动多个监听同一端口的工具。

## 按任务找入口

所有入口都通过 `python arpose.py <工具>` 启动，原有参数继续可用：

| 任务 | 工具名 |
| --- | --- |
| 实验实时监控、上传、同步回放 | `monitor` |
| 3D 位姿轨迹 | `visualizer` |
| 命令行接收位姿 | `receiver` |
| 仅启动上传服务器 | `upload-server` |
| 接收位姿和双路磁传感器 | `magnetic-receiver` |
| 视频诊断 / 丢包监测 | `video-debugger` / `packet-loss` |
| 离线轨迹验证 | `validator` |
| 导出 Zarr | `zarr-exporter` / `export-zarr` |
| AnySkin 串口映射 / UDP 监控 | `anyskin-serial` / `anyskin-monitor` |
| ArUco 夹爪跟踪 | `aruco-tracker` |

```powershell
python arpose.py --help
python arpose.py monitor --help
python arpose.py receiver --host 0.0.0.0 --port 5555 --encoding binary
```

## 目录怎么读

```text
ARPoseStreamer/
├── arpose.py                   # 电脑端统一启动入口
├── project.yml                 # XcodeGen 配置（从根目录运行）
├── requirements_visualizer.txt # 电脑端依赖
├── ios/                        # iPhone Swift 源码、Info.plist、图标
├── desktop/                    # 电脑端工具及共享模块
├── config/                     # ArUco 与相机标定配置
├── scripts/                    # Windows/macOS 启动与打包脚本
├── tests/                      # 自动化测试
└── docs/                       # 安装、协议、标定和使用说明
```

初次使用只需看本页；修改手机端看 `ios/`，修改电脑端看 `desktop/`。[目录与模块导航](docs/REPOSITORY_LAYOUT.zh-CN.md)列出了各功能对应的文件。

实验数据仍保存在 `uploads/`，独立 EXE 保存到它旁边的 `uploads/`。`build/`、`dist/`、日志和 Zarr 文件是本地输出，不属于源码；已有数据不会因目录整理被搬迁。

## 开发与打包

```powershell
# Windows 打包
.\scripts\build_windows.ps1

# 自动化测试（从仓库根目录运行）
python -m unittest discover -s tests -t .
```

```bash
# macOS 打包
./scripts/build_macos.sh

# 在 Mac 上生成 iPhone 工程
xcodegen generate
```

旧启动脚本移到了 `scripts/`，例如 `.\scripts\run_experiment_monitor_windows.ps1`。旧的 `python xxx.py` 命令改为 `python desktop/xxx.py`，也可以使用上面的统一入口。

## 进一步阅读

- [安装与连接](docs/SETUP.md)
- [iPhone 构建与签名](docs/INSTALL_IPHONE_APP.md)
- [架构](docs/ARCHITECTURE.md)与[通信协议](docs/PROTOCOL.md)
- [双路磁传感器采集](docs/HOTSPOT_MAGNETIC_CAPTURE.zh-CN.md)
- [ArUco 夹爪集成](docs/ARUCO_GRIPPER_INTEGRATION.zh-CN.md)
- [Zarr 导出](docs/ZARR_EXPORT.md)与[离线标定](docs/CALIBRATION_OVERVIEW.zh-CN.md)
- [独立可执行文件打包](docs/BUILD.md)

MIT License。
