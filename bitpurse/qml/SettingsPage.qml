import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    tools: backTools
    id: settingsPage

    Header{
        id:header
        source: Qt.resolvedUrl('bitcoin.svg')
        title: qsTr('Preferences')
        color: '#666666'
    }


    Flickable {
        id: flick
        interactive: true
        anchors.top: header.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        contentWidth: parent.width
        contentHeight: settingsColumn.height + 30
        clip: true

        Column {
            id: settingsColumn
            spacing: 10
            width: parent.width - 40
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 20
            
            TitleLabel {
                text: qsTr("Security")
            }

            Label {
                text: qsTr("Store wallet key")
                width: parent.width
                height: storePassKeySwitch.height
                verticalAlignment: Text.AlignVCenter
                Switch {
                    id: storePassKeySwitch
                    anchors.right: parent.right
                    checked: Settings.storePassKey
                    Binding {
                        target: Settings
                        property: "storePassKey"
                        value: storePassKeySwitch.checked
                    }
                }
            }
            Label {
                text: qsTr("Use double encryption")
                width: parent.width
                height: useDoubleEncryptionSwitch.height
                verticalAlignment: Text.AlignVCenter
                Switch {
                    id: useDoubleEncryptionSwitch
                    anchors.right: parent.right
                    checked: Settings.useDoubleEncryption
                    Binding {
                        target: Settings
                        property: "useDoubleEncryption"
                        value: useDoubleEncryptionSwitch.checked
                    }
                }
            }
            
            TitleLabel {
                text: qsTr("Blockchain.info MyWallet")
            }
            
            TextField {
                id: blockchainGuid
                placeholderText: qsTr("GUID")
                width: parent.width
            }
            TextField {
                id: blockchainKey
                placeholderText: qsTr("Main Key")
                echoMode: TextInput.Password
                width: parent.width
            }
            TextField {
                id: blockchainSecondKey
                placeholderText: qsTr("Second Key")
                echoMode: TextInput.Password
                width: parent.width
            }
            Button {
                text: qsTr('Import')
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    WalletController.importFromBlockchainInfoWallet(
                                blockchainGuid.text,
                                blockchainKey.text,
                                blockchainSecondKey.text);
                }
            }

            TitleLabel {
                text: qsTr("Import from private key")
            }

            TextField {
                id: privateKey
                placeholderText: qsTr("Private Key")
                echoMode: TextInput.Password
                width: parent.width
            }

            Button {
                text: qsTr('Import')
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    WalletController.importFromPrivateKey(privateKey.text);
                }
            }

        }
    }

    ScrollDecorator {
        flickableItem: flick
        platformStyle: ScrollDecoratorStyle {
        }}

}  
