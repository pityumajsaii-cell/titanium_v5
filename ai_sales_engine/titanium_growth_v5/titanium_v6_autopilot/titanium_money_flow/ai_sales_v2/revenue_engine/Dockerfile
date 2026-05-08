FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg curl jq bash
RUN pip install moviepy google-api-python-client google-auth-oauthlib
COPY . /app
WORKDIR /app
RUN chmod +x hunter.sh
CMD ["./hunter.sh"]
