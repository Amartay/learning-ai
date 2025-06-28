import os
from dotenv import load_dotenv
import urllib.request
import json

load_dotenv()

data = {
    "question": "Where to travel in londons?",
    "chat_history": []
}

body = str.encode(json.dumps(data))

url = 'https://ai-foundry-prj-prompt-flo-bfuns.canadacentral.inference.ml.azure.com/score'
api_key = os.getenv("api_key")

if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))