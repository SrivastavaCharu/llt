function speak() {
    var text = document.getElementById('speechText').value;
    var sourceLanguage = document.getElementById('sourceLanguage').value;
    var speechLanguage = document.getElementById('speechLanguage').value;

    // first call the translate API
    fetch('http://43.206.222.228:5000/translate', {
      
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text, source_language: sourceLanguage, target_language: speechLanguage.substring(0, 2) }),
    })
        .then(response => response.json())
        .then(data => {
            var translatedText = data.translated_text;

            // then call the speak API with the translated text
            fetch('http://43.206.222.228:5000/speak', {
        
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': true,
                },
                body: JSON.stringify({ text: translatedText, speechLanguage: speechLanguage }),
            })
                .then(response => response.blob())
                .then(blob => {
                    var url = window.URL.createObjectURL(blob);
                    var audio = document.querySelector("#speechAudio");
                    audio.src = url;
                    audio.play();
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}



function translate() {
    var text = document.getElementById('translateText').value;
    var sourceLanguage = document.getElementById('sourceLanguage').value;
    var targetLanguage = document.getElementById('targetLanguage').value;
    fetch('http://43.206.222.228:5000/translate', {
       
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': true,
        },
        body: JSON.stringify({ text: text, source_language: sourceLanguage, target_language: targetLanguage }),
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('translatedText').value = data.translated_text;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

var video = document.getElementById('video');
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
var imgUpload = document.getElementById('imgUpload');
var snap = document.getElementById('snap');
var openCameraButton = document.getElementById('openCamera');
var capturedImage = null;  // Variable to store the captured image

openCameraButton.addEventListener("click", function () {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
            video.srcObject = stream;
            video.play();
            video.style.display = 'block'; // show the video element
            snap.style.display = 'block'; // show the snap button
        });
    }
});

snap.addEventListener("click", function () {
    context.drawImage(video, 0, 0, 640, 480);
    video.style.display = 'none'; // hide the video element
    snap.style.display = 'none'; // hide the snap button
    canvas.toBlob(function (blob) {
        capturedImage = new File([blob], "snapshot.png");
        document.getElementById('uploadButton').disabled = false;
    });
});

function uploadImage() {
    var imgLanguage = document.getElementById('imgLanguage').value;
    var formData = new FormData();

    if (imgUpload.files.length > 0) {
        formData.append("imgUpload", imgUpload.files[0]);
    } else if (capturedImage !== null) {
        formData.append("imgUpload", capturedImage);
    }

    formData.append("language", imgLanguage);

    fetch('http://43.206.222.228:5000/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('imgTranslation').innerText = data.translation;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}



document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector('#translateButton').addEventListener('click', translate);
    document.querySelector('#speakButton').addEventListener('click', speak);
    // Assuming you have a button with id "uploadButton"
    document.querySelector('#uploadButton').addEventListener('click', uploadImage);
});