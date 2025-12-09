# End-to-End DevOps: Python Microservice with GitOps & Observability

This repository demonstrates a complete DevOps lifecycle for a Python Flask microservice: containerized with Docker, deployed on Kubernetes, managed with Argo CD (GitOps), and monitored via Prometheus + Grafana.

## Project Highlights (resume-friendly)
- Containerization: Slim Python 3.9 image, pinned dependencies, port exposed for Flask.
- Kubernetes: Deployment with 3 replicas, Service (LoadBalancer), readiness/health endpoints, Prometheus scrape annotations.
- GitOps: Argo CD Application pointing to this repo for automated sync/self-heal.
- Observability: Prometheus scraping custom app metrics; Grafana dashboards for RPS, latency, pod health.

## Project Structure
```
application/app.py         # Flask app with health/ready endpoints and custom metrics
requirements.txt           # flask, prometheus-flask-exporter
dockerfile                 # Builds the image and runs application/app.py
k8s/web-app.yml            # Deployment (3 replicas) with scrape annotations
k8s/loadblancer.yml        # Service (LoadBalancer) exposing port 5000
k8s/argo.yml               # Argo CD Application manifest (GitOps)
```

## Quickstart (local build and run)
```bash
docker build -t tuheen27/k8s-application:v0.1 .
docker run -p 5000:5000 tuheen27/k8s-application:v0.1
# Visit http://localhost:5000
```

## Deploy to Kubernetes (manual)
```bash
kubectl apply -f k8s/web-app.yml
kubectl apply -f k8s/loadblancer.yml
kubectl port-forward svc/my-webapp-service 8080:5000
# Visit http://localhost:8080
```

## Deploy with Argo CD (GitOps)
```bash
kubectl create namespace argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argo get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
kubectl apply -f k8s/argo.yml
```
> If you hit permission errors, ensure the ClusterRoleBinding subject namespace is `argo`.

## Install Monitoring (Prometheus + Grafana)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl get secrets prometheus-grafana -o jsonpath='{.data.admin-password}' | base64 -d
kubectl port-forward svc/prometheus-grafana 3000:80
# Visit http://localhost:3000 (user: admin)
```

## Configure Grafana Data Source
Set the Prometheus URL to the in-cluster service:
```
http://prometheus-kube-prometheus-prometheus.default:9090
```
Save & Test, then import dashboard ID `11074` or your custom JSON.

## Useful PromQL Snippets
- Pods up: `up{app="my-webapp"}`
- RPS: `sum(rate(flask_http_request_total[2m])) by (status)`
- Avg latency: `sum(rate(flask_http_request_duration_seconds_sum[2m])) / sum(rate(flask_http_request_duration_seconds_count[2m]))`

## Troubleshooting
- Grafana “connection refused”: ensure you are not using `localhost`; use the service DNS above.
- Argo CD sync issues: verify `targetRevision` and ClusterRoleBinding namespace.

## Future Improvements (talking points)
- Add CI pipeline (lint/test/build/push) with GitHub Actions.
- Add Horizontal Pod Autoscaler driven by CPU and request rate.
- Add Ingress with TLS termination.
