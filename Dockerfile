FROM python:3.10-alpine as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade

RUN apk add --no-cache build-base gcc musl-dev python3-dev libffi-dev libxml2-dev libxslt-dev

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

RUN python3 -m venv /app/myenv
ENV PATH="/app/myenv/bin:$PATH"

RUN pip install --upgrade pip

FROM python:3.10-alpine

WORKDIR /app

COPY --from=builder /app/myenv /app/myenv

ENV PATH="/app/myenv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt --use-pep517

COPY . .

EXPOSE 2226

ENTRYPOINT ["python3", "bookmaker_parser_bot.py"]