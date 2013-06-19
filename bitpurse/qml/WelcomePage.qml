import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: simpleTools

    Flickable {
        contentHeight: container.height + 10
        anchors.fill: parent

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

            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: Qt.resolvedUrl('bitpurse.svg')
            }

            Label {
                text: qsTr('<b>BitPurse</b>')
                font.pixelSize: 48
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Label {
                text: __version__
                font.pixelSize: 24
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                text: 'Welcome to BitPurse, to encrypt and protect your bitcoins, please enter a pass phrase to encrypt your wallet'
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
                text: qsTr("Create your wallet")
                onClicked: {
                    if (passKeyField.text != verifyPassKeyField.text) {
                        invalidPasswordMessage.visible = true;
                    }
                    else {
                        busyindicatorLogin.running = true;
                        WalletController.createWallet(passKeyField.text);
                        busyindicatorLogin.running = false;
                        pageStack.replace(Qt.createComponent(Qt.resolvedUrl("WalletPage.qml")))
                    }
                }
                anchors.right: parent.right
                anchors.left: parent.left
                visible: busyindicatorLogin.running ? false : true;
                opacity: busyindicatorLogin.running ? 0.0 : 1.0;
            }

            Button {
                id: helpButton
                width: 350; height: 50
                text: qsTr("See Help")
                onClicked: {
                        pageStack.push(Qt.createComponent(Qt.resolvedUrl("HelpPage.qml")))
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
