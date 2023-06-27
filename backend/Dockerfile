FROM python:3.11-slim-bookworm

WORKDIR /var/apps/popchat

COPY . .

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]