FROM python:3.6

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get -y install binutils libproj-dev gdal-bin postgresql-client libevent-dev
RUN apt-get clean
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN mkdir -p /code/public/media
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN ./manage.py collectstatic --noinput

EXPOSE 8000
