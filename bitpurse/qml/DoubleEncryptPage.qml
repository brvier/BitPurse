import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: decryptPKTools


    ToolBarLayout {
        id: decryptPKTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-back"
            onClicked: {pageStack.pop();Settings.useDoubleEncryption = false;}
        }
    }

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
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
                text: 'Enter a second password to encrypt and protect your private key to be used (During this operation, application could not respond during few minutes)'
                width: parent.width
                wrapMode: Text.Wrap
            }

            Label {
                id: invalidPasswordMessage
                color: 'red'
                text: 'Password you enter aren t the same'
                visible: false
            }

            TextField {
                id:passKeyField
                placeholderText: qsTr('Password')
                echoMode: TextInput.Password
                anchors.right: parent.right
                anchors.left: parent.left
            }

            TextField {
                id:verifyPassKeyField
                placeholderText: qsTr('Repeat Password')
                echoMode: TextInput.Password
                anchors.right: parent.right
                anchors.left: parent.left
            }

            Button {
                id: createButton
                width: 350; height: 50
                text: qsTr("Encrypt")
                onClicked: {
                    if (passKeyField.text != verifyPassKeyField.text) {
                        invalidPasswordMessage.visible = true;
                    }
                    else {
                        busyindicatorLogin.running = true;
                        WalletController.doubleEncrypt(passKeyField.text);
                        busyindicatorLogin.running = false;
                        pageStack.pop();
                    }
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
