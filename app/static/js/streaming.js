const eventURL = document.getElementById("event-url");
const slug = eventURL.innerText.split('/')[3];
const publishStreamingBtn = document.getElementById("publish-streaming");
const playerPreview = document.getElementById("player");
    
// VideoJS
if (playerPreview !== null){
    var player = videojs('player',{
        controls: true,
        autoplay: false,
        preload: 'auto',
        muted: true,
        fluid: true,
        language: 'pt-BR'
    });
}
    
// Input File Upload (Bootstrap 4)  
$('#upload-poster').change(function(event){
    var fileName = event.target.files[0].name;
    if (event.target.nextElementSibling!=null){
        event.target.nextElementSibling.innerText=fileName;
    }
});

// SocketIO - Publish start/stop live page
let ws_scheme = "";
if (window.location.protocol == "https:"){
    ws_scheme = "wss://";
}else{
    ws_scheme = "ws://";
}
const socket = io.connect(ws_scheme + location.host);
// Event Listeners
const status = publishStreamingBtn.getAttribute('value')
if (status === 'started'){
    publishStreamingBtn.setAttribute('value', 'finished');
    publishStreamingBtn.classList.remove('btn-success');
    publishStreamingBtn.classList.add('btn-danger');
    publishStreamingBtn.innerText = 'Encerrar Webinar'
}else if (status === 'finished'){
    publishStreamingBtn.setAttribute('value', 'started');
    publishStreamingBtn.classList.remove('btn-danger');
    publishStreamingBtn.classList.add('btn-success');
    publishStreamingBtn.innerText = 'Iniciar Webinar'
}; 

publishStreamingBtn.addEventListener('click', () =>{
    socket.emit('event_status',{status:status, slug:slug});
});


// Enable/Disable dropdown LiveID
let rd_liveid = document.getElementById('rdLiveID');
let dropdown_liveid = document.getElementById('selectLiveID');
let input_source= document.getElementById('inputSource');
let rd_url = document.getElementById('rdUrl');
rd_liveid.onclick = function(){
    if (rd_liveid.checked == true){
        rd_url.checked = false;
        dropdown_liveid.disabled = false;
        input_source.disabled = true
    }
}
rd_url.onclick = function(){
    if (rd_url.checked == true){
        rd_liveid.checked == false;
        dropdown_liveid.disabled = true;
        input_source.disabled = false;
    }
}

