
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

// Ping online user socket
const slug = window.location.pathname;
const cookie = getCookieByName(window.location.pathname.split('/')[1]);
socket.emit('user_online', {slug:slug, email:cookie.value});


function getCookieByName(cookieName){
    let cookie = {};
    document.cookie.split(';').forEach(item=>{
        const [key,value] = item.split('=');
        if (key.trim() === cookieName){
            cookie = {
                name: key.trim(),
                value: value.replace(/['"]+/g, '')
            }
        }
    });
    return cookie;
}