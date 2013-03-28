import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: backTools
    
    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Help')
        color: '#666666'
    }

    Flickable {
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        contentHeight: tutorial.height + 10

        Column {
                id: tutorial
                anchors {
                    right: parent.right
                    left: parent.left
                    leftMargin: 10
                    rightMargin: 10
                    top: parent.top
                }
                spacing: 20

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }

                id: intro
    	        text: '<b>About Bitcoin</b><p>Bitcoin is an experimental, decentralized digital currency that enables instant payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer technology to operate with no central authority: managing transactions and issuing money are carried out collectively by the network.</p>
    <p>The original Bitcoin software by Satoshi Nakamoto was released under the MIT license. Most client software, derived or "from scratch", also use open source licensing.</p>
    <p>Bitcoin is one of the first implementations of a concept called crypto-currency which was first described in 1998 by Wei Dai on the cypherpunks mailing list. Building upon the notion that money is any object, or any sort of record, accepted as payment for goods and services and repayment of debts in a given country or socio-economic context, Bitcoin is designed around the idea of using cryptography to control the creation and transfer of money, rather than relying on central authorities. (Sourced from en.bitcoin.it Wiki, Bitcoin.org and Wikipedia.)</p>

    <p><b>BitPurse</b> is a light bitcoin client which rely on a third party to avoid to download blockchain via P2P</p>'
        	}

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<b>First Launch</b><br>The first time you launch BitPurse, it ll ask you to set a main password, this password is used to encrypt your BitCoin wallet (a purse that contain many bitcoin addresses)'
            }

            Image {
                source: Qt.resolvedUrl('tutorial/welcome.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }


            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<p>By default BitPurse encrypt your wallet with a main storage key, you can optionnaly choose to store in settings that key to avoid entering it each time you launch BitPurse, for more security, you can choose also to double encrypt your private key, and you ll be invited to enter the double encryption password only when spending bitcoin.</p><p>BitPurse can import your private key address manually by putting the address key in the import text field or can import them from BlockChain.info MyWallet. BitPurse wallet and configuration is backup and restored by the Harmattan Backup Framework, but i also suggest to export from time to time your wallet to backup it, that the purpose of the export feature (the wallet will be exported encrypted for more security).</p>'
            }

            Image {
                source: Qt.resolvedUrl('tutorial/settings.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<b>The wallet</b><br> page list all your addresses and the balance of all your BitCoin addresses. The add toolbar button create a new BitCoin address, the balance is refreshing automatically at regular interval when new transaction income in your wallet'
            }

            Image {
                source: Qt.resolvedUrl('tutorial/wallet.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<b>Contextual Menu</b><br>A contextual menu is available when doing a long press on a BitCoin address. This menu permit to edit label, delete an address, or copy the bitcoin address'
            }

            Image {
                source: Qt.resolvedUrl('tutorial/contextmenu.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<b>The address</b><br> page list all give more information about a wallet, and give you the list of transactions associated with that address, a color code is used for the transaction value, purple for outgoing transaction, red for unconfirmed transaction, and green for incoming transaction. The up arrow allow you to spend money from that address.'
            }


            Image {
                source: Qt.resolvedUrl('tutorial/address.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Label {
                anchors {
                    right: parent.right
                    left: parent.left
                }
                text: '<b>The send</b><br> page enable you to emit a transaction to an specified address, with the desired amount and fees. While you can emit a transaction which have a higher value than 0.01 BTC with 0 fee, you re transaction could be not processed by miners and so can in some case never been included in the blockchain (after some days the fund will be available again to be spend.). If you choose to use double encryption, you second password will be required to emit the transaction'
            }

            Image {
                source: Qt.resolvedUrl('tutorial/send.png')
                width: 240
                height: 424
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

    }
}   
