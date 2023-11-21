FROM python:3.12-slim

WORKDIR /hermes

COPY . /hermes

RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod +x ./run.sh

CMD ["./run.sh"]