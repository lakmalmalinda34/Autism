from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os
import numpy as np
import tensorflow as tf
import joblib

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Receive the audio file from the POST request
        audio_file = request.files['audio']
        age = request.form.get('age')

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
            r.energy_threshold =1

            # Listen to the audio
            with sr.AudioFile(wav_temp_path) as source:
                audio_data = r.listen(source)

            # Perform speech recognition
            try:
                text = r.recognize_google(audio_data,language="si-LK")
            except sr.UnknownValueError:
                text = ""

            if not text:
                result = "Empty audio file"
            else:
                words = text.split()
                num_words = len(words)
                

            model = tf.keras.models.load_model("Autism_Trained_model.h5")
            scaler = joblib.load('standard_scaler.pkl')

            #model.summary()

            input_data =(int(age),num_words)

            np_array = np.asarray(input_data)

            data_reshaped = np_array.reshape(1,-1)

            std_data = scaler.transform(data_reshaped)

            threshold = 0.5
            prediction = model.predict(std_data)
            print(prediction)

            if prediction < threshold:
                result= "Autism Negetive"
            else:
                result= "Autism positve"

            
            print(num_words)
            print(text)
            # Return the result as JSON
            response_data = {'result': result , 'Word count': num_words}
            os.remove(wav_temp_path)
            os.remove(temp_audio_path)  # Remove the temporary files
            return jsonify(response_data)
        else:
            return jsonify({'error': 'No audio file provided in the request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
