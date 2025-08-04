import os
import shutil
from ..config import INPUT_FILE_PATH
from .ExtractTextInfoFromPDF import ExtractTextInfoFromPDF
from pypdf import PdfReader

class FileHandler:
    def __init__(self, file):
        self.userFile = file
        self.filepath = self.save_uploaded_file()
        self.process_uploaded_file()
        self.buildContext = self.read_pdf_text()

    def save_uploaded_file(self) -> str:
        """Save uploaded file to INPUT_FILE_PATH and return its full path."""
        os.makedirs(INPUT_FILE_PATH, exist_ok=True)
        original_path = self.userFile
        destination_path = os.path.join(INPUT_FILE_PATH, os.path.basename(original_path))

        # Avoid SameFileError
        if os.path.abspath(original_path) != os.path.abspath(destination_path):
            shutil.copyfile(original_path, destination_path)

        return destination_path


    def get_output_file_path(self) -> str:
        """Get processed output path from ExtractTextInfoFromPDF"""
        return ExtractTextInfoFromPDF.create_output_file_path()

    def process_uploaded_file(self):
        """Run Adobe SDK-based processor"""
        #ExtractTextInfoFromPDF(self.filepath)

    def read_pdf_text(self) -> str:
        """Extract raw text from all PDF pages"""
        reader = PdfReader(self.filepath)
        pdf_content = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                pdf_content += content
        return pdf_content
