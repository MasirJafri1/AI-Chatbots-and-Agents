FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV PYTHONUNBUFFERED=1


RUN rm -f /etc/apt/sources.list.d/yarn.list && \
    apt-get update --allow-releaseinfo-change && \
    apt-get install -y curl poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip