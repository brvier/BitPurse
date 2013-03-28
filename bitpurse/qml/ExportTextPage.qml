import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: backTools
    property alias text: exported.text
    
    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Help')
        color: '#666666'
    }

    Flickable {
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        contentHeight: exported.height + 10

        TextArea {
                id: exported
                anchors {
                    right: parent.right
                    left: parent.left
                    top: parent.top
                }
                text: ''
        }
    }
}         
