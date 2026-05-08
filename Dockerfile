FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY . .
# A HF 7860-as portot vár, a FastAPI-t uvicorn-nal indítjuk
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
