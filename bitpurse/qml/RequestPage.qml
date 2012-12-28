import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: mainTools

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
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
                text : 'Label\nNEEDTOBEFILLEDNEEDTOBEFILLED1234567890'
                wrapMode: Text.WrapAnywhere
                anchors.left: parent.left
                anchors.right: parent.right

            }

            BitCoinLabel {
                id: summary
                anchors.horizontalCenter: parent.horizontalCenter
                text: '<b>0.00</b>000000'
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

            Label {
                text: qsTr('<b>Address request to</b>')
            }

            TextField {
                id:addressField
                placeholderText: qsTr('Type BitCoin address')
                anchors.right: parent.right
                anchors.left: parent.left
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
                onClicked: { busyindicatorRequest.running = true; }
                anchors.right: parent.right
                anchors.left: parent.left
                visible: busyindicatorRequest.running ? false : true;
                opacity: busyindicatorRequest.running ? 0.0 : 1.0;
            }

            BusyIndicator {
                id: busyindicatorRequest
                platformStyle: BusyIndicatorStyle { size: "large"; spinnerFrames: "image://theme/spinner"}
                running: false;
                opacity: running ? 1.0 : 0.0;
                visible: running ? true : false;
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}
