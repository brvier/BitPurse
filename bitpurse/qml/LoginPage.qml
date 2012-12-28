import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: simpleTools

   function onConnected(connected) {
        if (connected)
            pageStack.replace(addressesPage);
        busyindicatorLogin.running = false;
    }

    Flickable {
        contentHeight: container.height + 10
        anchors.fill: parent
        /*anchors {
            right: parent.right
            left: parent.left
            verticalCenter: parent.verticalCenter
        }*/

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
            source: Qt.resolvedUrl('bitcoin.svg')
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
        TextField {
            id:loginField
            placeholderText: qsTr('Login')
            text:Settings.saveLogin ? Settings.login : ''
            anchors.right: parent.right
            anchors.left: parent.left
        }

        TextField {
            id:passwordField
            placeholderText: qsTr('Password')
            echoMode: TextInput.PasswordEchoOnEdit
            anchors.right: parent.right
            anchors.left: parent.left
            text: Settings.savePassword ? Settings.password : ''
        }

        Button {
            id: loginButton
            width: 350; height: 50
            text: qsTr("Sign in")
            onClicked: { 
                busyindicatorLogin.running = true;
                WalletController.getData(loginField.text, passwordField.text);
                if (Settings.saveLogin) {
                    Settings.login = loginField.text;
                }
                if (Settings.savePassword) {
                    Settings.password = passwordField.text;
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
