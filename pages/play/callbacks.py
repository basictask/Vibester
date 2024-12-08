from dash import Dash, Input, Output


def register_callbacks(app: Dash):
    app.clientside_callback(
        """
        function(pathname, captureClick) {
            const video = document.getElementById('play_video');
            const img = document.getElementById('play_captured_image');

            // Check pathname and show/hide camera components
            if (pathname === '/play') {
                // Ensure access to the camera
                if (!video.srcObject) {
                    navigator.mediaDevices.getUserMedia({ video: true })
                        .then((stream) => {
                            video.srcObject = stream;
                            video.style.display = "block";  // Show video feed
                        })
                        .catch((err) => {
                            console.error("Camera access denied:", err);
                        });
                }
            } else {
                // Hide camera elements if not on '/play'
                if (video.srcObject) {
                    const tracks = video.srcObject.getTracks();
                    tracks.forEach(track => track.stop());  // Stop the camera
                    video.srcObject = null;
                }
                video.style.display = "none";
                img.style.display = "none";
            }

            // Handle image capture when button is clicked
            if (pathname === '/play' && captureClick !== undefined) {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.save();  // Save the current canvas state
                ctx.scale(-1, 1);  // Flip the canvas horizontally
                ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);  // Draw the flipped image
                ctx.restore();  // Restore the canvas state

                // Convert canvas to Base64 image data
                const base64Image = canvas.toDataURL('image/png');  // Data URL format
                img.src = base64Image;  // Set image source
                img.style.display = "block";  // Show the captured image
                video.style.display = "none";  // Hide video feed
                return base64Image;  // Return Base64 data for storage
            }

            return null;  // Default return
        }
        """,
        Output({"name": "image_store", "type": "store", "page": "play"}, "data"),
        Input({"name": "url", "type": "location", "page": "play"}, "pathname")
    )
