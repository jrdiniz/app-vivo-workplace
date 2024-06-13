
// Socket - Streaming Status
if (window.location.protocol == "https:"){
    var ws_scheme = "wss://";
}else{
    var ws_scheme = "ws://";
}

// Redirect with event status change
const socket = io.connect(ws_scheme + location.host);
socket.on('event_status', (message) =>{
    const redirect = `${window.location.protocol}//${window.location.host}/${message.slug}`;
    window.location.href = redirect;
});
