import gradio as gr
import subprocess
import os
from .utils.FileHandler import FileHandler
from .userInputHandler import userInputHandler
from .config import INPUT_FILE_PATH
import shutil

chat_history = []
uploaded_file_path = None


def compile_tex_to_pdf(tex_path: str) -> str:
    """Compiles LaTeX file into a PDF and returns PDF path."""
    tex_dir = os.path.dirname(tex_path)
    tex_file = os.path.basename(tex_path)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file],
            cwd=tex_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        pdf_path = os.path.join(tex_dir, tex_file.replace(".tex", ".pdf"))
        return pdf_path if os.path.exists(pdf_path) else None
    except Exception as e:
        print(f"Compilation error: {e}")
        return None


def preview_pdf_iframe(pdf_path: str) -> str:
    """Returns iframe HTML to embed the PDF."""
    if pdf_path and os.path.exists(pdf_path):
        return f"<iframe src='{pdf_path}' width='100%' height='600px' style='border: none; border-radius: 12px;'></iframe>"
    return "<p style='color:red;'>❌ Failed to generate preview</p>"


def on_message(user_message, history):
    return userInputHandler(user_message, history)


import os
from uuid import uuid4


def on_upload(file):
    global uploaded_file_path

    os.makedirs(INPUT_FILE_PATH, exist_ok=True)
    file_extension = os.path.splitext(file.name)[1]
    filename = f"{uuid4().hex}{file_extension}"
    saved_path = os.path.join(INPUT_FILE_PATH, filename)

    # ✅ Safely copy from temp file to permanent path
    shutil.copyfile(file.name, saved_path)

    uploaded_file_path = saved_path

    if uploaded_file_path.endswith(".tex"):
        pdf_path = compile_tex_to_pdf(uploaded_file_path)
        return preview_pdf_iframe(pdf_path)
    elif uploaded_file_path.endswith(".pdf"):
        return preview_pdf_iframe(uploaded_file_path)
    else:
        return "<p style='color:orange;'>Uploaded, but preview not supported.</p>"

def reset_chat():
    return [], ""


with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        background: linear-gradient(to right, #f7f8fc, #ffffff);
        font-family: 'Inter', sans-serif;
    }
    .gradio-container {
        height: 100vh;
        width: 100vw;
        padding: 20px;
        box-sizing: border-box;
        overflow: hidden;
    }
    .gr-box {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px);
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease-in-out;
    }
    .gr-box:hover {
        transform: translateY(-3px);
    }
    .gr-button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-weight: bold;
        transition: transform 0.2s ease-in-out;
    }
    .gr-button:hover {
        transform: scale(1.05);
    }
    .gr-chatbot {
        background: #ffffff;
        border-radius: 12px;
        padding: 10px;
    }
    .gr-textbox textarea {
        font-size: 16px;
        border-radius: 10px;
    }
    .gr-markdown h1 {
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
        margin-top: 0.2rem;
    }
    .gr-markdown h2 {
        font-size: 1rem;
        margin-bottom: 0.4rem;
        margin-top: 0.2rem;
    }
    .gr-markdown {
        margin-bottom: 10px;
    }
    """
) as demo:

    gr.Markdown("# 📄 Resume Assistant (AI-Powered)")
    gr.Markdown("Transform your resume into LaTeX with style and precision — powered by CrewAI 🚀")

    with gr.Row(equal_height=True):
        # Left Panel – Chatbot (30%)
        with gr.Column(scale=3):
            gr.Markdown("### 💬 Chat with ResumeBot")
            chatbot = gr.Chatbot(label="Chat History", show_copy_button=True)

            with gr.Row():
                msg_input = gr.Textbox(
                    label="Type your message",
                    placeholder="e.g., Can you convert this resume to LaTeX?",
                    scale=6
                )
                file_input_inline = gr.File(file_types=[".pdf", ".tex"], label="📎", scale=2)
                send_btn = gr.Button("Send", scale=2)
            clear_btn = gr.Button("Clear Chat", variant="secondary")

        # Right Panel – Preview (70%)
        with gr.Column(scale=7):
            gr.Markdown("### 👀 Resume Preview")
            preview = gr.HTML(label="Live Preview")

    # Button Events
    send_btn.click(on_message, inputs=[msg_input, chatbot], outputs=[chatbot, chatbot])
    msg_input.submit(on_message, inputs=[msg_input, chatbot], outputs=[chatbot, chatbot])
    clear_btn.click(fn=reset_chat, outputs=[chatbot, msg_input])
    file_input_inline.change(fn=on_upload, inputs=file_input_inline, outputs=preview)

    gr.Markdown("---")
    gr.Markdown("© 2025 Resume Assistant · Built with ❤️ using CrewAI and Gradio.")

demo.launch()
