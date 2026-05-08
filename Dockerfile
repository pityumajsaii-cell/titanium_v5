FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# A Hugging Face a 7860-as portot várja!
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "wsgi:app"]
