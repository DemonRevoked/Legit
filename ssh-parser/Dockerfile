FROM python:3.10-slim
WORKDIR /app
RUN pip install pymongo
COPY parse_ttylogs_loop.py .
CMD ["python", "parse_ttylogs_loop.py"]
