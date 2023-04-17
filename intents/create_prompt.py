def create_prompt(intent, parameters, message):
    # Construct the ChatGPT API prompt
    prompt = f"Johnny Five, please {intent} for {parameters['location']}."
    return prompt
