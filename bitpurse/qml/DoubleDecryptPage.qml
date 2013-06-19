import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: encryptPKTools

    ToolBarLayout {
        id: encryptPKTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-back"
            onClicked: {Settings.useDoubleEncryption = true;pageStack.pop();}
        }
    }

    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Double encryption')
        color: '#666666'
    }

    Flickable {
        contentHeight: container.height + 10
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom

        Column {
            id: container
            spacing: 10
            anchors {
                right: parent.right
                left: parent.left
                leftMargin: 10
                rightMargin: 10
                verticalCenter: parent.verticalCenter
            }

            Label {
                text: 'Enter your second password to decrypt your private keys (During this operation, application could not respond during few minutes)'
                width: parent.width
                wrapMode: Text.Wrap
            }

            TextField {
                id:passKeyField
                placeholderText: qsTr('Password')
                echoMode: TextInput.Password
                anchors.right: parent.right
                anchors.left: parent.left
            }

            Button {
                id: createButton
                width: 350; height: 50
                text: qsTr("Decrypt")
                onClicked: {
                    busyindicatorLogin.running = true;
                    WalletController.doubleDecrypt(passKeyField.text);
                    busyindicatorLogin.running = false;
                    pageStack.pop();
                }
                anchors.right: parent.right
                anchors.left: parent.left
                visible: busyindicatorLogin.running ? false : true;
                opacity: busyindicatorLogin.running ? 0.0 : 1.0;
            }

            BusyIndicator {
                id: busyindicatorLogin
                platformStyle: BusyIndicatorStyle { size: "large"; spinnerFrames: "image://theme/spinner"}
                running: false;
                opacity: running ? 1.0 : 0.0
                visible: running ? true : false
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

} 