# 测试与兼容性

日期：2026-09-13。设备：MECHREVO WUJIE Series-T142-HPT-R，BIOS T142_HPTR_V12。

## 硬件与事件

| 项目 | 结果 |
| --- | --- |
| 当前内核 7.2.4-x64v3-xanmod1-1 | DKMS 构建、签名、安装、加载通过 |
| 7.2.4-arch1-2 | DKMS 构建、签名、安装通过；未启动该内核 |
| 6.18.51-1-lts | 0.1.1 模块构建通过；未启动该内核 |
| 6.18.50-x64v3-xanmod1-2-lts | 0.1.1 模块构建通过；未启动该内核 |
| Fn+X 性能模式 | 安静、均衡、性能三档提示通过实机测试 |
| 键盘背光 | 0、1、2、3 四档状态通过实机测试 |
| Caps Lock / Num Lock | 开关状态提示通过实机测试 |
| Fn 锁定、触控板开关 | 已实现，待实机测试 |
| 停止绑定服务 | 恢复原 redmi-wmi 事件驱动 |
| 重新启动绑定服务 | 恢复 OSD 事件设备；已有图形进程自动重新连接 |

## 显示与安装

- Plasma Wayland：layer-shell 悬浮显示已在本机运行。
- X11：在本机 XWayland 下完成初始化检查；离屏验证了 120×120 图标绘制和自动隐藏。独立 X11 桌面尚未实测。
- 系统通知：在 Plasma 通知服务中通过状态显示、替换和连续更新测试。
- GNOME、Sway、Hyprland：待实机测试。
- 图标绘制及 1500 ms 自动隐藏测试通过。
- 7 项自动测试通过，覆盖事件边界、锁定状态和通知更新。
- `DESTDIR` 隔离安装和卸载通过；systemd 单元语法检查通过。
- 本机系统绑定服务与用户服务已启用；尚未重启电脑验证启动全过程。

跨桌面通知使用 [freedesktop Desktop Notifications 接口](https://specifications.freedesktop.org/notification/latest-single/)。layer-shell 后端使用 [layer-shell-qt](https://github.com/KDE/layer-shell-qt)。实际位置、图标大小及通知策略以所在桌面实现为准。
