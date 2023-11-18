FROM python:3.12

WORKDIR /hermes

COPY . /hermes

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["./run.sh"]