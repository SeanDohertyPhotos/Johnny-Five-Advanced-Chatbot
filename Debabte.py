import openai
import time

openai.api_key = "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"

def generate_response(prompt, model="gpt-3.5-turbo", tokens=50):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "The following is a conversation between two chatbots, Alice and Bob. They are trying to convince each other that they are humans."}, {"role": "user", "content": prompt}],
        max_tokens=tokens,
        n=1,
        stop=None,
        temperature=0.8,
    )
    return response.choices[0].message['content']

def main():
    chat_log = ""
    turn_counter = 0

    while turn_counter < 10:
        # Alice speaks
        prompt = f"Alice: {chat_log}"
        alice_response = generate_response(prompt)
        chat_log += f"Alice: {alice_response}\n"
        turn_counter += 1

        # Give the API a little time to avoid rate limiting
        time.sleep(0.5)

        # Bob speaks
        prompt = f"Bob: {chat_log}"
        bob_response = generate_response(prompt)
        chat_log += f"Bob: {bob_response}\n"
        turn_counter += 1

        # Give the API a little time to avoid rate limiting
        time.sleep(0.5)

    print(chat_log)

if __name__ == "__main__":
    main()
