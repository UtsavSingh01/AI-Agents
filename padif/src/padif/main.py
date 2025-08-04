import gradio as gr
import subprocess
import os
from uuid import uuid4
import shutil
from .utils.FileHandler import FileHandler
from .userInputHandler import userInputHandler
from .config import INPUT_FILE_PATH

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
    """Embed PDF preview using base64-encoded data URI inside iframe."""
    import base64

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            encoded = base64.b64encode(pdf_bytes).decode("utf-8")
            return f"""
            <iframe 
                src="data:application/pdf;base64,{encoded}" 
                width="100%" 
                height="600px" 
                style="border: none; border-radius: 12px;">
            </iframe>
            """
    return "<p style='color:red;'>❌ PDF preview failed — file not found</p>"


def on_message(user_message, history):
    # Get bot response using your custom handler
    bot_response = userInputHandler(user_message, history)
    
    # Update chat history
    updated_history = history + [(user_message, bot_response)]
    
    # Return updated history and clear input
    return updated_history, ""

def on_upload(file):
    global uploaded_file_path

    # Create input directory if needed
    os.makedirs(INPUT_FILE_PATH, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.name)[1]
    filename = f"{uuid4().hex}{file_extension}"
    saved_path = os.path.join(INPUT_FILE_PATH, filename)

    # Copy file to permanent storage
    shutil.copyfile(file.name, saved_path)
    uploaded_file_path = saved_path

    # Handle different file types
    if uploaded_file_path.endswith(".tex"):
        with gr.Blocks(analytics_enabled=False):
            with gr.Row():
                loading = gr.Markdown(
                    "<div style='text-align:center; padding: 40px;'>"
                    "🔄 Compiling LaTeX document..."
                    "<div class='spinner'></div>"
                    "</div>"
                )
        yield loading
        
        pdf_path = compile_tex_to_pdf(uploaded_file_path)
        if pdf_path:
            yield preview_pdf_iframe(pdf_path)
        else:
            yield "<div class='error-box'>❌ LaTeX compilation failed</div>"
    elif uploaded_file_path.endswith(".pdf"):
        yield preview_pdf_iframe(uploaded_file_path)
    else:
        yield f"<div class='info-box'>✅ Uploaded {file_extension} file<br>Preview not supported.</div>"

def reset_chat():
    global chat_history
    chat_history = []
    return [], ""

# Modern theme configuration
theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="indigo",
    font=[gr.themes.GoogleFont("Inter")]
).set(
    body_background_fill="linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%)",
    body_background_fill_dark="linear-gradient(135deg, #0f0c29 0%, #302b63 100%)",
    button_primary_background_fill="linear-gradient(90deg, #8e2de2 0%, #4a00e0 100%)",
    button_primary_background_fill_hover="linear-gradient(90deg, #9d4edd 0%, #5a2be0 100%)",
    button_primary_text_color="#ffffff",
    button_primary_border_color="#4a00e0",
    button_secondary_background_fill="#ffffff",
    button_secondary_text_color="#4a00e0",
    block_background_fill="#ffffff",
    block_border_color="#e0e0e0",
    block_label_background_fill="#f0f2f6",
    block_title_text_color="#4a00e0",
    block_label_text_color="#5c5c5c",
    input_background_fill="#f9fafc",
    input_border_color="#e0e0e0",
    input_border_color_focus="#8e2de2",
    input_shadow_focus="0 0 0 2px rgba(142, 45, 226, 0.2)",
    shadow_spread="6px",
    shadow_drop="0 10px 20px rgba(0,0,0,0.05)"
)

with gr.Blocks(
    theme=theme,
    css="""
    :root {
        --primary-gradient: linear-gradient(90deg, #8e2de2 0%, #4a00e0 100%);
        --border-radius-xl: 20px;
        --shadow-lg: 0 10px 30px rgba(0,0,0,0.08);
    }
    .gradio-container {
        font-family: 'Inter', sans-serif;
        padding: 20px;
        height: 100vh;
        box-sizing: border-box;
        background-attachment: fixed;
    }
    .header {
        text-align: center;
        margin-bottom: 30px !important;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        padding: 10px;
    }
    .gr-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius-xl) !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s ease;
        padding: 25px;
        border: none !important;
    }
    .gr-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12) !important;
    }
    .gr-button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(142, 45, 226, 0.3) !important;
    }
    .gr-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 20px rgba(142, 45, 226, 0.4) !important;
    }
    .gr-chatbot {
        border-radius: var(--border-radius-xl);
        padding: 20px;
        background: white;
        height: 520px;
        border: 1px solid #eee !important;
        margin-bottom: 20px;
    }
    .chat-message {
        padding: 16px 20px;
        border-radius: 16px !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    .user-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%) !important;
        border: 1px solid #e0e0e0 !important;
    }
    .bot-message {
        background: linear-gradient(135deg, #f0f2f6 0%, #e6e9ff 100%) !important;
        border: 1px solid #e0e0ff !important;
    }
    .gr-textbox {
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 16px;
        border: 1px solid #e0e0e0 !important;
        margin-bottom: 15px;
    }
    .preview-panel {
        height: 700px;
        overflow: hidden;
        border-radius: var(--border-radius-xl);
        box-shadow: var(--shadow-lg);
        background: white;
        padding: 20px;
    }
    .chat-panel {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
        border: 1px solid #c2e0ff;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: #4a00e0;
        font-size: 18px;
        margin: 20px 0;
    }
    .error-box {
        background: linear-gradient(135deg, #fff0f0 0%, #ffe6e6 100%);
        border: 1px solid #ffc2c2;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: #e00000;
        font-size: 18px;
        margin: 20px 0;
    }
    .spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        margin: 20px auto;
        border: 4px solid rgba(142, 45, 226, 0.2);
        border-radius: 50%;
        border-top: 4px solid #8e2de2;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .upload-btn {
        background: var(--primary-gradient) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(142, 45, 226, 0.3) !important;
        margin-right: 15px;
    }
    .clear-btn {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 65, 108, 0.3) !important;
    }
    .clear-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 20px rgba(255, 65, 108, 0.4) !important;
    }
    .file-info {
        font-size: 14px;
        color: #666;
        text-align: center;
        margin-top: 15px;
        padding: 10px;
    }
    footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.9rem;
        margin-top: 20px;
        border-top: 1px solid #eee;
    }
    .gr-tabs {
        border-radius: var(--border-radius-xl);
        overflow: hidden;
    }
    .send-icon {
        background: var(--primary-gradient) !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100%;
    }
    .input-row {
        margin-bottom: 20px !important;
    }
    .button-row {
        margin-top: 15px !important;
    }
    .section-title {
        margin-bottom: 15px !important;
        font-weight: 600;
    }
    .preview-container {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .preview-header {
        margin-bottom: 15px;
    }
    .preview-content {
        flex-grow: 1;
        min-height: 600px;
    }
    """
) as demo:

    gr.Markdown("# 📄 ResumeCraft AI", elem_classes="header")
    gr.Markdown("Transform your resume into LaTeX with style and precision — powered by CrewAI 🚀", 
                elem_id="subheader")

    with gr.Row(equal_height=True):
        # Left Panel - Chatbot (30%)
        with gr.Column(scale=3, min_width=350, elem_classes="chat-panel"):
            gr.Markdown("### 💬 Chat with ResumeBot", elem_classes="section-title")
            
            # Chat history with increased height
            chatbot = gr.Chatbot(
                value=chat_history,
                bubble_full_width=False,
                show_label=False,
                height=520,
                avatar_images=(
                    "https://i.imgur.com/7TSaSlB.png",  # User avatar
                    "https://i.imgur.com/7TSaSlB.png"   # Bot avatar
                )
            )
            
            # Input row with better spacing
            with gr.Row(elem_classes="input-row"):
                msg_input = gr.Textbox(
                    placeholder="Ask to convert, edit, or enhance your resume...",
                    show_label=False,
                    container=False,
                    scale=6,
                    autofocus=True
                )
                send_btn = gr.Button("➤", elem_classes="send-icon", scale=1)
            
            # Button row with more vertical space
            with gr.Row(elem_classes="button-row"):
                file_input_inline = gr.UploadButton(
                    "📁 Upload Resume",
                    file_types=[".pdf", ".tex"],
                    scale=4,
                    elem_classes="upload-btn"
                )
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", scale=2, elem_classes="clear-btn")
            
            gr.Markdown("_Supported formats: PDF, LaTeX (.tex)_", elem_classes="file-info")

        # Right Panel - Preview (70%)
        with gr.Column(scale=7, elem_classes="preview-panel"):
            with gr.Column(elem_classes="preview-container"):
                gr.Markdown("### 👀 Resume Preview", elem_classes="preview-header section-title")
                preview = gr.HTML(
                    value="<div class='info-box' style='height: 600px; display: flex; flex-direction: column; justify-content: center;'>"
                          "<h3 style='margin-top: 0;'>Welcome to ResumeCraft AI</h3>"
                          "<p>Upload your resume to get started:</p>"
                          "<div style='margin: 20px 0;'>"
                          "<p>• PDF ➔ LaTeX conversion</p>"
                          "<p>• Formatting enhancements</p>"
                          "<p>• Expert suggestions</p>"
                          "<p>• Real-time preview</p>"
                          "</div>"
                          "<div style='margin-top: 20px; padding: 15px; background: rgba(142, 45, 226, 0.1); border-radius: 12px;'>"
                          "<p>⬆️ Use the 'Upload Resume' button to begin</p>"
                          "</div>"
                          "</div>",
                    elem_classes="preview-content"
                )

    # Event handling
    send_btn.click(
        on_message, 
        inputs=[msg_input, chatbot], 
        outputs=[chatbot, msg_input],
        api_name="send_message"
    )
    
    msg_input.submit(
        on_message, 
        inputs=[msg_input, chatbot], 
        outputs=[chatbot, msg_input],
        api_name="submit_message"
    )
    
    clear_btn.click(
        fn=reset_chat, 
        outputs=[chatbot, msg_input],
        api_name="clear_chat"
    )
    
    file_input_inline.upload(
        fn=on_upload, 
        inputs=file_input_inline, 
        outputs=preview,
        api_name="upload_file"
    )

    gr.Markdown("---")
    gr.Markdown("© 2025 ResumeCraft AI · Built with ❤️ using CrewAI and Gradio")

demo.launch()