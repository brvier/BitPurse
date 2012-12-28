import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.1

PageStackWindow {
    id: appWindow

    initialPage: loginPage
    
    function changePage(page) {
        if (pageStack.currentPage.objectName !== page.objectName) {
                                 	pageStack.replace(page);
                                 }
       }

    LoginPage {
        id: loginPage
        objectName: 'loginPage'
    }

    AboutPage {
        id: aboutPage
        objectName: 'aboutPage'
    }
    
    AddressesPage {
        id: addressesPage
        objectName: 'addressesPage'
    }

    AddressPage {
        id: addressPage
        objectName: 'addressPage'
    }

    SendPage {
        id: sendPage
        objectName: 'sendPage'
    }


    RequestPage {
        id: requestPage
        objectName: 'requestPage'
    }

    ToolBarLayout {
        id: mainTools
        visible: false

        ToolIcon {
            platformIconId: "toolbar-home"
            onClicked: {changePage(addressesPage);}
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
        id: addressesTools
        visible: false

        //Create new address : planned for futur release
        /*ToolIcon {
            platformIconId: "toolbar-add"
            onClicked: {;}
        }*/
        
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

        ToolIcon {
            platformIconId: "toolbar-view-menu"
            onClicked: (mainMenu.status === DialogStatus.Closed) ? mainMenu.open() : mainMenu.close()
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
            MenuItem { text: qsTr("About"); onClicked: pageStack.push(aboutPage);}
            MenuItem { text: qsTr("Preferences"); onClicked: {
                        pageStack.push(Qt.createComponent(Qt.resolvedUrl("SettingsPage.qml"))); }
                        }
                        
            MenuItem { text: qsTr("Report a bug");onClicked: {
                    Qt.openUrlExternally('https://github.com/khertan/KhtBitCoin/issues/new');
                }
            }
            MenuItem { text: qsTr('LogOut'); onClicked: {
                Settings.login = '';
                Settings.password = '';
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

}
