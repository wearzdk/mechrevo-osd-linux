import QtQuick
import QtQuick.Window

Window {
    id: osd
    width: 120
    height: 120
    visible: false
    color: "transparent"
    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
           Qt.WindowDoesNotAcceptFocus | Qt.WindowTransparentForInput
    x: screen.virtualX + Math.round((screen.width - width) / 2)
    y: screen.virtualY + Math.round((screen.height - height) / 1.25)
    Image { id: icon; anchors.fill: parent; smooth: true; cache: true }
    Timer { id: hold; interval: 1500; onTriggered: osd.visible = false }
    function showResource(source) {
        hold.stop()
        icon.source = source
        osd.visible = true
        hold.start()
    }
}
