FROM python:3.11-slim
WORKDIR /app
# A standard uvicorn csomag kell a megbízható hálózati kezeléshez
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"
COPY . .
# HF Port 7860 kényszerítése
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
