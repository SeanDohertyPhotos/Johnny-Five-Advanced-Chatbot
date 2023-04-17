def process_message(message):
    # Process the user's message and identify the intent or API to call
    # For demonstration purposes, we'll assume the message is asking for weather
    intent = 'get_weather'
    parameters = {'location': 'New York'}

    return intent, parameters
