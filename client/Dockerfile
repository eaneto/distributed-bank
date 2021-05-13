FROM python:3.9-buster

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY client.py /client.py

WORKDIR /

ENTRYPOINT ["python", "/client.py"]
