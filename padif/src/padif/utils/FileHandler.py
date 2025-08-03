import os
import shutil
from ..config import INPUT_FILE_PATH
from .ExtractTextInfoFromPDF import ExtractTextInfoFromPDF
from pypdf import PdfReader

class FileHandler:    
    def __init__(self, file):
        self.filepath=self.save_uploaded_file()
        self.userFile=file
        self.process_uploaded_file()
        self.buildContext=self.pdfReader()
    
    def save_uploaded_file(self) -> str:
        os.makedirs(INPUT_FILE_PATH, exist_ok=True)
        shutil.copy(self.userFile, INPUT_FILE_PATH)
        path=os.path.join(INPUT_FILE_PATH,self.userFile.name)
        return path
    
    def get_output_file_path()->str:
        return ExtractTextInfoFromPDF.create_output_file_path()

    def process_uploaded_file(self) ->str:
        ExtractTextInfoFromPDF(self.filepath)

    def pdfReader(self):   
        reader = PdfReader(self.filepath)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                pdfContent += content
            return pdfContent
