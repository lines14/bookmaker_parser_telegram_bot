FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER root

RUN apt-get update && apt-get upgrade -y && apt-get install -y gnupg2 wget
RUN wget -O /etc/apt/keyrings/google-chrome.asc https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get -y install google-chrome-stable locales

RUN python3 -m venv /app/myenv
ENV PATH="/app/myenv/bin:$PATH"

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt --use-pep517

RUN sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG ru_RU.UTF-8  
ENV LC_ALL ru_RU.UTF-8

COPY . .

EXPOSE 2226

ENTRYPOINT ["python3", "-u", "bookmaker_parser_bot.py"]
