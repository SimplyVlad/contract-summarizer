import os
import pypdfium2 as pdfium
from nltk.tokenize import sent_tokenize
import re
from docx import Document
import json





def remove_non_ascii(string):
    return "".join(
        char
        for char in string
        if ord(char) < 128 or (ord(char) in [196, 214, 220, 228, 246, 252, 223])
    )




def parse_pdf_language(file_path, n_sent, language="german", token_limit=250):
    file_splits = []
    file_splits_vanilla = []
    try:
        pdf = pdfium.PdfDocument(file_path)
    except:
        print("Problem with the file")
        return []
    for page_num, page in enumerate(pdf):
        textpage = page.get_textpage()
        text_all = textpage.get_text_range()
        text_all = remove_non_ascii(text_all)
        text_sent_vanilla = sent_tokenize(text_all)
        text_sent = [
            str(sent).replace("\r\n", " ")
            for sent in text_sent_vanilla]
        all_text = " ".join(text_sent)
        all_text_vanilla = " ".join(text_sent_vanilla)
        file_splits.append(all_text)
        file_splits_vanilla.append(all_text_vanilla)
    full_text = " ".join(file_splits)
    full_text_vanilla = " ".join(file_splits_vanilla)
    return full_text
