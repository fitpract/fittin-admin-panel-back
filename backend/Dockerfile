FROM python:3.12

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE = 1\
	PYTHONNONBUFFERED = 1

COPY requirements.txt /backend

RUN pip install -r requirements.txt

COPY . /backend