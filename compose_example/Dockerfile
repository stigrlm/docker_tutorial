FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3-pip

WORKDIR /app/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python3", "app.py"]
