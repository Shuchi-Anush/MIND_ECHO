import requests

def get_llama_response(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.2:latest", "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("message", "")
    else:
        return "Error: Llama model did not respond correctly."
