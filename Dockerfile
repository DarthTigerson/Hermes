FROM python:3.12

WORKDIR /hermes

COPY . /hermes

RUN pip install -r requirements.txt

CMD ["./run.sh"]