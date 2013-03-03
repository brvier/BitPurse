import QtQuick 1.1
import com.nokia.meego 1.0
import QtWebKit 1.0

Page {

    tools: backTools
    
    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
        title: qsTr('Tutorial')
        color: '#666666'
    }

    Flickable {
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        //contentHeight: tutorial.height + 10
	//contentWidth: tutorial.width

        WebView {
            id: tutorial
            anchors {
                right: parent.right
                left: parent.left
                leftMargin: 10
                rightMargin: 10
                top: parent.top
	    }
	    settings.autoLoadImages: true
	    settings.defaultFontSize : 18
	    html: '<p>Bitcoin is an experimental, decentralized digital currency that enables instant payments to anyone, anywhere in the world. Bitcoin uses peer-to-peer technology to operate with no central authority: managing transactions and issuing money are carried out collectively by the network.</p>
<p>The original Bitcoin software by Satoshi Nakamoto was released under the MIT license. Most client software, derived or "from scratch", also use open source licensing.</p>
<p>Bitcoin is one of the first implementations of a concept called crypto-currency which was first described in 1998 by Wei Dai on the cypherpunks mailing list. Building upon the notion that money is any object, or any sort of record, accepted as payment for goods and services and repayment of debts in a given country or socio-economic context, Bitcoin is designed around the idea of using cryptography to control the creation and transfer of money, rather than relying on central authorities. (Sourced from en.bitcoin.it Wiki, Bitcoin.org and Wikipedia.)</p>

<p>BitPurse is a light bitcoin client which rely on a third party to avoid to download blockchain via P2P</p>

<p>By default BitPurse encrypt your wallet with a main storage key, you can optionnaly choose to store in preference that key to avoid entering it each time you launch BitPurse, for more security, you can choose also to double encrypt your private key, and you ll be invited to enter the double encryption password only when spending bitcoin.
<img src="tutorial/settings.png" width=400px></p>'



    	}
    }
}   
