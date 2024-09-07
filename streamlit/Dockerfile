FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# put the values of the openai keys here or in the default values in the contract_summarizer.py reading part
#ENV OI_ORG
#ENV OI_KEY

CMD ["streamlit", "run", "contract_summarizer.py", "--server.enableCORS", "false", "--browser.serverAddress", "0.0.0.0", "--browser.gatherUsageStats", "false", "--server.port", "8501"]