import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    tools: backTools
    id: settingsPage

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
        title: qsTr('Preferences')
        color: '#666666'
    }


    Flickable {
        id: flick
        interactive: true
        anchors.top: header.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        contentWidth: parent.width
        contentHeight: settingsColumn.height + 30
        clip: true

        Column {
            id: settingsColumn
            spacing: 10
            width: parent.width - 40
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 20
            
            TitleLabel {
                text: qsTr("Security")
            }

            Label {
                text: qsTr("Save login")
                width: parent.width
                height: saveLoginSwitch.height
                verticalAlignment: Text.AlignVCenter
                Switch {
                    id: saveLoginSwitch
                    anchors.right: parent.right
                    checked: Settings.saveLogin
                    Binding {
                        target: Settings
                        property: "saveLogin"
                        value: saveLoginSwitch.checked
                    }
                }
            }
            Label {
                text: qsTr("Save password")
                width: parent.width
                height: savePasswordSwitch.height
                verticalAlignment: Text.AlignVCenter
                Switch {
                    id: savePasswordSwitch
                    anchors.right: parent.right
                    checked: Settings.savePassword
                    Binding {
                        target: Settings
                        property: "savePassword"
                        value: savePasswordSwitch.checked
                    }
                }
            }
        }
    }

    ScrollDecorator {
        flickableItem: flick
        platformStyle: ScrollDecoratorStyle {
        }}

}


