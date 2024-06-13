const sendMessage = document.getElementById('send-message');
const inputMessage = document.getElementById('input-message');
const messageBox = document.getElementById('message-box');
const nickName = document.getElementById('nickname');
const buttonsDeleteMessage = document.getElementsByName('delete-message');
const inputRegisterID = document.getElementById("input-register-id");

// Got to end of message list
function goToEndMessageList(){
    messageBox.scrollTop = messageBox.scrollHeight - messageBox.clientHeight;
}

// Clean message input
function cleanMessageInput(){
    if (inputMessage.value.length === 0){
        sendMessage.disabled = true;
    }else if (inputMessage.value.length > 0) {
        sendMessage.disabled = false  
    }    
}

// Add Class to messages
function setColorBox(nickname){
    if (nickname === labelNickname.innerText){
        return 'chat-message-you';
    }else{
        return 'chat-message-guest';
    }
}
// Add Message to Message Box
function addMessageOld(message){
    
    // Message Container
    let chatMessageLeftEL = document.createElement("div");
    //chatMessageLeftEL.classList.add('chat-message-left', 'pb-2');
    chatMessageLeftEL.classList.add('container', 'my-1', 'message', 'rounded');
    chatMessageLeftEL.setAttribute('id', `message_${message['message_id']}`);
    
    // Message Header 
    let chatMessageEL = document.createElement("div");
    //chatMessageEL.classList.add('flex-shrink-1', 'bg-light', 'rounded', 'py-2', 'px-3', 'ml-3', 'mr-3');
    chatMessageEL.classList.add('row', 'pt-2', 'align-items-left');


    let chatUserEL = document.createElement("div");
    chatUserEL.classList.add('mb-1');
    
    let chatNickname = document.createElement("span");
    chatNickname.classList.add('fw-bold');
    chatNickname.innerHTML = `${message['nickname'] } - `;

    let chatMessageDateTime = document.createElement("span");
    chatMessageDateTime.classList.add('small', 'text-secondary');
    chatMessageDateTime.innerText = message['create_at'];

    let chatMessageTextEL = document.createElement("span");
    chatMessageTextEL.innerText =  message['text'];

    if (nickName.innerText === message['nickname']){
        chatMessageEL.classList.remove('bg-light');
        chatMessageEL.classList.add('message');

        chatMessageDateTime.classList.remove('text-secondary');
        chatMessageDateTime.classList.add('text-light');
    }

    chatUserEL.appendChild(chatNickname);
    chatUserEL.appendChild(chatMessageDateTime);
    chatMessageEL.appendChild(chatUserEL);
    chatMessageEL.appendChild(chatMessageTextEL);
    chatMessageLeftEL.appendChild(chatMessageEL);
    messageBox.appendChild(chatMessageLeftEL);
    goToEndMessageList();
}


// Add Message to Message Box
function addMessage(message){
    
    // Message Container
    let chatMessageEL = document.createElement("div");
    chatMessageEL.classList.add('container', 'my-1', 'message', 'rounded');
    chatMessageEL.setAttribute('id', `message_${message['message_id']}`);
    
    // Message Header 
    let chatMessageHeaderEL = document.createElement("div");
    chatMessageHeaderEL.classList.add('row', 'pt-2', 'align-items-left');
    
    // Message Header Content 
    let chatMessageHeaderContent = document.createElement("div");

    if (nickName.innerText === message['nickname']){
        
        chatMessageHeaderContent.classList.add('col-10', 'py-1');

        // Message Header Nickname
        let chatMessageHeaderNickNameText = document.createElement("span");
        chatMessageHeaderNickNameText.classList.add('fw-bold');
        chatMessageHeaderNickNameText.innerHTML = `${message['nickname'] } - `;

        // Message Header DateTime
        let chatMessageHeaderCreateAtText = document.createElement("span");
        chatMessageHeaderCreateAtText.classList.add('small', 'text-light');
        chatMessageHeaderCreateAtText.innerText = message['create_at'];

        chatMessageHeaderContent.appendChild(chatMessageHeaderNickNameText);
        chatMessageHeaderContent.appendChild(chatMessageHeaderCreateAtText);

        // Delete Message Button
        let chatMessageHeaderDeleteEL = document.createElement("div");
        chatMessageHeaderDeleteEL.classList.add('col-2');

        let chatMessageHeaderDeleteBtn = document.createElement("button");
        chatMessageHeaderDeleteBtn.classList.add('btn', 'btn-sm','text-light', 'btn-delete-message');
        chatMessageHeaderDeleteBtn.setAttribute('name','delete-message');
        chatMessageHeaderDeleteBtn.setAttribute('id',`${message['message_id']}`);

        let chatMessageHeaderDeleteIcon = document.createElement("i");
        chatMessageHeaderDeleteIcon.classList.add('bi', 'bi-trash')

        chatMessageHeaderDeleteBtn.appendChild(chatMessageHeaderDeleteIcon);
        chatMessageHeaderDeleteEL.appendChild(chatMessageHeaderDeleteBtn);
        chatMessageHeaderEL.appendChild(chatMessageHeaderContent)
        chatMessageHeaderEL.appendChild(chatMessageHeaderDeleteEL)
        
    } else {

        chatMessageEL.classList.add('bg-light');
        chatMessageEL.classList.remove('message');
        chatMessageHeaderContent.classList.add('col-12', 'py-1');

        // Message Header Nickname
        let chatMessageHeaderNickNameText = document.createElement("span");
        chatMessageHeaderNickNameText.classList.add('fw-bold');
        chatMessageHeaderNickNameText.innerHTML = `${message['nickname'] } - `;

        // Message Header DateTime
        let chatMessageHeaderCreateAtText = document.createElement("span");
        chatMessageHeaderCreateAtText.classList.add('small', 'text-secondary');
        chatMessageHeaderCreateAtText.innerText = message['create_at'];

        chatMessageHeaderContent.appendChild(chatMessageHeaderNickNameText);
        chatMessageHeaderContent.appendChild(chatMessageHeaderCreateAtText);

        chatMessageHeaderEL.appendChild(chatMessageHeaderContent)

    }
    
    // Message Content
    let chatMessageContentEL = document.createElement("div");
    chatMessageContentEL.classList.add('row', 'pb-2', 'align-items-left');

    let chatMessageContentText = document.createElement("div");
    chatMessageContentText.classList.add('col-12', 'text-break');
    chatMessageContentText.innerHTML = message['text']
    chatMessageContentEL.appendChild(chatMessageContentText);

    chatMessageEL.appendChild(chatMessageHeaderEL);
    chatMessageEL.appendChild(chatMessageContentEL);
    messageBox.appendChild(chatMessageEL);
    goToEndMessageList();
}

// Connect to server
// Socket functions
if (window.location.protocol == "https:"){
    var scheme = "https://";
}else{
    var scheme = "http://";
}

const socketChat = io.connect(scheme + location.host);
socketChat.on('connect', () =>{
    socketChat.send('Connected to server');

    // Receive message from server
    socketChat.on('message from server', (message)=>{
        addMessage({
            'create_at': message['create_at'],
            'nickname': message['nickname'],
            'text': message['text'],
            'message_id': message['message_id'],
            'register_id': message['register_id']
        });
    });

    // Send message to server
    sendMessage.addEventListener('click', ()=>{
        if (inputMessage.value.length > 0){
            socketChat.emit('message from user', {'nickname': nickName.innerText, 'text': inputMessage.value, 'event_id': sendMessage.value, 'register_id': inputRegisterID.value });
            goToEndMessageList();
            cleanMessageInput();
            inputMessage.value = '';
        }
    });

    // Send Delete Message
    Array.from(buttonsDeleteMessage).forEach((buttonDelete, index)=>{
        buttonDelete.addEventListener('click',() =>{
            messageID = buttonDelete.getAttribute('id');
            socket.emit('send delete chat message', messageID);
            document.getElementById(`message_${messageID}`).remove();
        });
    })

    socketChat.on('receive delete chat message', (message)=>{
        if (nickName.innerText !== message['nickname']){
            document.getElementById(`message_${message['message_id']}`).remove();
        }
    })
});


// Check if input message is empty
inputMessage.addEventListener('input', (e)=>{
    if (e.target.value.length === 0){
        sendMessage.disabled = true;
    }else if (e.target.value.length > 0) {
        sendMessage.disabled = false  
    }
});

// Keyboard Events
inputMessage.addEventListener('keydown', (e) =>{
    // Clean input messagebox
    if (e.key === 'Escape'){
        inputMessage.value = '';
    }
    // Send message with Enter
    if (e.key == "Enter" & sendMessage.disabled === false){
        sendMessage.click();
    }
});



// Initialize
goToEndMessageList();