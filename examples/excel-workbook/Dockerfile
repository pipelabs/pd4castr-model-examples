FROM debian:12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libreoffice-calc-nogui python3 python3-openpyxl python3-requests \
    && rm -rf /var/lib/apt/lists/*

# LibreOffice needs a writable home for its user profile.
ENV HOME=/tmp

WORKDIR /app

COPY model/ ./model/

CMD [ "python3", "model/main.py" ]
