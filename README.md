# Kubernetes Python App with Monitoring (Prometheus & Grafana)

This guide documents the steps to build a Python Flask application, deploy it to Kubernetes using Argo CD, and set up a complete monitoring stack with Prometheus and Grafana.

## Prerequisites
- Docker
- Kubernetes Cluster (Minikube, Docker Desktop, or Cloud Provider)
- `kubectl` CLI
- `helm` CLI

---

## Step 1: Build and Push Docker Image

1. **Build the image**:
   ```bash
   docker build -t tuheen27/k8s-application:v0.1 .
   ```

2. **Push to Docker Hub**:
   ```bash
   docker push tuheen27/k8s-application:v0.1
   ```

---

## Step 2: Deploy Application (Manual Method)

If you want to deploy directly without Argo CD:

```bash
kubectl apply -f k8s/web-app.yml
kubectl apply -f k8s/loadblancer.yml
```

To access the app locally:
```bash
kubectl port-forward svc/my-webapp-service 8080:5000
```
Visit: [http://localhost:8080](http://localhost:8080)

---

## Step 3: Deploy via Argo CD (GitOps Method)

1. **Install Argo CD**:
   ```bash
   kubectl create namespace argo
   kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

2. **Get Initial Password**:
   ```bash
   kubectl -n argo get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

3. **Fix Permissions (Important)**:
   If you see "Permission Denied" errors, patch the ClusterRoleBinding:
   ```bash
   kubectl edit clusterrolebinding argocd-application-controller
   # Change the namespace in the "subjects" section from 'argocd' to 'argo'
   ```

4. **Apply Application Manifest**:
   ```bash
   kubectl apply -f k8s/argo.yml
   ```

---

## Step 4: Setup Monitoring (Prometheus & Grafana)

We use the `kube-prometheus-stack` Helm chart.

1. **Add Helm Repo**:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   ```

2. **Install Stack**:
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

3. **Access Grafana**:
   ```bash
   # Get Admin Password
   kubectl get secrets prometheus-grafana -o jsonpath='{.data.admin-password}' | base64 -d

   # Port Forward
   kubectl port-forward svc/prometheus-grafana 3000:80
   ```
   Visit: [http://localhost:3000](http://localhost:3000) (User: `admin`)

---

## Step 5: Configure Grafana Data Source

By default, Grafana might try to connect to `localhost`. You need to point it to the K8s Service DNS.

1. Go to **Configuration** -> **Data Sources** -> **Prometheus**.
2. Change the **URL** to:
   ```text
   http://prometheus-kube-prometheus-prometheus.default:9090
   ```
3. Click **Save & Test**.

---

## Step 6: Import Dashboard

1. Go to **Dashboards** -> **New** -> **Import**.
2. Paste the JSON provided in the project documentation (or use ID `11074` for a generic Flask dashboard).
3. You should now see metrics for:
   - Requests per second
   - Latency
   - Active Pods

---

## Troubleshooting

- **Connection Refused in Grafana**: Ensure you are using the internal DNS URL (`http://prometheus-kube-prometheus-prometheus.default:9090`) and not `localhost`.
- **Argo CD Sync Failed**: Check the `ClusterRoleBinding` namespace issue mentioned in Step 3.
