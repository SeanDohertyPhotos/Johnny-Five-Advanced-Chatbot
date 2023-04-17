from google.cloud import speech as speech_v1p1beta1

def transcribe_speech(audio_data, language_code='en-US'):
    client = speech_v1p1beta1.SpeechClient()
    config = speech_v1p1beta1.RecognitionConfig(
        encoding=speech_v1p1beta1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )
    response = client.recognize(config=config, audio=audio_data)

    return response.results[0].alternatives[0].transcript.strip()
