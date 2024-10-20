import asyncio
import json
import os
import uuid
import time

import httpx
import reflex as rx
from openai import AsyncOpenAI
import google.generativeai as genai

import json


# def gemini_starter():
    

GEMINI_API_KEY = 'AIzaSyBjWprVJ6UMCQXHE4GnO7OapYn1r_0ejak' 
genai.configure(api_key=GEMINI_API_KEY)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
)

# Upload your video file
files = [
    upload_to_gemini(r"./assets/calhacks.mp4", mime_type="video/mp4"),
]

# Wait for the files to be processed
wait_for_files_active(files)



chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                files[0],
            ],
        },
    ]
)



class SettingsState(rx.State):
    # The accent color for the app
    color: str = "violet"

    # The font family for the app
    font_family: str = "Poppins"


class State(rx.State):
    # The current question being asked.
    question: str

    # Whether the app is processing a question.
    processing: bool = False

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    user_id: str = str(uuid.uuid4())

    async def answer(self):
        # Set the processing state to True.
        self.processing = True
        yield

        # convert chat history to a list of dictionaries
        chat_history_dicts = []
        for chat_history_tuple in self.chat_history:
            chat_history_dicts.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            chat_history_dicts.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )

        self.chat_history.append((self.question, ""))

        # Clear the question input.
        question = self.question
        self.question = ""

        # Yield here to clear the frontend input before continuing.
        yield

        
        # This is where I am calling the gemini api
        prompt = f"{question}. Give the response with the key being 'details'. Please give the response in a paragraph format. Only provide it in a detailed response. Provide a detailed and descriptive explanation in natural language."

# Send the modified prompt to the model
        response = chat_session.send_message(prompt)

        # client = httpx.AsyncClient()

        # # call the agentic workflow
        # input_payload = {
        #     "chat_history_dicts": chat_history_dicts,
        #     "user_input": question,
        # }
        # deployment_name = os.environ.get("DEPLOYMENT_NAME", "MyDeployment")
        # apiserver_url = os.environ.get("APISERVER_URL", "http://localhost:4501")
        # response = await client.post(
        #     f"{apiserver_url}/deployments/{deployment_name}/tasks/create",
        #     json={"input": json.dumps(input_payload)},
        #     timeout=60,
        # )
        response_text = response.text
        response_data = json.loads(response_text)
        details = response_data.get('details')
        answer = details

        for i in range(len(answer)):
            # Pause to show the streaming effect.
            await asyncio.sleep(0.01)
            # Add one letter at a time to the output.
            self.chat_history[-1] = (
                self.chat_history[-1][0],
                answer[: i + 1],
            )
            yield
        

        # Add to the answer as the chatbot responds.
        answer = ""
        yield

        # async for item in session:
        #     if hasattr(item.choices[0].delta, "content"):
        #         if item.choices[0].delta.content is None:
        #             break
        #         answer += item.choices[0].delta.content
        #         self.chat_history[-1] = (self.chat_history[-1][0], answer)
        #         yield

        # Ensure the final answer is added to chat history
        if answer:
            self.chat_history[-1] = (self.chat_history[-1][0], answer)
            yield

        # Set the processing state to False.
        self.processing = False

    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False

