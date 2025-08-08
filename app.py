from flask import Flask
from prometheus_client import start_http_server, Counter
import random   
import time

app = Flask(__name__)

REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests')

@app.route('/')
def hello_world():
    REQUEST_COUNTER.inc()
    return "Hello, Promethues!"


if __name__ == '__main__':
    start_http_server(8000)  # Start Prometheus metrics server on port 8000
    app.run(host='0.0.0.0', port=5000)  # Start Flask app on port 5000
