import cv2
import base64
import numpy as np
import pandas as pd
from loader import load_db
from .utils import find_file
from config import VibesterConfig
from typing import List, Dict, Tuple
from dash import Dash, Input, Output, State, callback, no_update, ctx


def register_callbacks(app: Dash) -> None:
    @callback(
        Output({"name": "music_store", "type": "store", "page": "play"}, "data"),
        Input({"name": "url", "type": "location", "page": "play"}, "pathname"),
    )
    def load_music_store(pathname: str) -> List[Dict]:
        """
        Loads the music database from the local disk into a store component.
        """
        if pathname != "/play":
            return no_update

        df_db = load_db()  # Reads DB pickle file from the disk or creates it if it does not exist
        return df_db.to_dict("records")

    app.clientside_callback(
        """
        function(pathname) {
            const video = document.getElementById('play_video');

            if (pathname === '/play') {
                // Ensure access to the camera
                if (!video.srcObject) {
                    navigator.mediaDevices.getUserMedia({
                        video: {
                            facingMode: { ideal: 'environment' }  // Try to use the back camera
                        }
                    }).then((stream) => {
                        video.srcObject = stream;
                        video.style.display = "block";  // Show video feed
                    }).catch((err) => {
                        console.error("Camera access error:", err);
                        alert("Could not access the back camera. Falling back to any available camera.");
                        // Retry with default camera
                        navigator.mediaDevices.getUserMedia({ video: true })
                            .then((fallbackStream) => {
                                video.srcObject = fallbackStream;
                                video.style.display = "block";
                            })
                            .catch((fallbackErr) => {
                                console.error("Fallback camera access denied:", fallbackErr);
                            });
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
            }
            return "";
        }
        """,
        Output({"name": "dummy", "type": "store", "page": "play"}, "data"),
        Input({"name": "url", "type": "location", "page": "play"}, "pathname")
    )

    app.clientside_callback(
        """
        function(n_intervals) {
            const video = document.getElementById('play_video');
            const store = document.getElementById('captured_frame');

            if (video && video.style.display !== "none" && video.srcObject) {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');

                // Set canvas size to match video dimensions
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Draw the current video frame onto the canvas
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Convert canvas content to base64-encoded image (data URL)
                const frameData = canvas.toDataURL('image/png');

                return frameData;  // Return the frame data to store
            }
            return null;  // No frame captured
        }
        """,
        Output({"name": "frame_store", "type": "store", "page": "play"}, "data"),
        Input({"name": "sample", "type": "interval", "page": "play"}, "n_intervals")
    )

    @callback(
        Output("play_video", "style"),
        Output({"name": "music", "type": "audio", "page": "play"}, "src"),
        Output({"name": "stop_music", "type": "button", "page": "play"}, "style"),
        Input({"name": "frame_store", "type": "store", "page": "play"}, "data"),
        Input({"name": "stop_music", "type": "button", "page": "play"}, "n_clicks"),
        State({"name": "url", "type": "location", "page": "play"}, "pathname"),
        State({"name": "music_store", "type": "store", "page": "play"}, "data")
    )
    def scan_image(
        image_b64: str,
        n_clicks: int,
        pathname: str,
        music_store_data: List[Dict]
    ) -> Tuple[Dict, str, Dict]:
        """
        Scans webcamera image for QR codes. The camera image is provided as a base64 encoded string.
        """
        if pathname != "/play":
            return no_update, no_update, no_update

        if "frame_store" in str(ctx.triggered_id):
            if not image_b64 or pathname != "/play" or not music_store_data or len(music_store_data) == 0:
                return no_update, no_update, no_update

            # Decode the Base64 string into an image
            try:
                # Extract the Base64 portion of the string (remove "data:image/png;base64,")
                image_data = base64.b64decode(image_b64.split(",")[1])
                # Convert to a numpy array and decode into an image
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                # Scan the image_b64 for QR codes
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(image)

                # If there is a QR code decode and print it
                if data:
                    # If a QR code is detected, check it against music_store_data
                    df_music = pd.DataFrame(music_store_data)
                    matched_items = df_music.query(f"hash == '{data}'")
                    if len(matched_items) > 0:
                        # If a match is found, start playing music
                        filename = matched_items.iloc[0, :]["filename"]
                        # Find which folder the music is in
                        filepath = find_file(root_dir=VibesterConfig.path_music, filename=filename)
                        filepath = filepath.lstrip("data/")  # Strip this because of the music serving endpoint
                        return (
                            {"display": "none"},
                            filepath,
                            VibesterConfig.default_style_button_big_gif,
                        )

                return no_update, no_update, no_update

            except Exception as e:
                print(e)

        elif "stop_music" in str(ctx.triggered_id):
            if not n_clicks or pathname != "/play" or not music_store_data or len(music_store_data) == 0:
                return no_update, no_update, no_update

            else:
                # Show the webcam video, hide the button and the audio component
                return (
                    VibesterConfig.default_style_webcam_video,
                    "",
                    {"display": "none"},
                )
