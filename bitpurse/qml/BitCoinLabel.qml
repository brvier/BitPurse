import QtQuick 1.1
import com.nokia.meego 1.0

Item {
  property alias text: label.text
  height: label.height
  width: label.width + bitcoinLogo.width + 20
  Text {
    id: label
    text : '<b>00.00</b>000000'
    font.pixelSize: 40
    height: paintedHeight
    width: paintedWidth
    anchors.verticalCenter: parent.verticalCenter
    }

    Image {
        id: bitcoinLogo
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: label.right
        anchors.leftMargin: 10
        sourceSize.width: 32
        sourceSize.height: 32
        source: Qt.resolvedUrl('bitcoin.svg')
        width: 32
        height: 32
    }

}
