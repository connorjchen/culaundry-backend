FROM python:latest

RUN mkdir usr/app
WORKDIR usr/app

COPY . . 

RUN pip install -r requirements.txt
RUN pip install requests

CMD python app.py