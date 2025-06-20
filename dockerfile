FROM python:3.12-slim as requirements-stage

WORKDIR /tmp
RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY . /tmp
RUN poetry export -f requirements.txt --output requirements.txt 

FROM python:3.12-slim

WORKDIR /app
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

# 安裝所需的系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-noto-cjk \
    texlive-latex-extra \
    texlive-fonts-extra \
    ffmpeg \
    build-essential \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    dvisvgm \
    #xvfb \
    #xauth \
    #x11-utils \
    #x11-xserver-utils \
    #libgl1-mesa-dev \
    #libegl1-mesa-dev \
    #libgles2-mesa-dev \
    #libosmesa6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/*

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir manim edge-tts

COPY . /app
COPY . /data

EXPOSE 3000
CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "3000", "--factory"]