import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1

PageStackWindow {
    id: appWindow

    initialPage: WalletController.walletExists() ? ((WalletController.walletUnlocked) ? walletPage : loginPage) : welcomePage
    
    function changePage(page) {
        if (pageStack.currentPage.objectName !== page.objectName) {
            pageStack.replace(page);
        }
    }

    LoginPage {
        id: loginPage
        objectName: 'loginPage'
    }

    WelcomePage {
        id: welcomePage
        objectName: 'welcomePage'
    }

    /*AboutPage {
        id: aboutPage
        objectName: 'aboutPage'
    }*/
    
    WalletPage {
        id: walletPage
        objectName: 'walletPage'
    }

    AddressPage {
        id: addressPage
        objectName: 'addressPage'
    }

    SendPage {
        id: sendPage
        objectName: 'sendPage'
    }


    /*RequestPage {
        id: requestPage
        objectName: 'requestPage'
    }*/

    ToolBarLayout {
        id: mainTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-home"
            onClicked: {changePage(walletPage); WalletController.update();}
        }

        ToolIcon {
            platformIconId: "toolbar-up"
            onClicked: {changePage(sendPage);}
        }

        /*ToolIcon {
            platformIconId: "toolbar-down"
            onClicked: {changePage(requestPage);}
        }*/

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            onClicked: (mainMenu.status === DialogStatus.Closed) ? mainMenu.open() : mainMenu.close()
        }
    }

    ToolBarLayout {
        id: walletTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-add"
            onClicked: {WalletController.newAddr();}
        }
        
        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: parent.right
            onClicked: (mainMenu.status === DialogStatus.Closed) ? mainMenu.open() : mainMenu.close()
        }
    }

    ToolBarLayout {
        id: backTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-back"
            onClicked: {pageStack.pop();}
        }
    }

    ToolBarLayout {
        id: simpleTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: parent.right
            onClicked: (mainMenu.status === DialogStatus.Closed) ? mainMenu.open() : mainMenu.close()
        }
    }

    Menu {
        id: mainMenu
        visualParent: pageStack
        MenuLayout {
            MenuItem { text: qsTr("About");
                onClicked: pageStack.push(
                               Qt.createComponent(
                                   Qt.resolvedUrl("AboutPage.qml")));
            }
            MenuItem { text: qsTr("Preferences");
                onClicked: {
                    pageStack.push(
                                Qt.createComponent(
                                    Qt.resolvedUrl("SettingsPage.qml"))); }
            }

            MenuItem { text: qsTr("Report a bug");
                onClicked: {
                    Qt.openUrlExternally('https://github.com/khertan/BitPurse/issues/new');
                }
            }
            MenuItem { text: qsTr('LogOut'); onClicked: {
                    WalletController.currentPassKey = '';
                    changePage(loginPage);
                }
            }
        }
    }

    function onError(errMsg) {
        errorEditBanner.text = errMsg;
        errorEditBanner.show();
    }

    InfoBanner{
        id:errorEditBanner
        text: ''
        timerShowTime: 15000
        timerEnabled:true
        anchors.top: parent.top
        anchors.topMargin: 60
        anchors.horizontalCenter: parent.horizontalCenter
    }

    //State used to detect when we should refresh view
    states: [
        State {
            name: "fullsize-visible"
            when: platformWindow.viewMode === WindowState.Fullsize && platformWindow.visible
            StateChangeScript {
                script: {
                    if ((pageStack.currentPage.objectName === 'walletPage') && (! WalletController.busy)) {
                        WalletController.update();
                    }
                    if ((pageStack.currentPage.objectName === 'addressPage') && (! WalletController.busy)) {
                        WalletController.update();
                    }
                }
            }
        }
    ]
}    