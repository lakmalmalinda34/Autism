from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Receive the audio file from the POST request
        audio_file = request.files['audio']

        if audio_file:
            # Save the audio file to a temporary location
            temp_audio_path = "temp_audio.wav"
            audio_file.save(temp_audio_path)

            # Load the audio file using pydub
            audio = AudioSegment.from_file(temp_audio_path)

            # Export it as a WAV file (optional)
            wav_temp_path = "temp_audio_converted.wav"
            audio.export(wav_temp_path, format="wav")

            # Initialize the speech recognizer
            r = sr.Recognizer()

            # Listen to the audio
            with sr.AudioFile(wav_temp_path) as source:
                audio_data = r.listen(source)

            # Perform speech recognition
            try:
                text = r.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = ""

            # Check the length of the saved audio file using pydub
            audio_duration_seconds = len(audio) / 1000  # Convert from milliseconds to seconds

            if not text:
                result = "Empty audio file"
            else:
                words = text.split()
                num_words = len(words)
                word_count = (40 / 120) * audio_duration_seconds

                if num_words > word_count:
                    result = "Autism Negative"
                else:
                    result = "Autism Positive"

            # Return the result as JSON
            response_data = {'result': result}
            os.remove(wav_temp_path)
            os.remove(temp_audio_path)  # Remove the temporary files
            return jsonify(response_data)
        else:
            return jsonify({'error': 'No audio file provided in the request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
