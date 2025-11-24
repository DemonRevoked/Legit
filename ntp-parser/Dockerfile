FROM python:3.9-slim

WORKDIR /app

RUN pip install pymongo

COPY parse_ntplogs_loop.py .

CMD ["python", "-u", "parse_ntplogs_loop.py"]