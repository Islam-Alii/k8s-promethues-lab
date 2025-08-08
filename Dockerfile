FROM python:3.10-slim
WORKDIR /app
COPY . . 
RUN pip install --upgrade pip
RUN pip install -r requirments.txt
EXPOSE 5000 8000
CMD ["python", "app.py"]