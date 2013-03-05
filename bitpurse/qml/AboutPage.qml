import QtQuick 1.1
import com.nokia.meego 1.0

Page {

    tools: backTools

    function onTxSent(sent) {
        busyindicatorSending.running = false;
    }
    
    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
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
                text: qsTr('A nice looking Bitcoin Client for MeeGo.')
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

                BitCoinField {
                    id:donateField
                    text: '1.000000'
                    anchors.right: parent.right
                    anchors.left: parent.left
                }
            TextField {
                id:donatePassword
                placeholderText: qsTr('Second Password')
                echoMode: TextInput.Password
                opacity: WalletController.currentDoubleEncrypted ? 1.0 : 0.0
                visible: WalletController.currentDoubleEncrypted ? true : false
                anchors.right: parent.right
                anchors.left: parent.left
            }
                Button {
                    id: sendButton
                    width: 350; height: 50
                    text: qsTr("Donate")
                    onClicked: { WalletController.sendFromCurrent(
                        '1H1QjfoANoATk1yAsCHmqbPChmQtogPpvv',
                        donateField.text,
                        '0.0005',
                        donatePassword.text);
                    }
                    anchors.horizontalCenter: parent.horizontalCenter
                }

            BusyIndicator {
                id: busyindicatorSending
                platformStyle: BusyIndicatorStyle { size: "large"; spinnerFrames: "image://theme/spinner"}
                running: false;
                opacity: running ? 1.0 : 0.0;
                visible: running ? true : false;
                anchors.horizontalCenter: parent.horizontalCenter
            }            }

            Label {
                text: qsTr('By Benoit HERVIER<br>Licenced under GPLv3.<br>http://khertan.net/BitPurse')
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
                MouseArea {
                    anchors.fill: parent
                    onClicked:
                    {
                        Qt.openUrlExternally('https://github.com/khertan/BitPurse/issues/new');
                    }
                }
            }

            Label {
                text: qsTr('<b>No Blockchain</b> Download The app uses Blockchain.info api saving valuable space and bandwidth.<br><br>'
                           +'<b>Double Encryption</b> Your main wallet password will be saved on your phone however you can optionally set a second password required before you can make payments. This means even if your phone gets stolen your funds will still be safe!<br><br>'
                           +'<b>Secure</b> your private key is never transmitted to a third party services.<br><br>'
                           +'<b>100% Free and Open source</b> Use open source technology Python, PySide, Qt, PyCrypto, PyPackager, Git, Python ECDSA module, and Python PBKDF2 module . The source can be found on my github repository.')

                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
            }

            Label {
                text: '<b>Changelog</b><br>' + __upgrade__
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
            }


            Label {
                text: qsTr('<b>Privacy Policy</b><br>BitPurse connect to an remote third party api to avoid downloading the bitcoin blockchain.'
                           + '<br><br>Your Bitcoin private keys is never send'
                           + '<br><br>Which datas are stored :'
                           + '<br>* Your Private Keys, addresses with last know balances and tx (with encryptions)'
                           + '<br>* Your main encryption password (optionnal)')
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
            }
            Label {
                text: qsTr('<b>Blockchain.info Privacy Policy</b><br>Please see <a>https://blockchain.info/about</a>')
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
                MouseArea {
                    anchors.fill: parent
                    onClicked:
                    {
                        Qt.openUrlExternally('https://blockchain.info/about');
                    }
                }
            }
            
            Label {
                text: qsTr('<b>Thanks to</b><br>M4rtinK on #NemoMobile on freenode for the name suggestion')
                anchors {right: parent.right; left: parent.left}
                wrapMode: Text.WordWrap
            }
        }
    }
}   
