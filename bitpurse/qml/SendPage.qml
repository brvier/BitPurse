import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: simpleBackTools
    property alias sendTo: addressField.text
    property alias amount: amountField.text

    function onTxSent(sent) {
        if (sent) {
            amountField.text = '0.00';
            secondPasswordField.text = ''; }
        busyindicatorSending.running = false;
    }

    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Send Bitcoins')
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


            BitCoinLabel {
                id: summary
                anchors.horizontalCenter: parent.horizontalCenter
                text: WalletController.currentBalance
                subtext: WalletController.currentFiatBalance
            }

            Label {
                text: qsTr('<b>Pay to</b>')
            }

            TextField {
                id:addressField
                placeholderText: qsTr('Type BitCoin address')
                anchors.right: parent.right
                anchors.left: parent.left
                onTextChanged: {
                    console.log('test');
                    console.log(addressField.text.substring(0, 8));
                    if (addressField.text.substring(0, 8) == 'bitcoin:') {
                        addressField.text = addressField.text.substring(9);
                    } else if (addressField.text.substring(0, 10) == 'bitcoin://') {
                        addressField.text = addressField.text.substring(11);
                    }
                }
            }

            Label {
                text: qsTr('<b>Amout to pay</b>')
            }

            BitCoinField {
                id:amountField
                anchors.right: parent.right
                anchors.left: parent.left
            }

            Label {
                text: qsTr('<b>Fee</b>')
            }

            BitCoinField {
                id:feeField
                anchors.right: parent.right
                anchors.left: parent.left
                text: '0.0005'
            }

            Label {
                opacity: WalletController.currentDoubleEncrypted ? 1.0 : 0.0
                visible: WalletController.currentDoubleEncrypted ? true : false
                text: qsTr('<b>Second Password</b>')
            }

            TextField {
                id:secondPasswordField
                echoMode: TextInput.Password
                opacity: WalletController.currentDoubleEncrypted ? 1.0 : 0.0
                visible: WalletController.currentDoubleEncrypted ? true : false
                anchors.right: parent.right
                anchors.left: parent.left
            }

            Button {
                id: sendButton
                width: 350; height: 50
                text: qsTr("Send")
                anchors.right: parent.right
                anchors.left: parent.left
                visible: busyindicatorSending.running ? false : true;
                opacity: busyindicatorSending.running ? 0.0 : 1.0;
                onClicked: {
                    busyindicatorSending.running = true;
                    WalletController.sendFromCurrent(addressField.text,
                                                     amountField.text,
                                                     feeField.text,
                                                     secondPasswordField.text);
                }
            }

            BusyIndicator {
                id: busyindicatorSending
                platformStyle: BusyIndicatorStyle { size: "large"; spinnerFrames: "image://theme/spinner"}
                running: false;
                opacity: running ? 1.0 : 0.0;
                visible: running ? true : false;
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}   
