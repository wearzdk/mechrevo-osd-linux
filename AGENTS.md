# AI 工作指引

适用于帮助用户安装、排查或适配 MECHREVO OSD 的编程助手。`CLAUDE.md` 引用本文件，两者共用此处的规则。

## 开始工作

1. 阅读 [README](README.md) 和 [测试与兼容性](docs/validation.md)，检查工作区现有修改。
2. 确认命令运行在用户要安装 OSD 的 Linux 设备上，收集发行版、内核、DMI 型号、桌面会话和安装来源。
3. 已支持机型按 README 安装；型号不同则阅读 [机型适配指南](docs/hardware-adaptation.md)，继续检查接口和协议。
4. 用户要求安装时，完成所需的依赖安装、服务配置和验证。沿用本次会话已有授权，实体按键操作请用户配合。
5. 缺少管理员权限、设备访问或账号权限时，说明具体阻碍和用户需要完成的步骤；账号登录、注册由用户处理。

建议先读取：

```sh
cat /etc/os-release
uname -r
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name /sys/class/dmi/id/board_name /sys/class/dmi/id/bios_version
printf '%s\n' "$XDG_SESSION_TYPE" "$XDG_CURRENT_DESKTOP"
type -a mechrevo-osd
dkms status
```

命令不存在、设备节点不存在或尚未安装服务，也属于检测结果；据此选择下一步。

## 安装决策

- Arch Linux 上，已有机型支持优先使用 AUR 的 `mechrevo-osd-linux`，驱动由 `mechrevo-osd-dkms` 提供。其他发行版或本地适配使用源码安装。
- 修改过的本地代码按源码或本地包验证；已发布 AUR 包不包含尚未合入的修改。
- 依赖使用发行版包管理器查询和安装。当前运行环境使用系统 Python、PySide6、Qt Quick 和 dbus-python；`pyproject.toml` 的空依赖列表不是完整的系统依赖清单。
- 核对当前内核及所有已安装内核的头文件，读取 `driver/dkms.conf` 确认模块版本。AUR 由 pacman 的 DKMS 钩子处理模块，源码安装按 README 手动注册。
- 区分 `/usr` 的包管理器安装和 `/usr/local` 的源码安装。迁移前保存旧配置，停止旧进程，清理旧启动入口对新版本的覆盖。
- 按会话能力选择 `auto`、`layer-shell`、`x11` 或 `notifications`。图形进程运行在桌面用户会话中，管理员权限用于模块和系统服务。
- XDG Autostart、窗口管理器启动命令和用户服务选择一种。使用用户服务前确认桌面管理 `graphical-session.target` 且用户服务具有当前显示会话环境。
- 临时源码副本、构建目录、日志和一次性输出放在 `/tmp` 下的独立目录；保留原工作区和用户已有配置。

## 代码导航

| 路径 | 职责 |
| --- | --- |
| `driver/mechrevo-osd-wmi.c` | 机型匹配、WMI 事件接收、输入设备数据传递 |
| `packaging/bind-events.py` | 事件设备绑定与原驱动恢复；包含机型检查 |
| `events.py` | 事件数据解码和图标映射 |
| `mechrevo_osd.py` | 设备发现、数据读取、系统锁定状态、程序入口 |
| `display.py`、`Overlay.qml`、`LayerOverlay.qml` | 显示后端与窗口 |
| `packaging/`、`Makefile`、`driver/dkms.conf` | 安装、启动、权限与模块构建 |
| `tests/` | 事件与通知更新测试 |

添加机型时同时检查内核模块和绑定脚本中的匹配条件。以设备事件及系统状态为解码依据，将机型差异限定到对应设备，保留已有机型行为。内核改动需兼顾 6.18 LTS 与 7.2 的 WMI 接口。

## 验证与交付

- 文档修改检查链接、命令和入口文件即可。Python 行为修改运行 `make test`；内核修改用目标设备的头文件构建，并记录所覆盖内核。
- 安装后运行 `mechrevo-osd --check --check-display`，检查系统绑定服务、实际图形进程和日志，再请用户测试对应实体按键。
- `--check` 证明设备和图标可读取，`--check-display` 证明后端可初始化；实体按键测试用于确认事件、图标与实际状态一致。
- 涉及绑定逻辑时，验证停止服务恢复原驱动、重新启动后重连。修改启动方式时检查实际启用的入口；重启或休眠测试由用户安排合适时机。
- 总结版本、安装来源、启动方式、已通过和待完成的测试，以及更新/卸载路径。区分编译通过、模块加载、状态事件和用户确认。
- 用户要求贡献时，按 [贡献指南](CONTRIBUTING.md) 整理分支、测试证据和 PR；仅安装的请求不自动授权发布代码。

公开说明面向使用者介绍功能、兼容性和操作步骤。提交内容聚焦项目改动与必要测试数据，保留资源的归属说明，移除个人路径、设备序列号和账号信息。
