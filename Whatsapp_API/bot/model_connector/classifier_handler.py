import json
import httpx


class ClassifierHandler:
    def __init__(self, model_url, model_secret_key):
        self.model_url = model_url
        self.model_secret_key = model_secret_key

    async def predict(self, text):
        data = [str(text)[0:512]]
        data = json.dumps(data)

        headers = {
            "Content-Type": "application/json",
            "Secret-Key": self.model_secret_key
        }

        # Send the request and wait for it to resolve
        async with httpx.AsyncClient() as client:
            r = await client.post(self.model_url, data=data, headers=headers)

        if r.status_code != 200:
            raise Exception(f"Error in model request: {r.status_code}")

        return r.json()["prediccion"][0]
