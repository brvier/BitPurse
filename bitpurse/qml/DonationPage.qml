import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: backTools
    
    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('About BitPurse')
        color: '#666666'
    }

    Flickable {
        anchors {
            top: header.bottom
            topMargin: 10
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        contentHeight: aboutContainer.height + 10

        Column {
            id: aboutContainer
            spacing: 20
            anchors {
                right: parent.right
                left: parent.left
                leftMargin: 10
                rightMargin: 10
                top: parent.top
            }

            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: Qt.resolvedUrl('bitcoin.svg')
            }

            Label {
                text: qsTr('<b>BitPurse</b>')
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 48
            }

            Label {
                text: __version__
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 24
            }
            Label {
                text: qsTr('You have use BitPurse for a few time now, show your support by making a small donation.')
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
            }

            Column {
                id: donateContainer
                spacing: 10
                anchors {
                    right: parent.right
                    left: parent.left
                    leftMargin: 10
                    rightMargin: 10
                }

                Button {
                    id: sendButton
                    width: 350; height: 50
                    text: qsTr("Donate")
                    onClicked: { /*WalletController.sendFromCurrent(
                        '1H1QjfoANoATk1yAsCHmqbPChmQtogPpvv',
                        donateField.text,
                        '0.0005',
                        donatePassword.text);*/
                        //pageStack.pop();
                        sendTo('1H1QjfoANoATk1yAsCHmqbPChmQtogPpvv', '0.01');
                    }
                    anchors.horizontalCenter: parent.horizontalCenter
                }

            /*BusyIndicator {
                id: busyindicatorSending
                platformStyle: BusyIndicatorStyle { size: "large"; spinnerFrames: "image://theme/spinner"}
                running: false;
                opacity: running ? 1.0 : 0.0;
                visible: running ? true : false;
                anchors.horizontalCenter: parent.horizontalCenter
            }  */          }
        }
    }
}       
