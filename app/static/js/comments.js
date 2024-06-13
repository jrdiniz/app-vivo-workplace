$(document).ready(function(){
    // SocketIO - Publish start/stop live page    
    if (window.location.protocol == "https:"){
        var ws_scheme = "wss://";
    }else{
        var ws_scheme = "ws://";
    }
    var socket = io.connect(ws_scheme + location.host);
    
    // Go Live
    $('#status_enable').on('click', function(){
        console.log('enable');
        socket.emit('status_comment','status_enable');
    });
    $('#status_disable').on('click', function(){
        console.log('disable');
        socket.emit('status_comment','status_disable');
    });
});