FROM python:3.11-bullseye

WORKDIR /app

# Install FFmpeg for video frame extraction
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./ /app

RUN python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

CMD ["python3", "-m", "gunicorn", "-b", "0.0.0.0:8000", "main:app"]
