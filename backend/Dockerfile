FROM python:3.11-slim

WORKDIR /app

COPY ./backend /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["python", "run.py"]
