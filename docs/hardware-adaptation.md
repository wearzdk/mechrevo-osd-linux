# 机型适配指南

型号与已支持设备不同，也可以从接口检测开始尝试适配。本指南供 AI 编程助手和贡献者使用；最终支持情况由实机测试确定。

## 1. 识别设备与现有安装

读取发行版、内核、厂商、产品、主板和 BIOS 版本，记录桌面会话类型。营销名称相似的设备可能使用不同主板，匹配以实际 DMI 信息为准。

```sh
cat /etc/os-release
uname -r
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name /sys/class/dmi/id/board_name /sys/class/dmi/id/bios_version
ls /sys/bus/wmi/devices
```

检查当前绑定的 WMI 驱动及已有 OSD 安装。保存准备修改的配置、原驱动名称和 `driver_override`，在独立分支或源码副本中测试。

## 2. 判断接口是否相同

当前事件设备的 GUID 为 `46C93E13-EE9B-4262-8488-563BCA757FEF`。设备路径的尾号由系统枚举决定，应通过 GUID 查找。

```sh
for device in /sys/bus/wmi/devices/46C93E13-EE9B-4262-8488-563BCA757FEF-*; do
    [ -d "$device" ] || continue
    printf '%s\n' "$device"
    readlink "$device/driver"
    cat "$device/driver_override"
done
```

发现相同 GUID 后，先检查该设备事件格式和接管前的驱动。以本机准确的厂商、主板组合扩展 `driver/mechrevo-osd-wmi.c` 和 `packaging/bind-events.py` 的匹配，进行范围限定到本机的临时探测。

GUI 暂停时采集事件，先验证数据，再启用对应的显示映射。当前桥接器接收至少 8 字节的缓冲区，将前 8 字节通过 `MSC_SERIAL` 和 `MSC_RAW` 两个 32 位值传给用户进程，在 `SYN_REPORT` 处组成完整数据包。可对名为 `MECHREVO OSD firmware events` 的设备使用 `evtest` 记录，具体节点按设备名称查找。

如果 GUID 不同，继续检查设备已有的 Linux 驱动、接口文档和可观测事件，以确认候选接口与热键的对应关系。取得事件来源和载荷格式的证据后，再扩展桥接器。如果当前接口无法提供所需数据，报告缺少的证据以及需要用户配合的操作。

## 3. 对照实体按键与状态

请用户逐项操作，记录每次操作后的完整事件、设备状态和显示结果：

| 功能 | 建议测试 |
| --- | --- |
| 性能模式 | 遍历设备实际提供的模式，核对事件值与模式名称 |
| 键盘背光 | 从关闭到每个亮度档位，核对灯光和图标 |
| Fn 锁定 | 开启和关闭后分别测试功能键行为 |
| 触控板 | 开启和关闭后实际测试指针移动 |
| Caps Lock / Num Lock | 切换锁定状态，核对输入行为与图标 |

同一操作重复几次，确认映射稳定。记录电源状态、外接键盘等影响测试的条件；硬件本身没有的功能标记为“不适用”。

若数据与现有协议一致，复用 `events.py`。若存在差异，将解码规则关联到对应机型，并为新数据添加离线测试。已有机型的解码和测试应继续通过。

## 4. 验证安装与恢复

源码或本地包应包含本次修改，再按 [安装指南](installation.md) 安装到目标设备。先完成：

```sh
make test
mechrevo-osd --check --check-display
systemctl status mechrevo-osd-binding.service
journalctl -u mechrevo-osd-binding.service -b
```

检查图形进程的实际运行路径，确认当前加载模块与待测代码一致。记录目标内核构建、模块加载、按键测试、停止服务恢复原驱动和重新连接的结果。

启用适合该桌面的登录启动方式。重启、休眠恢复或其他桌面的测试若尚未执行，保留为待测项。测试出现异常时恢复此前保存的安装和绑定配置。

## 5. 将适配贡献回仓库

测试通过后更新支持机型与测试记录，按 [贡献指南](../CONTRIBUTING.md) 提交 PR。建议随 PR 提供：

- DMI 厂商、产品、主板和 BIOS 版本。
- 发行版、内核、桌面会话和显示后端。
- 必要的事件样例、对应状态、自动测试和实体按键结果。
- 安装、恢复、自启及尚未覆盖的测试情况。

贡献者可以让 Claude Code、Codex 等助手完成代码、测试整理和 PR 提交，让同型号的用户直接受益。
