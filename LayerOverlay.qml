import QtQuick
import org.kde.layershell as LayerShell

Overlay {
    LayerShell.Window.layer: LayerShell.Window.LayerOverlay
    LayerShell.Window.anchors: LayerShell.Window.AnchorTop
    LayerShell.Window.exclusionZone: -1
    LayerShell.Window.keyboardInteractivity: LayerShell.Window.KeyboardInteractivityNone
    LayerShell.Window.activateOnShow: false
    LayerShell.Window.scope: "mechrevo-osd"
    LayerShell.Window.margins.top: Math.round((screen.height - height) / 1.25)
}
