import gradio as gr
from .utils.FileHandler import FileHandler

from .userInputHandler import userInputHandler

chat_history = []

def on_message(user_message, history):
    return userInputHandler(user_message, history)
    

def on_upload(file):
    saved_path = FileHandler(file)
    return f"✅ File saved to: {saved_path}"

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Resume Assistant Chatbot (CrewAI + Gradio)")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot()
            msg_input = gr.Textbox(label="Ask a question", placeholder="e.g., Can you convert this resume to LaTeX?")
            send_btn = gr.Button("Send")
            clear_btn = gr.Button("Clear Chat")

        with gr.Column(scale=1):
            upload = gr.File(label="Upload your resume", file_types=[".pdf", ".docx"])
            upload_status = gr.Textbox(label="Upload result", interactive=False)

    send_btn.click(on_message, inputs=[msg_input, chatbot], outputs=[chatbot, chatbot])
    msg_input.submit(on_message, inputs=[msg_input, chatbot], outputs=[chatbot, chatbot])
    clear_btn.click(lambda: ([], ""), None, [chatbot, msg_input])
    upload.change(on_upload, inputs=upload, outputs=upload_status)

demo.launch()
