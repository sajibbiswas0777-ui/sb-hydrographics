FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN python db.py
EXPOSE 5000
CMD ["python", "server.py"]
