import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    tools: walletTools

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
        title: qsTr('Wallet')
        color: '#666666'
    }

    ItemMenu {
        id: itemMenu
    }

    BitCoinLabel {
        id: summary
        anchors {
            top: header.bottom
            horizontalCenter: parent.horizontalCenter
        }
        text: WalletController.balance
    }

    ListModel {
        id: designModel
        ListElement {
            address:"NEEDTOBEFILLEDNEEDTOBEFILLED1234567890"
            label:'Label'
            balance: '0.000000'
        }
        ListElement {
            address:"NEEDTOBEFILLEDNEEDTOBEFILLED1234567890"
            label:'Label'
            balance: '0.000000'
        }
        ListElement {
            address:"NEEDTOBEFILLEDNEEDTOBEFILLED1234567890"
            label:'Label'
            balance: '0.000000'
        }
    }

    Rectangle {
        anchors {
            top: summary.bottom
            right: parent.right
            left: parent.left
            bottom: parent.bottom
            topMargin: 10
        }
        color:'white'
        border.color: 'grey'
        border.width: 1


        ListView {
            id: adressesView
            clip: true
            model: AddressesModel
            anchors.fill: parent
            anchors {
                leftMargin: 1
                rightMargin: 1
                bottomMargin: 1
                topMargin: 1
            }

            delegate: Component {
                id: adressesDelegate
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
                        id:addressInfos
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
                            text:label
                            font.pixelSize: 16
                            color: "#666666"
                            anchors.right:parent.right
                            anchors.left:parent.left

                            Label {
                                id: transactionAmount
                                text: prettyBalance
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                color: 'green'
                            }
                        }

                    }

                    MouseArea {
                        anchors.fill: parent
                        onPressed: background.opacity = 1.0;
                        onReleased: background.opacity = 0.0;
                        onPositionChanged: background.opacity = 0.0;
                        onClicked: {
                            console.log('Go to AddressPage :' + address)
                            WalletController.setCurrentAddress(address)
                            changePage(addressPage);
                            WalletController.update();
                        }
                        onPressAndHold: {
                            itemMenu.addr = model.address;
                            itemMenu.open();
                        }
                    }
                }
            }
        }

        ScrollDecorator {
            id: scrollDecorator
            flickableItem: adressesView
            z:3
            platformStyle: ScrollDecoratorStyle {
            }
        }
    }

    QueryDialog {
        
        property string addr

        id: deleteQueryDialog
        icon: Qt.resolvedUrl('bitcoin.svg')
        titleText: "Delete"
        message: "Are you sure you want to delete this address and his private key ?"
        acceptButtonText: qsTr("Delete")
        rejectButtonText: qsTr("Cancel")
        onAccepted: {
            WalletController.remove(addr);
        }
    }

    LabelDialog {
        
        property string addr

        id: editLabelDialog
        
        onAccepted: {
            WalletController.setLabelForAddr(addr, addrLabel);
        }
    }

}     
