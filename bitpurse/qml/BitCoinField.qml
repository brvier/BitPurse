import QtQuick 1.1
import com.nokia.meego 1.0

TextField {
    placeholderText: qsTr('0.00')
    validator: DoubleValidator{ bottom: 0; decimals: 8; notation:DoubleValidator.StandardNotation }
    errorHighlight: !acceptableInput
    Image {
        anchors.verticalCenter: parent.verticalCenter
        sourceSize.width: 24
        sourceSize.height: 24
        anchors.rightMargin: 10
        anchors.right: parent.right
        source: Qt.resolvedUrl('bitcoin.svg')
    }
}
