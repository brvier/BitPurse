import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    tools: mainTools

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
        title: qsTr('Address')
        color: '#666666'
    }

    Column {
        id: addressInfo
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            leftMargin: 10
            rightMargin: 10}
        spacing: 5


        Item {
            anchors.right: parent.right
            anchors.left: parent.left
            height: Math.max(qrCode.height, label.height) + 10

            Label {
                id : label
                text : '<b>' + WalletController.currentLabel + '</b><br>' + WalletController.currentAddress
                wrapMode: Text.WrapAnywhere
                anchors.left: parent.left
                anchors.right: qrCode.left
                anchors.verticalCenter:  parent.verticalCenter
            }

            Image {
                id: qrCode
                source: WalletController.currentAddress ?
                            Qt.resolvedUrl('https://blockchain.info/qr?data='
                                           + WalletController.currentAddress
                                           + '&size=128') : undefined
                anchors.right: parent.right
                sourceSize.width: 128
                sourceSize.height: 128
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        BitCoinLabel {
            id: summary
            anchors {
                
                horizontalCenter: parent.horizontalCenter
            }
            text: WalletController.currentBalance
        }
    }

    Rectangle {
        anchors {
            top: addressInfo.bottom
            right: parent.right
            left: parent.left
            bottom: parent.bottom
            topMargin: 10
        }
        color:'white'
        border.color: 'grey'
        border.width: 1


        ListView {
            id:transactionsView
            clip: true
            model: TransactionsModel
            anchors.fill: parent
            anchors {
                leftMargin: 1
                rightMargin: 1
                bottomMargin: 1
                topMargin: 1
            }

            delegate: Component {
                id: transcationsDelegate
                Rectangle {
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    height: 80
                    color:"white"

                    Rectangle {
                        id: background
                        anchors.fill: parent
                        color: "darkgray";
                        opacity: 0.0
                        Behavior on opacity { NumberAnimation {} }
                    }

                    Column {
                        id:transactionInfos
                        spacing: 10
                        anchors {
                            left: parent.left
                            right: parent.right
                        }

                        Label {
                            anchors.right:parent.right
                            anchors.left:parent.left
                            text:address
                            font.family: "Nokia Pure Text"
                            font.pixelSize: 18
                            color:"black"
                        }

                        Label {
                            text:date + (confirmations < 100 ? ' - Unconfirmed' : '')
                            font.pixelSize: 16
                            color: "#666666"
                            anchors.right:parent.right
                            anchors.left:parent.left

                            Label {
                                id: transactionAmount
                                text: amount
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                color: confirmations < 100 ? 'red' : (amount > 0 ? 'green' : 'purple')
                            }
                        }

                    }




                    MouseArea {
                        anchors.fill: parent
                        onPressed: background.opacity = 1.0;
                        onReleased: background.opacity = 0.0;
                        onPositionChanged: background.opacity = 0.0;
                    }
                }
            }
        }

        ScrollDecorator {
            id: scrollDecorator
            flickableItem: transactionsView
            z:3
            platformStyle: ScrollDecoratorStyle {
            }
        }
    }
}

