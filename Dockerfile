FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p outputs/eval_runs
RUN mkdir -p outputs/reports


ENV PYTHONUNBUFFERED=1


CMD ["sh", "-c", "python main.py && python test_compare.py"]