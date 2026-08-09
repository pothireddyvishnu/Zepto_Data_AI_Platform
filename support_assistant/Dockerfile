FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python data_ingestion.py

ENV MOCK_LLM=1

EXPOSE 7860

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860" ]