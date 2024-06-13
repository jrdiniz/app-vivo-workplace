
// SocketIO - Publish start/stop live page    
if (window.location.protocol == "https:"){
    var ws_scheme = "wss://";
}else{
    var ws_scheme = "ws://";
}
var socket = io.connect(ws_scheme + location.host);

// Users Connected
socket.on('users_online', function(msg){
    let users_connected = document.getElementById("users_connected");
    users_connected.textContent = msg;
});
