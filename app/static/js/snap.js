let video = document.getElementById('video')
let click_button = document.querySelector("#validate");
let canvas = document.querySelector("#canvas");


window.onload = async function() {
	let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	video.srcObject = stream;
}

var result = video.addEventListener( "loadedmetadata", function (event) {
	canvas.height = this.videoHeight;
	canvas.width = this.videoWidth;
}, false );

click_button.addEventListener('click', function() {
	loginStatus = document.getElementById("login-status");
   	canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
	let image_data_url = canvas.toDataURL('image/jpeg');
	$.post( 
		"/compare_faces", {
		javascript_data: image_data_url
	}).done(
		function(response){
			
			if (response == "Match"){
				loginStatus.style.color = 'green'
				loginStatus.innerHTML = "Identity verified !";
				console.log('match')
				// window.location.href = "/config";
			}
			else {
				loginStatus.style.color = 'red'
				loginStatus.innerHTML = "Failed to verify your identity !"
				console.log('no match')
			}
		}
	);
	
});