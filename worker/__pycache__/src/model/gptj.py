import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GPT:
    def __init__(self):
        self.url = os.environ.get('MODEL_URL')
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGING_FACE_TOKEN')}",
            "Content-Type": "application/json"
        }
        self.payload = {
            "inputs": "",
            "parameters": {
                "return_full_text": False,
                "use_cache": False,
                "max_new_tokens": 100  # 🔼 increased for longer answers
            }
        }

    def query(self, input: str) -> str:
        self.payload["inputs"] = input.strip()
        data = json.dumps(self.payload)

        try:
            response = requests.post(self.url, headers=self.headers, data=data)
            print("🔁 Raw response text:", response.text)

            data = response.json()

            # Check for error response
            if isinstance(data, dict) and "error" in data:
                print("❌ API Error:", data["error"])
                return "[Error] HuggingFace API issue"

            # Validate response structure
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()

            print("⚠️ Unexpected format:", data)
            return "[Error] No valid generated_text found"

        except Exception as e:
            print("🚨 JSON parse error:", e)
            return "[Error] Failed to parse model response"


if __name__ == "__main__":
    result = GPT().query("Will artificial intelligence help humanity conquer the universe?")
    print("\n🧠 GPT Output:", result)
