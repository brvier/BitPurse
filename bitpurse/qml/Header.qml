import QtQuick 1.1
import com.nokia.meego 1.0

Rectangle {
    id:header

    property alias title: headerlabel.text
    property alias source: headericon.source
    property alias color: header.color

    anchors.top: parent.top
    width:parent.width
    height:70
    color: '#666666'
    z:2

    Image {
        id:headericon
        anchors.verticalCenter: parent.verticalCenter
        sourceSize.width: 48
        sourceSize.height: 48
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.left: parent.left
    }

    Text{
        id:headerlabel
        anchors.right: parent.right
        anchors.left: headericon.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        font { bold: false; family: "Nokia Pure Text"; pixelSize: 36; }
        color:"white"
        text:''
    }
    BusyIndicator {
        id: busyindicatorsmall
        platformStyle: BusyIndicatorStyle { size: "medium"; spinnerFrames: "image://theme/spinnerinverted"}
        running: WalletController.busy ? true : false;
        opacity: WalletController.busy ? 1.0 : 0.0;
        anchors.right: header.right
        anchors.rightMargin: 10
        anchors.verticalCenter: header.verticalCenter
    }
} 