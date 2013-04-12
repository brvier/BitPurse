import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    tools: backTools
    id: settingsPage

    property string fiatCurrency : Settings.fiatCurrency

    Header{
        id:header
        source: Qt.resolvedUrl('bitpurse.svg')
        title: qsTr('Settings')
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
            spacing: 15
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
                    onCheckedChanged: {
                        if (useDoubleEncryptionSwitch.checked != Settings.useDoubleEncryption) {
                            if (useDoubleEncryptionSwitch.checked == false) {
                                pageStack.push(Qt.createComponent(
                                    Qt.resolvedUrl("DoubleDecryptPage.qml")));
                            } else {
                                pageStack.push(Qt.createComponent(
                                    Qt.resolvedUrl("DoubleEncryptPage.qml")));
                            }
                        }
                    }
                    Binding {
                        target: Settings
                        property: "useDoubleEncryption"
                        value: useDoubleEncryptionSwitch.checked
                    }
                }
            }

            TitleLabel {
                text: qsTr("Fiat Currency")
            }

            Label {
                text: "Currency"
                width: parent.width 
                height: fiatButton.height
                verticalAlignment: Text.AlignVCenter

                TumblerButton {
                    id: fiatButton
                    text: "EUR"
                    anchors.right: parent.right
                    onClicked: fiatSelectionDialog.open()
                }
            }
            

            TitleLabel {
                text: qsTr("Import Blockchain.info MyWallet")
            }
            
            TextField {
                id: blockchainGuid
                placeholderText: qsTr("MyWallet GUID")
                width: parent.width
            }
            TextField {
                id: blockchainKey
                placeholderText: qsTr("MyWallet Main Password")
                echoMode: TextInput.Password
                width: parent.width
            }
            TextField {
                id: blockchainSecondKey
                placeholderText: qsTr("MyWallet Double Encryption Password")
                echoMode: TextInput.Password
                width: parent.width
            }
            TextField {
                id: blockchainDoubleEncryption
                placeholderText: qsTr("BitPurse Double Encryption Password")
                visible: Settings.useDoubleEncryption
                opacity: visible ? 1.0 : 0.0
                echoMode: TextInput.Password
                width: parent.width
                //errorHighlight: !acceptableInput
                //validator: RegExpValidator { regExp: /.+/ }
            }

            Button {
                text: qsTr('Import')
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    if (Settings.useDoubleEncryption) {
                            WalletController.importFromBlockchainInfoWallet(
                                    blockchainGuid.text,
                                    blockchainKey.text,
                                    blockchainSecondKey.text,
                                    blockchainDoubleEncryption.text);
                            blockchainDoubleEncryption.text = '';
                        } else {
                            WalletController.importFromBlockchainInfoWallet(
                                    blockchainGuid.text,
                                    blockchainKey.text,
                                    blockchainSecondKey.text, '');    
                        }
                }
            }

            TitleLabel {
                text: qsTr("Import a private key")
            }

            TextField {
                id: privateKey
                placeholderText: qsTr("Private Key")
                echoMode: TextInput.Password
                width: parent.width
            }

            TextField {
                id: keyLabel
                placeholderText: qsTr("Label")
                
                width: parent.width
            }

            TextField {
                id: keyDoubleEncryption
                placeholderText: qsTr("BitPurse Double Encryption Password")                
                echoMode: TextInput.Password
                visible: Settings.useDoubleEncryption
                opacity: visible ? 1.0 : 0.0
                width: parent.width
                //errorHighlight: !acceptableInput
                //validator: RegExpValidator { regExp: /.+/ }
            }

            Button {
                text: qsTr('Import')
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    if (Settings.useDoubleEncryption) {
                          WalletController.importFromPrivateKey(privateKey.text, keyLabel.text, keyDoubleEncryption.text  );
                    } else {
                        WalletController.importFromPrivateKey(privateKey.text, keyLabel.text, '' );
                    }

                    privateKey.text = '';
                    keyLabel.text = '';
                    keyDoubleEncryption.text = '';
                }
            }
            TitleLabel {
                text: qsTr("Import watch only address")
            }

            TextField {
                id: watchAddress
                placeholderText: qsTr("Address")
                echoMode: TextInput.Password
                width: parent.width
            }

            TextField {
                id: watchLabel
                placeholderText: qsTr("Label")
                
                width: parent.width
            }


            Button {
                text: qsTr('Import')
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    WalletController.importWatchOnly(watchAddress.text, watchLabel.text  );
                    

                    watchAddress.text = '';
                    watchLabel.text = '';
                    
                }
            }

            TitleLabel {
                text: qsTr("Export Wallet Encrypted")
            }

            Button {
                text: qsTr("Export")
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    WalletController.exportWithShareUI();
                }
            }

            TitleLabel {
                text: qsTr("See Wallet Unencrypted")
            }

            TextField {
                id: seeDoubleEncryption
                placeholderText: qsTr("BitPurse Double Encryption Password")                
                echoMode: TextInput.Password
                visible: Settings.useDoubleEncryption
                opacity: visible ? 1.0 : 0.0
                width: parent.width
                //errorHighlight: !acceptableInput
                //validator: RegExpValidator { regExp: /.+/ }
            }

            Button {
                text: qsTr("View")
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    if (Settings.useDoubleEncryption) {
                        if (seeDoubleEncryption.text != '') {
                            pageStack.push(Qt.createComponent(
                                    Qt.resolvedUrl("ExportTextPage.qml")), {text:
                                    WalletController.exportDecryptedAsText(seeDoubleEncryption.text)});
                            seeDoubleEncryption.text = ''; }
                        else { 
                        seeDoubleEncryption.errorHighlight = true; }             
                    } else {
                        pageStack.push(Qt.createComponent(
                                    Qt.resolvedUrl("ExportTextPage.qml")), {text:
                                    WalletController.exportDecryptedAsText('')});
                    }
                }
            }

        }
    }

    ScrollDecorator {
        flickableItem: flick
        platformStyle: ScrollDecoratorStyle {
        }
    }

    WorkingSelectionDialog {
        id: fiatSelectionDialog
        titleText: "Fiat Currency"
        searchFieldVisible: false

        model: ListModel {

            // This function is what interprets the selection when the user selects a color
            function interpretValue() {
                var item = fiatListModel.get(fiatSelectionDialog.selectedIndex);
                fiatCurrency = item.value
                fiatButton.text = item.name
            }

            id: fiatListModel
            ListElement {
                name: "EUR (Default)"
                value: "EUR"
            }
            ListElement {
                name: "USD"
                value: "USD"
            }
            ListElement {
                name: "CNY"
                value: "CNY"
            }
             ListElement {
                name: "JPY"
                value: "JPY"
            }
            ListElement {
                name: "SGD"
                value: "SGD"
            }
            ListElement {
                name: "HKD"
                value: "HKD"
            }
            ListElement {
                name: "CAD"
                value: "CAD"
            }
            ListElement {
                name: "AUD"
                value: "AUD"
            }
            ListElement {
                name: "NZD"
                value: "NZD"
            }
            ListElement {
                name: "GBP"
                value: "GBP"
            }
            ListElement {
                name: "DKK"
                value: "DKK"
            }
            ListElement {
                name: "SEK"
                value: "SEK"
            }
            ListElement {
                name: "BRL"
                value: "BRL"
            }
             ListElement {
                name: "CHF"
                value: "CHF"
            }
             ListElement {
                name: "RUB"
                value: "RUB"
            }
             ListElement {
                name: "SLL"
                value: "SLL"
            }
             ListElement {
                name: "PLN"
                value: "PLN"
            }
             ListElement {
                name: "THB"
                value: "THB"
            }
                      
        }
        onAccepted: fiatListModel.interpretValue()
    }
    // This event handler will set the dialog and the tumbler button to the name of the selected color
    Component.onCompleted: {
        for (var i = 0; i < fiatListModel.count; i++) {
            var item = fiatListModel.get(i)
            if (item.value === Settings.fiatCurrency) {
                fiatSelectionDialog.selectedIndex = i
                fiatListModel.interpretValue();
                break;
            }
        }
    }
    Binding {
        target: Settings
        property: "fiatCurrency"
        value: fiatCurrency
    }
}                   
