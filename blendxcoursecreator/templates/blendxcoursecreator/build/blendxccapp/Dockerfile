# syntax=docker/dockerfile:1.4
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && \
  apt upgrade -y && \
  apt install -y \
    locales \
    git \
    python3-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    && \
  sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
  locale-gen
ENV LC_ALL=en_US.UTF-8

###### Git-clone BlendxCCApp repo ######
ARG APP_USER_ID=1000
RUN useradd --home-dir /app --create-home --shell /bin/bash --uid ${APP_USER_ID} app

# Run as root to set permissions
USER root
RUN git clone {{ BLENDXCCAPP_REPOSITORY }} --branch {{ BLENDXCCAPP_REPOSITORY_VERSION }} --depth 1 /app/blendxccapp
RUN chown -R app:app /app/blendxccapp
RUN chmod +x /app/blendxccapp/app/main.py

USER ${APP_USER_ID}
WORKDIR /app/blendxccapp

# Setup empty config file for production settings
RUN echo "{}" > /app/config.yml
ENV BLENDXCCAPP_CFG=/app/config.yml

###### Install python venv ######
RUN python -m venv /app/venv
ENV PATH=/app/venv/bin:${PATH}
RUN --mount=type=cache,target=/app/.cache/pip,sharing=shared pip install setuptools==69.2.0 pip==24.0 wheel==0.43.0
RUN --mount=type=cache,target=/app/.cache/pip,sharing=shared pip install -r requirements.txt

# Create data directories
RUN mkdir -p /app/data /app/temp_courses /app/course_exports

# Run production server
EXPOSE 8000
CMD ["gunicorn", "--workers=2", "--name", "blendxccapp", "--bind=0.0.0.0:8000", "--max-requests=1000", "app.main:app"]
