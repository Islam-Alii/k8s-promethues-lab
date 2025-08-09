# Python App with Prometheus + Grafana on Local Kubernetes

this guide sets up a hands-on lab to deploy a Python app that exposes Prometheus metrics, scrapes them via Prometheus, and visualizes them in Grafana — all running on a local Kubernetes cluster using `kind`.

---

## 🧰 Prerequisites

- Docker
- `kind` (Kubernetes in Docker)
- `kubectl`
- `helm`
- Python 3.x

---

## 🚀 Steps

### 1. Create Local Kubernetes Cluster

```
kind create cluster --name prom-demo
```

---

### 2. Install Prometheus and Grafana with kube-prometheus-stack

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

---

### 3. Create Your Python App with Prometheus Client

**app/main.py**

```python
from flask import Flask
from prometheus_client import start_http_server, Counter
import time

app = Flask(__name__)
REQUEST_COUNTER = Counter("python_app_requests_total", "Total requests")

@app.route("/")
def hello():
    REQUEST_COUNTER.inc()
    return "Hello from Python!"

if __name__ == "__main__":
    start_http_server(8000)  # Prometheus metrics on :8000
    app.run(host="0.0.0.0", port=5000)
```

**Dockerfile**

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask prometheus_client
CMD ["python", "main.py"]
```

**Build & Push to Docker** (use DockerHub or local)

```
docker build -t python-metrics-app .
kind load docker-image python-metrics-app --name prom-demo
```

---

### 4. Kubernetes YAMLs

**Deployment + Service**

```yaml
# k8s/python-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-app
  template:
    metadata:
      labels:
        app: python-app
    spec:
      containers:
      - name: app
        image: python-metrics-app
        ports:
        - containerPort: 5000
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: python-app
  labels:
    app: python-app
spec:
  selector:
    app: python-app
  ports:
    - name: web
      port: 5000
      targetPort: 5000
    - name: metrics
      port: 8000
      targetPort: 8000
```

Apply:
```
kubectl apply -f k8s/python-app.yaml
```

---

### 5. Create a ServiceMonitor

```yaml
# k8s/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: python-app
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: python-app
  namespaceSelector:
    matchNames:
      - default
  endpoints:
    - port: metrics
      interval: 15s
```

Apply:
```
kubectl apply -f k8s/service-monitor.yaml
```

---

### 6. Access Prometheus and Grafana

#### Port-forward Prometheus
```
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090
```

Visit: http://localhost:9090/targets — confirm your Python app is listed

#### Port-forward Grafana
```
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

Login to Grafana at http://localhost:3000 (user: admin, password: prom-operator)

---

### 7. Visualize in Grafana

- Add new dashboard > Add new panel
- Use query: `python_app_requests_total`
- Visualize request growth over time

---

## ✅ Troubleshooting

- If metrics are not visible in Prometheus:
  - Check `/metrics` is exposed correctly via curl inside cluster
  - Ensure Service port name matches ServiceMonitor endpoint `port:`
  - Ensure ServiceMonitor has correct label and namespace

---

## 🧹 Cleanup

```
kind delete cluster --name prom-demo
```

---

## ✅ Result

You now have a local Prometheus-Grafana lab monitoring your Python app in Kubernetes!
