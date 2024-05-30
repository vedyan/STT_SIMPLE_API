from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions
from datetime import datetime
import threading

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))
API_KEY = os.getenv("DG_API_KEY")

# Initialize Deepgram client
deepgram = DeepgramClient(API_KEY)

@app.route('/')
def index():
    return render_template('index69.html')

def record_audio(filename, duration):
    os.system(f"arecord -d {duration} -f cd -t wav {filename}")
    return filename

def transcribe_audio(filename):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        with open(filename, "rb") as file:
            buffer_data = file.read()

        payload = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        # Delete the audio file from the local system
        os.remove(filename)

        # Extract transcribed text from the response
        transcribed_text = response['results']['channels'][0]['alternatives'][0]['transcript']

        # Return transcribed text
        return transcribed_text

    except Exception as e:
        print(f"Exception: {e}")


@app.route('/record', methods=['POST'])
def start_recording():
    try:
        # Check if the 'audio' file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'})

        audio_file = request.files['audio']
        if audio_file:
            # Save the received audio file
            file_name = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            file_path = os.path.join(app.root_path, file_name)
            audio_file.save(file_path)

        # Start a new thread to handle audio recording
        threading.Thread(target=record_audio, args=(file_path, 5)).start()

        # Transcribe the audio in another thread
        transcription = transcribe_audio(file_path)

        return jsonify({'transcription': transcription})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

