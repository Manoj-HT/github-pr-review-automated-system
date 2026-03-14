import requests
import json
import sys
#OLLAMA_MODEL = "gemma:2b"
OLLAMA_MODEL = "qwen3:8b"

def call_llm(system_prompt, user_prompt):
    print(f"    -> Calling local LLM ({OLLAMA_MODEL}) using Ollama API...")

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": True,
        "options": {
            "num_ctx": 4096  # Set a reasonable context window
        }
    }

    output_txt = []
    try:
        # Added timeout of 30 seconds for the initial connection
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "error" in data:
                    print(f"\n    -> [!] Ollama Error: {data['error']}")
                    break

                message = data.get("message", {})
                chunk = message.get("content", "")
                sys.stdout.write(chunk)
                sys.stdout.flush()
                output_txt.append(chunk)

                if data.get("done"):
                    break

    except requests.exceptions.Timeout:
        print("\n    -> [!] Error: Ollama API request timed out.")
    except Exception as e:
        print(f"\n    -> [!] Error calling Ollama API: {e}")

    print() # Add a final newline when done
    return "".join(output_txt).strip()