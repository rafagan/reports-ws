FROM ubuntu:latest

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

COPY ./requirements.txt .

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app
EXPOSE 5000
WORKDIR /app

ENV DEBUG="false"

ENTRYPOINT ["python3"]
CMD ["/app/server/api.py"]