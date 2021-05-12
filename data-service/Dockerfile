FROM python:3.9-buster

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY data.py /app.py

EXPOSE 5000

WORKDIR /

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
