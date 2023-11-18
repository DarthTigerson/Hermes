FROM python:3.12

WORKDIR /hermes

COPY . /hermes

RUN pip install -r requirements.txt

# Run startup.py if database is not set
RUN test -e hermes.db && python startup.py

CMD ["uvicorn", "main:app", "--reload"]