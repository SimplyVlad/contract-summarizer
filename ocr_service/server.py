import sys
import datetime
import pytesseract
import shutil
import os
from typing import List
import base64
from tempfile import NamedTemporaryFile

try:
 from PIL import Image
except ImportError:
 import Image
from pdf2image import convert_from_path
from PIL import Image
import tesserocr


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.logger import logger
from pydantic import BaseSettings

from pdf_parser import parse_pdf_language


##TODO adjust those when we deploy
ocr_tesseractdata = '/usr/share/tesseract-ocr/5/tessdata/'
pdf_safe_directory = "pdfs_dir"
pdf_safe_subdir = str(round(datetime.datetime.now().timestamp()))
if not os.path.exists(os.path.join(pdf_safe_directory, pdf_safe_subdir)):
   os.makedirs(os.path.join(pdf_safe_directory, pdf_safe_subdir))








app = FastAPI(title="Contract read endpoint", description="Used to read digitally born and scanned pdf documents", version="1.0")




#TODO add initialization in a central way --- blocker: how to dynamically reload the data language
@app.on_event("startup")
async def initialize_service():
    global api
    #TODO remove hard German dependency
    api = tesserocr.PyTessBaseAPI(path=ocr_tesseractdata, lang='deu')
    print("api has been initialized")

def read_PDF_with_OCR(pdf_file_path, lang='deu'):
    images = convert_from_path(pdf_file_path, 600)
    text_total = []
    for index, image in enumerate(images):
        extracted_text = pytesseract.image_to_string(image, lang='deu')
        text_total.append(extracted_text)
    return " ".join(text_total)

def read_PDF_with_OCR_API(pdf_file_path, lang='deu'):
    global api
    images = convert_from_path(pdf_file_path, 600)
    text_total = []
    for index, image in enumerate(images):
       api.SetImage(image)
       extracted_text = api.GetUTF8Text()
       text_total.append(extracted_text)
    return " ".join(text_total)


@app.post("/get_text", tags=["transformations"])
def upload(filename: str = Form(...), filedata: str = Form(...)):
    pdf_as_bytes = str.encode(filedata)
    file_decoded = base64.b64decode(pdf_as_bytes)
    try:
        with NamedTemporaryFile(dir='.', suffix='.pdf') as f:
            f.write(file_decoded)
            pdf_text = read_PDF_with_OCR_API(f.name)
    except Exception as e:
        return {"result": "Unsuccessful read of the file" + "\n" + str(e)}
    return {"result": pdf_text}


@app.post("/get_text_pdf", tags=["transformations"])
def upload2(filename: str = Form(...), filedata: str = Form(...)):
    pdf_as_bytes = str.encode(filedata)
    file_decoded = base64.b64decode(pdf_as_bytes)
    try:
        with NamedTemporaryFile(dir='.', suffix='.pdf') as f:
            f.write(file_decoded)
            pdf_text = parse_pdf_language(f.name, 0)
            print(pdf_text)
    except Exception as e:
        return {"result": "Unsuccessful read of the file" + "\n" + e}
    return {"result": pdf_text}