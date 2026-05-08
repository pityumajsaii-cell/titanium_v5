FROM alpine:latest
RUN apk add --no-cache bash curl jq
COPY hunter.sh /app/hunter.sh
WORKDIR /app
RUN chmod +x hunter.sh
CMD ["./hunter.sh"]
