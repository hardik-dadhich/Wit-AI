//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;
var gumStream;
//stream from getUserMedia()
var rec;
//Recorder.js object
var input;
//MediaStreamAudioSourceNode we'll be recording
// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext();
//new audio context to help us record
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");
//add events to those 3 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

/* Simple constraints object, for more advanced audio features see

https://addpipe.com/blog/audio-constraints-getusermedia/ */

var constraints = {
    audio: true,
    video: false,
};
/* Disable the record button until we get a success or fail from getUserMedia() */

recordButton.disabled = true;
stopButton.disabled = false;
pauseButton.disabled = false;

/* We're using the standard promise based getUserMedia()

https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia */

navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function(stream) {
        console.log(
            "getUserMedia() success, stream created, initializing Recorder.js ..."
        );
        /* assign to gumStream for later use */
        gumStream = stream;
        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);
        /* Create the Recorder object and configure to record mono sound (1 channel) Recording 2 channels will double the file size */
        rec = new Recorder(input, {
            numChannels: 1,
        });
        //start the recording process
        rec.record();
        console.log("Recording started");
    })
    .catch(function(err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
        pauseButton.disabled = true;
    });

function pauseRecording() {
    console.log("pauseButton clicked rec.recording=", rec.recording);
    if (rec.recording) {
        //pause
        rec.stop();
        pauseButton.innerHTML = "Resume";
    } else {
        //resume
        rec.record();
        pauseButton.innerHTML = "Pause";
    }
}

function stopRecording() {
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;
    //reset button just in case the recording is stopped while paused
    pauseButton.innerHTML = "Pause";
    //tell the recorder to stop the recording
    rec.stop(); //stop microphone access
    gumStream.getAudioTracks()[0].stop();
    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
}


// ------------------------------------------------------------------------------------------------------------
// Required for Django CSRF
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

recorder.addEventListener("dataAvailable", function(e) {
    var fileName = new Date().toISOString() + "." + e.detail.type.split("/")[1];
    var url = URL.createObjectURL(e.detail);

    var audio = document.createElement('audio');
    audio.controls = true;
    audio.src = url;

    var link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.innerHTML = link.download;

    // New Code starts here
    var progress = document.createElement('progress');
    progress.min = 0;
    progress.max = 100;
    progress.value = 0;
    var progressText = document.createTextNode("Progress: ");

    var button = document.createElement('button');
    var t = document.createTextNode("Upload?");
    button.id = 'button';
    button.appendChild(t);
    button.onclick = function() {
        upload(e.detail, progress);
    };

    // All that's left is to add the button and Progress bar to the list            
    var li = document.createElement('li');
    li.appendChild(link);
    li.appendChild(audio);
    li.appendChild(button);
    li.appendChild(progressText);
    li.appendChild(progress);

    recordingslist.appendChild(li);
});
// Actual Upload function using xhr
function upload(blob, progressBar) {
    var csrftoken = getCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'upload/', true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.setRequestHeader("MyCustomHeader", "Put anything you need in here, like an ID");

    xhr.upload.onloadend = function() {
        alert('Upload complete');
    };
    // If you want you can show the upload progress using a progress bar
    //var progressBar = document.querySelector('progress');
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            progressBar.value = (e.loaded / e.total) * 100;
            progressBar.textContent = progressBar.value; // Fallback for unsupported browsers.
        }
    };

    xhr.send(blob);




    let img_data = new Image();
    let canvas = document.getElementById("canvas");
    let lyrics = document.getElementById("lyrics");
    let controls_button = document.getElementById("controls");
    let ctx = canvas.getContext("2d");
    let x = 0;
    let y = 0;
    let playing = true;
    // x,y coordinates in pixels to display mouth shape for each word's phonemes
    let coordinates = [
        [-676 / 3, (-2 * 653) / 3, ""],
        [-676 / 3, (-2 * 653) / 3, ""],
        [(-2 * 676) / 3, -653 / 3, "Let"],
        [(-2 * 676) / 3, 0, "Let"],
        [-676 / 3, -653 / 3, "Let"],
        [-676 / 3, (-2 * 653) / 3, "Let me"],
        [(-2 * 676) / 3, 0, "Let me"],
        [(-2 * 676) / 3, 0, "Let me"],
        [-676 / 3, -653 / 3, "Let me"],
        [(-2 * 676) / 3, 0, "Let me tell"],
        [(-2 * 676) / 3, -653 / 3, "Let me tell"],
        [(-2 * 676) / 3, -653 / 3, "Let me tell"],
        [0, (-2 * 653) / 3, "Let me tell you"],
        [0, (-2 * 653) / 3, "Let me tell you"],
        [0, (-2 * 653) / 3, "Let me tell you"],
    ];
    // One way to adjust the speed of the animation is to dictate how many frames
    // each phoneme
    let currentIdx = 0;
    let count = 0;

    canvas.width = 676 / 3;
    canvas.height = 653 / 3 - 70;
    lyrics.style.fontSize = "2em";
    img_data.onload = animate;
    img_data.src =
        "https://thepracticaldev.s3.amazonaws.com/i/iubpy8p58bkfg7vwvxoh.jpg";

    let requestID = requestAnimationFrame(animate);

    function animate() {
        // When the count hits 17, go to the next phoneme
        // Change the `17` to another value and watch the
        // animation speed change
        if (count == 17) {
            currentIdx++;
            currentIdx %= coordinates.length;
            count = 0;
        }

        // Clear the canvas, draw the image and display the corresponding text
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(
            img_data,
            coordinates[currentIdx][0],
            coordinates[currentIdx][1]
        );
        lyrics.textContent = coordinates[currentIdx][2];

        count++;
        if (playing) {
            requestAnimationFrame(animate);
        }
    }

    // Allow the user to pause the animation because it might
    // get distracting while they are reading the blog
    const handleClick = (e) => {
        if (playing) {
            cancelAnimationFrame(requestID);
        } else {
            requestID = requestAnimationFrame(animate);
        }
        controls_button.textContent =
            controls_button.textContent == "Pause" ? "Play" : "Pause";
        playing = !playing;
    };

    controls_button.addEventListener("click", handleClick, false);


    $('.progress-bar-fill').delay(5000).queue(function() {
        $(this).css('width', '100%')
    });

    function start(al) {
        var bar = document.getElementById('progressBar');
        var status = document.getElementById('status');
        status.innerHTML = al + "%";
        bar.value = al;
        al++;
        var sim = setTimeout("start(" + al + ")", 1);
        if (al == 100) {
            status.innerHTML = "100%";
            bar.value = 100;
            clearTimeout(sim);
            var finalMessage = document.getElementById('finalMessage');
            finalMessage.innerHTML = "Process is complete";
        }
    }