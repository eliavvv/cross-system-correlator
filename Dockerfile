FROM python:3.11-slim
WORKDIR /app
COPY correlator correlator
COPY sample-logs sample-logs
COPY requirements.txt README.md ./
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "-m", "correlator.cli"]
CMD ["--help"]
