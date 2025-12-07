import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    # Demonstrates reading from environment variables (K8s ConfigMaps)
    app_env = os.getenv('APP_ENV', 'Development')
    return jsonify({
        "message": "Welcome to the K8s Demo App",
        "environment": app_env,
        "hostname": socket.gethostname()  # Shows which pod is serving the request
    })

@app.route('/health')
def health():
    # Used for Kubernetes Liveness/Readiness probes
    return jsonify({"status": "healthy"}), 200

@app.route('/ready')
def ready():
    # Simulate a readiness check (e.g., database connection)
    return jsonify({"status": "ready"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)