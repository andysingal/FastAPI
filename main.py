from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
import os
import json

from fastapi.websockets import WebSocket

from enum import Enum
from pydantic import Field

class TextOption(str, Enum):
    NOOBLET = "Nooblet"
    TRENDIE = "Trendie"
    ELITE = "Elite"

class ButtonData(BaseModel):
    topic: Optional[str] = Field(None, max_length=30)
    max_chars: Optional[int] = 30
    text: Optional[TextOption] = None
    previous_topics: Optional[List[str]]
    number_of_words: Optional[int] = 50
app = FastAPI()

# replace this with your own origin which is the url you are hosting from if you are hosting this on a server
origins = [
    "http://localhost:8000/",
    "http://127.0.0.1:8000",
    "https://fastapi-production-bdc9.up.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=Response, responses={200: {"content": {"text/html": {}}}})
async def root():
    with open('static/index.html', 'r') as f:
        content = f.read()
    return Response(content, media_type="text/html")

@app.post("/get-topics")
async def handle_button_click(data: ButtonData):
    print("data is: ", data)
    if not data.text:
        raise HTTPException(status_code=400, detail="No text provided")

    print("previous topics: ", data.previous_topics)
    set_of_previous_topics = set(data.previous_topics)
    previous_topics = data.previous_topics
    print("length of previous topics vs set of previous topics: ", len(previous_topics), len(set_of_previous_topics))
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_KEY_HERE")

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      response_format={"type": "json_object"},
      stream=True,
      timeout=15,
      max_tokens=100,
      messages=[
        {"role": "system", "content": f"""You are a helpful assistant. return your answer in JSON format always. keep the topics random. pick at random and not in any order. don't repeat previous topics, choose new ones, you can choose micropscopic topics, it doesnt have to be so general. just dont repeat the previous topics. previous topics are: {data.previous_topics}.
         return your response as:
         {{
           "topics": [list of topics] # very short one-two word topics,"
         }}
         """},
        {"role": "user", "content": f"Don't repeat previous topics.Give me 5  new Python topics for the level {data.text}, only cover the topics for this level of python"},
      ]
    )

    responses = ''
    for chunk in response:
        if chunk.choices[0].delta.content: 
            text_chunk = chunk.choices[0].delta.content 
            print(text_chunk, end="", flush="true")
            responses += str(text_chunk)

    # return str -> json
    response = json.loads(responses)
    return JSONResponse(content=response)

async def get_explanation(data: ButtonData):
    if not data.topic:
        raise HTTPException(status_code=400, detail="No text provided")
    print(f"Button clicked with text: {data.topic}")
    print(f"data is: {data}")
    

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_KEY_HERE")

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      stream=True,
      timeout=15,
      max_tokens=500,
      messages=[
        {"role": "system", "content": f"please explain the given topic very simply. use code examples if possible. use {data.number_of_words} words max. "},
        {"role": "user", "content": f"Explain the Python topic {data.topic} with code examples "},
      ]
    )

    for chunk in response:
        if chunk.choices[0].delta.content: 
            text_chunk = chunk.choices[0].delta.content 
            print(text_chunk, end="", flush="true")
            yield {"data": text_chunk}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        button_data = ButtonData.parse_raw(data)
        async for response in get_explanation(button_data):
            await websocket.send_text(json.dumps(response))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)