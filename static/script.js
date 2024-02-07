
const urlParams = new URLSearchParams(window.location.search);
const socket = io.connect('wss://' + document.domain + ':' + location.port);
let video_res = [0, 0]
let sended = 0;
let received = 0;

socket.on('response', function(data) {
    received += 1;
    let cursor = [0, 0];
    if (data.status === "ok" && data.image) {
        console.log("Status: ok", data.click)

        const buttons = document.querySelectorAll('.button');
        if (data.cursor != null) {
          cursor = [(window.innerWidth / video_res[0]) * data.cursor[0], (window.innerHeight / video_res[1]) * data.cursor[1]]
        }

        buttons.forEach(button => {
            const rect = button.getBoundingClientRect();
            if (cursor[0] >= rect.left && cursor[0] <= rect.right && cursor[1] >= rect.top && cursor[1] <= rect.bottom) {
                button.classList.add('button_hover');
                if (data.click){
                    const hrefValue = button.getAttribute('onclick');
                    eval(hrefValue);
                }
            } else {
                button.classList.remove('button_hover');
            }            
        });

        const processedImageElement = document.getElementById('processedImage');
        processedImageElement.src = data.image;
    } else {
        console.error("Nepodařilo se získat zpracovaný obrázek.");
    }
});

function captureAndSendImage() {
    const video = document.querySelector('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    video_res = [video.videoWidth, video.videoHeight]
    canvas.getContext('2d').drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    if (sended -1 <= received) {
        socket.emit('image_navigation', { image: canvas.toDataURL('image/jpeg')});
        sended += 1;
    }
}

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true }) // get permission
    .then(() => navigator.mediaDevices.enumerateDevices())
    .then(devices => {
        const videoDevices = devices.filter(device => device.kind === 'videoinput');

        if (videoDevices.length <= 0){
            throw new Error('Žádná kamera nenalezena.');
        }
        
        if (urlParams.has('camera')){
            const cameraID = Number(urlParams.get('camera'));
            return navigator.mediaDevices.getUserMedia({ video: { deviceId: videoDevices[cameraID].deviceId } });
        }
        else {
            location.href = `?camera=0`;
        }
    })
    .then(function(stream) {
        const video = document.querySelector('video');
        video.srcObject = stream;
        video.onloadedmetadata = function(e) {
            video.play();
            setInterval(captureAndSendImage, 100); // Snímek každých xxx ms
        };
    })
    .catch(function(err) {
        console.log(err);
    });
}

window.addEventListener("load", (event) => {
    startCamera();
});