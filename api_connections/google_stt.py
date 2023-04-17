from google.cloud import speech_v1p1beta1 as speech

def transcribe_speech(audio_data, language_code='en-US'):
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )
    response = client.recognize(config=config, audio=audio_data)

    return response.results[0].alternatives[0].transcript.strip()
