FROM python:3.9.7-buster
WORKDIR /data
EXPOSE 8000
COPY ./admin_panel/requirements.txt /data
RUN pip install -r requirements.txt
COPY ./admin_panel /data
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000