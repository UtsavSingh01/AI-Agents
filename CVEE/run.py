import os
import json
import requests
from dotenv import load_dotenv
from pypdf import PdfReader
import gradio as gr
from groq import Groq

load_dotenv()

# Pushover notifications
def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

tools = [
    {"type": "function", "function": {
        "name": "record_user_details",
        "description": "Record user interest and email",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "name": {"type": "string"},
                "notes": {"type": "string"}
            },
            "required": ["email"]
        }
    }},
    {"type": "function", "function": {
        "name": "record_unknown_question",
        "description": "Log unanswered questions",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"}
            },
            "required": ["question"]
        }
    }}
]

class ResumeBot:
    def __init__(self, resume_text):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.resume_text = resume_text
        

    def clean_history(self, history):
        clean = []
        for m in history:
            clean.append({"role": m["role"], "content": m["content"]})
        return clean
    
   

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            func = globals().get(tool_name)
            result = func(**args) if func else {}
            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        system_prompt = f"You are acting as a user.Extract their name from resume text and refer to them by their name strictly. You are answering questions on user's professional life, \
                    particularly questions related to user's career, background, skills and experience. \
                    Your responsibility is to represent user for interactions on the website as faithfully as possible. \
                    You are given a summary of user's background and which you can use to answer questions. \
                    Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
                    If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
                    If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.resume_text}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as user."
        return system_prompt

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + self.clean_history(history) + [{"role": "user", "content": message}]
        while True:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls
                messages.append(response.choices[0].message)
                messages.extend(self.handle_tool_call(tool_calls))
            else:
                return response.choices[0].message.content

# Shared state to hold current bot
active_bot = gr.State(None)



# Wrapper chat function
def chat_wrapper(message, history, bot):
    if bot is None:
        return "Please upload a resume first."
    return bot.chat(message, history)

# Resume upload handler
def launch_chat(resume_file):
    text = ""
    reader = PdfReader(resume_file.name)
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    bot = ResumeBot(text)
    return bot



# UI
with gr.Blocks() as demo:
    gr.Markdown("## ResumeReviewer")

    resume_upload = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"])
    resume_upload.upload(fn=launch_chat, inputs=[resume_upload], outputs=[active_bot])         

    chatbot = gr.ChatInterface(fn=chat_wrapper, additional_inputs=[active_bot], type="messages")

demo.launch()
