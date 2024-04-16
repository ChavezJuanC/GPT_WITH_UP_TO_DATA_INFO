# imports#
from openai import OpenAI
import os
import requests
import json
from datetime import datetime

# client#
API_KEY = os.getenv("API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")
client = OpenAI(api_key=API_KEY)

# conversation history list of objects
message_history = [{"role": "system", "content": "You are a helpful assistant"}]


# Fetch time helper function for AI#
def time_lookup(location):
    data_dict = json.loads(location)

    res = requests.get(
        "http://worldtimeapi.org/api/timezone/{}".format(data_dict["location"])
    )
    time_data = res.json()["datetime"]
    dt = datetime.fromisoformat(time_data)
    formatted_time = dt.strftime("%H:%M:%S")

    print("The current time in {} is {}".format(data_dict["location"], formatted_time))


# function to reset the conversation History object
def clear_history():
    global message_history
    message_history = [{"role": "system", "content": "You are a helpful assistant"}]


# Fetch Function to fetch from openAI
def fetch_open_ai(messageData):

    user_input = input("OpenAI: ")
    ##VALIDATE command or message##
    if user_input == "/clear":
        clear_history()
        return None

    message_history.append({"role": "user", "content": user_input})
    # print("History:", message_history)
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messageData,
        functions=[
            {
                "name": "time_lookup",
                "description": "look up the current time for a specified location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location for which to loop up the current time ex: 'Beijin'. How ever it has to be in a time zone format ex: Asia/Shangai, America/Bogota, Europe/Madrid, etc ",
                        }
                    },
                    "required": ["location"],
                },
            }
        ],
        function_call="auto",
    )

    res_object = {
        "role": response.choices[0].message.role,
        "content": response.choices[0].message.content,
    }

    ##Fucntion check##
    if res_object["content"] == None:
        if response.choices[0].message.function_call.name == "time_lookup":
            return time_lookup(response.choices[0].message.function_call.arguments)

    message_history.append(res_object)
    return response.choices[0].message.content


# keep interaction going

while True:
    response = fetch_open_ai(messageData=message_history)

    if response is not None:
        print(response)


##maybe add a limit to message History##