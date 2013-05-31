import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: simpleBackTools

    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Request Bitcoins')
        color: '#666666'
    }

    Flickable {
        anchors {
            top: header.bottom
            bottom: parent.bottom
            left: parent.left
            right: parent.right
        }
        contentHeight: container.height + 10
        //contentWidth: container.width

        Column {
            id:container
            spacing: 20
            anchors {
                right: parent.right
                left: parent.left
                leftMargin: 10
                rightMargin: 10
                verticalCenter: parent.verticalCenter
            }

            Label {
                text: qsTr('<b>From address</b>')
            }

            Label {
                id : label
                text : '<b>' + WalletController.currentLabel + '</b><br>' + WalletController.currentAddress
                wrapMode: Text.WrapAnywhere
                anchors.left: parent.left
                anchors.right: parent.right

            }

            Image {
                id: qrCode
                source: WalletController.currentAddress ?
                            Qt.resolvedUrl('https://blockchain.info/qr?data='
                                           + WalletController.currentAddress
                                           + '&size=384') : undefined
                width: 384
                height: 384

                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                text: qsTr('<b>Requested amount (optional)</b>')
            }

            BitCoinField {
                id:amountField
                anchors.right: parent.right
                anchors.left: parent.left
                text: '0.00'
            }


            /*        Label {
            text: qsTr('Label')
        }


        TextArea {
            id:labelField
            placeholderText: qsTr('Label')
            anchors.right: parent.right
            anchors.left: parent.left
        }*/

            Button {
                id: requestButton
                width: 350; height: 50
                text: qsTr("Request")
                onClicked: { WalletController.requestFromCurrent( amountField.text ); }
                anchors.right: parent.right
                anchors.left: parent.left
            }
        }
    }
}    