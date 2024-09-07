ARG BASE_CONTAINER=tiangolo/uvicorn-gunicorn:python3.9
FROM $BASE_CONTAINER

RUN mkdir /ocr_service

USER root
RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    sudo \
    tesseract-ocr \
    tesseract-ocr-deu \
    poppler-utils \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
 && apt-get clean && rm -rf /var/lib/apt/lists/*



CMD ["tesseract", "--version"]
CMD ["tesseract", "--list-langs"]

USER $NB_UID

WORKDIR /ocr_service

COPY requirements.txt /ocr_service

RUN pip install -r requirements.txt

	
COPY . /ocr_service

EXPOSE 8000

RUN python -m nltk.downloader punkt
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]