FROM python:3.9-buster

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY business.py /app.py

EXPOSE 5000

WORKDIR /

ENTRYPOINT ["python", "/app.py"]
