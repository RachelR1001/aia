import requests
import json
import time
import os

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_LLM_DEPLOY_ID = os.environ["AZURE_LLM_DEPLOY_ID"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

def chat(messages, max_tokens=256):

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_LLM_DEPLOY_ID}/chat/completions?api-version=2024-02-01"

    # HTTP headers for authorization
    headers = {
        'Content-Type': 'application/json',
        'api-key': f'{AZURE_OPENAI_API_KEY}'
    }

    # 
    payload = json.dumps({
        "messages": messages,
        "stream": False,
        "max_tokens": max_tokens
    })
    

    # call api
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error raised by inference endpoint: {e}")

    if response.status_code != 200:
        raise ValueError(f"Failed with response: {response.json()}")

    try:
        parsed_response = response.json()['choices'][0]['message']
        return parsed_response
        

    except requests.exceptions.JSONDecodeError as e:
        print(
            f"Error raised during decoding response from inference endpoint: {e}."
            f"\nResponse: {response.text}"
        )
    

if __name__ == '__main__':
    messages = [
        {
        "role": "user",
        "content": "Who are you?"
        }
    ]
    res = chat(messages, 32)
    print(res)
