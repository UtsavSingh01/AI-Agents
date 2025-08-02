import gradio as gr

# Simple function to simulate chat reply
def chatbot_response(message, history):
    history = history or []
    response = f"You said: {message}"
    history.append((message, response))
    return history, history

# Handle uploaded document
def handle_upload(file):
    if file is None:
        return "No file uploaded."
    return f"Uploaded file: {file.name}"

with gr.Blocks() as demo:
    gr.Markdown("## 📄 Chatbot with Document Upload")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Assistant")
            msg = gr.Textbox(label="Enter message", placeholder="Ask me anything...")
            submit_btn = gr.Button("Send")
            clear_btn = gr.Button("Clear")

        with gr.Column(scale=1):
            upload = gr.File(label="Upload your document", file_types=[".pdf", ".docx", ".txt"])
            upload_output = gr.Textbox(label="Upload status", interactive=False)

    submit_btn.click(fn=chatbot_response, inputs=[msg, chatbot], outputs=[chatbot, chatbot])
    msg.submit(fn=chatbot_response, inputs=[msg, chatbot], outputs=[chatbot, chatbot])
    clear_btn.click(lambda: ([], ""), None, [chatbot, msg])
    upload.change(fn=handle_upload, inputs=upload, outputs=upload_output)

demo.launch()
