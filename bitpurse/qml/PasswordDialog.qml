import QtQuick 1.1
import com.nokia.meego 1.1
 
CommonDialog {
    id: root
 
    title: Label {
        text: qsTr("Enter your double password")
        color:'white'
    }
 
    property alias passwd: addrLabelField.text
    
 
    function launch() {
        addrLabelField.text = '';
        hideHint();
        open();
    }
 
 
    // we want to use only one button with own onClicked handler
    buttons: Item {
        id: buttonContainer
 
        LayoutMirroring.enabled: false
        LayoutMirroring.childrenInherit: true
 
        width: parent.width
        height: buttonRow.height
 
        Row {
            id: buttonRow
            objectName: "buttonRow"
            anchors.centerIn: parent
            spacing: 10
 
            Button {
                id: btOk
                text: qsTr( "Ok" )
                onClicked: {
 
                    // check  password and confirmation
                    hideHint();
                    //addrLabel = addrLabelField.text
                    if (passwd != '')
                      accept();
                    else
                      showHint("Double password can't be empty");
                }
            }
        }
    }
 
 
    content: Item {
        id: content
        height: addrLabelField.height + column.spacing + hintArea.height +
                column.anchors.topMargin + column.anchors.bottomMargin
        width: parent.width
        anchors.top: parent.top
 
        Column {
            id: column
            spacing:  10
            anchors.fill: parent
            anchors {
                leftMargin:   10
                rightMargin:  10
                topMargin:    10
            }

 
            TextField {
                id: addrLabelField
                anchors.left:  parent.left
                anchors.right: parent.right
                onTextChanged: hintArea.state = "Hide"
                text: ''
                echoMode: TextInput.Password
            } 
 
            Item {
                id: hintArea
                state: "Hide"
                anchors.left:  parent.left
                anchors.right: parent.right
                property alias text: hintText.text
 
                states: [
                    State {
                        name: "Show"
                        PropertyChanges { target: hintArea; height: hintText.paintedHeight }
                    },
                    State {
                        name: "Hide"
                        PropertyChanges { target: hintArea; height: 1 }
                    }
                ]
 
                // add hide-show animation
                transitions: [
                    Transition {
                        from: "Hide"; to: "Show"
                        NumberAnimation { target: hintArea; properties: "height"; duration: 300; easing.type: Easing.OutQuad }
                    },
                    Transition {
                        from: "Show"; to: "Hide"
                        NumberAnimation { target: hintArea; properties: "height"; duration: 300; easing.type: Easing.OutQuad }
                    }
                ]
 
                Text {
                   id: hintText
                   anchors.fill: parent
                   anchors.margins: 1
 
                   horizontalAlignment: Text.AlignHCenter
                   color: 'red'
                   wrapMode: Text.WordWrap
                   font.pixelSize: 16          
                   text: ""
                   
                }
            }
        }
    }
 
    function hideHint() {
        hintArea.text  = ''
        hintArea.state = "Hide"
    }

    function showHint( msg )
    {
        hintArea.text  = msg
        hintArea.state = "Show"
    }
}        
