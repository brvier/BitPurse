import QtQuick 1.1
import com.nokia.meego 1.0

Menu {
    id: itemMenu
    visualParent: pageStack

    property string addr;

    MenuLayout {
        MenuItem {
            text: qsTr("Edit label")
            onClicked: {
                editLabelDialog.addrLabel = WalletController.getLabelForAddr(addr);
                editLabelDialog.addr = addr;
                editLabelDialog.open();
                console.log('dialig still open?');
            }
        }
        MenuItem {
            text: qsTr("Copy address")
            onClicked: {

            }
        }
        MenuItem {
            text: qsTr("Delete")
            onClicked: {
                deleteQueryDialog.addr = addr;
                deleteQueryDialog.open();
            }
        }
    }
}
