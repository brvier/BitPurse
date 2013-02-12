import QtQuick 1.1
import com.nokia.meego 1.1
 
Dialog {
    id: root
 
    title: Label {
        text: qsTr("Set Wallet Key")
        color:'white'
    }
 
    property alias edPasswordPlaceholderText: edPassword.placeholderText
    property alias edConfirmPlaceholderText:  edPasswordConfirm.placeholderText
 
    property string password: ""
 
    property bool showClearPassword: false
    property int  minNumberOfCharacters: 6
 
    property string msgMinNumberOfCharacters:       qsTr( "Minimum number of characters: " )
    property string msgPasswordDoesNotMatchConfirm: qsTr( "Password does not match confirm!" )
 
 
    function advancedCheck( pwd )
    {
        // this function may contain additional password check
        // if something wrong  - function should return error message, 
        // otherwise function should return empty string
 
        return ""
    }
 
    function launch() {
        password = ""
        edPassword.text = ""
        edPasswordConfirm.text = ""
        open()
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
 
            ToolButton {
                id: btOk
                text: qsTr( "Ok" )
                onClicked: {
 
                    // check  password and confirmation
                    hintArea.state = "Hide"
                    if( edPassword.text != edPasswordConfirm.text )
                        showHint( msgPasswordDoesNotMatchConfirm )
                    else {
                        if( edPassword.text.length < minNumberOfCharacters )
                            showHint( msgMinNumberOfCharacters + minNumberOfCharacters )
                        else
                        {
                            var msg = advancedCheck( edPassword.text )
                            if( msg.length !== 0  )
                                showHint( msg )
                            else
                            {
                                password = edPassword.text
                                accept();
                            }
                        }
                    }
                }
            }
        }
    }
 
 
    content: Item {
        id: content
        height: edPassword.height * 2 + column.spacing * 2 + hintArea.height +
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
                id: edPassword
                anchors.left:  parent.left
                anchors.right: parent.right
                echoMode: showClearPassword ? TextInput.Normal : TextInput.Password
                placeholderText: qsTr( "Enter password" )
                onTextChanged: hintArea.state = "Hide"
            }
 
            TextField {
                id: edPasswordConfirm
                anchors.left:  parent.left
                anchors.right: parent.right
                echoMode: showClearPassword ? TextInput.Normal : TextInput.Password
                placeholderText: qsTr( "Confirm password" )
                onTextChanged: hintArea.state = "Hide"
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
                   color: 'white'
                   wrapMode: Text.WordWrap
                   text: ""
                   
                }
            }
        }
    }
 
    function showHint( msg )
    {
        hintArea.text  = msg
        hintArea.state = "Show"
    }
}
