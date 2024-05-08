FROM python:3.11
ENV PYTHONBURRERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt