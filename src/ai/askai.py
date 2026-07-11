import json
from openai import OpenAI
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import get_apis

data=get_apis()[0]
client = OpenAI(
    api_key=data["api_key"],
    base_url=data["base_url"]
)
def ask_json(system_prompt,user_prompt):

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=data["model"],
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    return json.loads(response.choices[0].message.content)


def ask(system_prompt,user_prompt):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=data["model"],
        messages=messages,
        stream=False
    )
    
    return response.choices[0].message.content


def ask_reason(system_prompt,user_prompt):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=data["model"],
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    
    return [response.choices[0].message.reasoning_content,response.choices[0].message.content]



#print(ask("you are a helpful assistant","hello world!"))
#print(ask_json("The user will provide some exam text. Please parse the \"question\" and \"answer\" and output them in JSON format","Which is the highest mountain in the world? The Everest."))
#print(ask_reason("you are a helpful assistant","How will you explain AI to a 8-year-old boy?"))