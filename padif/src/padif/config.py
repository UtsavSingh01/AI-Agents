import os

# --- Paths ---
# Root of the src/padif/ directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Input PDF file path
DEFAULT_PDF_FILENAME = "Utsav_Kumar_Resume.pdf"
INPUT_PDF_PATH = os.path.join(BASE_DIR, "wwwroot", DEFAULT_PDF_FILENAME)

# Output folder to save extracted results
OUTPUT_DIR = os.path.join(BASE_DIR, "wwwroot", "output", "ExtractTextInfoFromPDF")
os.makedirs(OUTPUT_DIR, exist_ok=True) 