FROM python:3.9.7-buster
WORKDIR /data
EXPOSE 8000
COPY ./requirements.txt /data
RUN pip install -r requirements.txt
COPY . /data
CMD python /data/main.py