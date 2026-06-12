# PL Stats Platform — Runbook

Operational commands for managing the PL Stats AI platform on Azure.

---

## Quick reference

| Task | Command |
|---|---|
| Start cluster | `az aks start --name plstats-aks --resource-group pl-stats-rg` |
| Stop cluster | `az aks stop --name plstats-aks --resource-group pl-stats-rg` |
| Check cluster state | `az aks show --name plstats-aks --resource-group pl-stats-rg --query powerState` |
| Check pods | `kubectl get pods` |
| Check live app | `http://4.147.108.223` |
| Check API health | `http://4.147.108.223/api/health` |

---

## 1. Daily operations

### Start the platform (before a demo or interview)

```bash
# Step 1 — Start the AKS cluster (takes 3-5 minutes)
az aks start --name plstats-aks --resource-group pl-stats-rg

# Step 2 — Connect kubectl to the cluster
az aks get-credentials --resource-group pl-stats-rg --name plstats-aks

# Step 3 — Verify node is ready
kubectl get nodes
# Expected: STATUS = Ready

# Step 4 — Verify pods are running
kubectl get pods
# Expected: both pl-stats-agent and pl-stats-frontend = Running

# Step 5 — Open the app
open http://4.147.108.223
```

### Stop the platform (after demo to save cost)

```bash
az aks stop --name plstats-aks --resource-group pl-stats-rg
```

### Check cluster state

```bash
az aks show \
  --name plstats-aks \
  --resource-group pl-stats-rg \
  --query powerState
# Returns: {"code": "Running"} or {"code": "Stopped"}
```

---

## 2. Pod management

### Check pod status

```bash
kubectl get pods
kubectl get pods -w   # watch live updates
```

### Check pod logs

```bash
# Agent logs
kubectl logs -l app=pl-stats-agent --tail=50

# Frontend logs
kubectl logs -l app=pl-stats-frontend --tail=50

# Follow logs in real time
kubectl logs -l app=pl-stats-agent --tail=50 --follow

# Logs from previous crashed pod
kubectl logs -l app=pl-stats-agent --previous
```

### Restart pods

```bash
kubectl rollout restart deployment pl-stats-agent
kubectl rollout restart deployment pl-stats-frontend
```

### Scale pods up/down

```bash
# Scale down (stop containers but keep cluster running)
kubectl scale deployment pl-stats-agent --replicas=0
kubectl scale deployment pl-stats-frontend --replicas=0

# Scale back up
kubectl scale deployment pl-stats-agent --replicas=1
kubectl scale deployment pl-stats-frontend --replicas=1
```

### Describe a pod (for debugging)

```bash
kubectl describe pod $(kubectl get pod -l app=pl-stats-agent -o jsonpath='{.items[0].metadata.name}')
```

### Execute a command inside a pod

```bash
# Run a command inside the agent pod
kubectl exec -it $(kubectl get pod -l app=pl-stats-agent -o jsonpath='{.items[0].metadata.name}') -- bash

# Test internal connectivity
kubectl run test-curl --image=curlimages/curl --rm -it --restart=Never -- curl http://pl-stats-agent-svc:8000/health
```

---

## 3. Deployment

### Deploy new image to AKS manually

```bash
# Step 1 — Log in to ACR
az acr login --name plstatsacr

# Step 2 — Build agent image (always use linux/amd64 for AKS)
docker build \
  --platform linux/amd64 \
  -t plstatsacr.azurecr.io/pl-stats-agent:v1 \
  ./agent

# Step 3 — Build frontend image
docker build \
  --no-cache \
  --platform linux/amd64 \
  -t plstatsacr.azurecr.io/pl-stats-frontend:v2 \
  ./frontend

# Step 4 — Push images
docker push plstatsacr.azurecr.io/pl-stats-agent:v1
docker push plstatsacr.azurecr.io/pl-stats-frontend:v2

# Step 5 — Apply manifests
kubectl apply -f k8s/agent/
kubectl apply -f k8s/frontend/

# Step 6 — Restart deployments
kubectl rollout restart deployment pl-stats-agent
kubectl rollout restart deployment pl-stats-frontend

# Step 7 — Watch rollout
kubectl get pods -w
```

### Deploy via CI/CD (recommended)

```bash
# Just push to main — GitHub Actions handles everything automatically
git add .
git commit -m "your message"
git push origin main

# Watch the pipeline at:
# https://github.com/justinvu-au/Agent-PL-Player-Stats/actions
```

### Check rollout status

```bash
kubectl rollout status deployment/pl-stats-agent
kubectl rollout status deployment/pl-stats-frontend
```

### Roll back a deployment

```bash
kubectl rollout undo deployment/pl-stats-agent
kubectl rollout undo deployment/pl-stats-frontend
```

---

## 4. Secrets management

### View secrets in Key Vault

```bash
az keyvault secret list --vault-name plstats-kv --query "[].name" -o table
```

### Update a secret in Key Vault

```bash
az keyvault secret set \
  --vault-name plstats-kv \
  --name rapidapi-key \
  --value "YOUR_NEW_KEY"
```

### Recreate Kubernetes secret from Key Vault

```bash
# Delete existing secret
kubectl delete secret pl-stats-secrets

# Recreate from Key Vault
kubectl create secret generic pl-stats-secrets \
  --from-literal=rapidapi-key="$(az keyvault secret show --vault-name plstats-kv --name rapidapi-key --query value -o tsv)" \
  --from-literal=anthropic-api-key="$(az keyvault secret show --vault-name plstats-kv --name anthropic-api-key --query value -o tsv)"
```

---

## 5. Local development

### Start local stack with Docker Compose

```bash
cd /Users/justinv/pl-stats-platform

# Start both services
docker compose -f infra/docker/docker-compose.yml up

# Start in background
docker compose -f infra/docker/docker-compose.yml up -d

# Stop
docker compose -f infra/docker/docker-compose.yml down

# Open local app
open http://localhost:3000
```

### Run agent locally without Docker

```bash
cd /Users/justinv/pl-stats-platform
source .venv/bin/activate
cd agent
PYTHONPATH=src uvicorn src.pl_stats.main:app --reload --port 8000
```

### Run tests

```bash
cd /Users/justinv/pl-stats-platform
source .venv/bin/activate
cd agent
python -m pytest tests/ -v
```

### Run frontend locally

```bash
cd /Users/justinv/pl-stats-platform/frontend
npm run dev
# Open http://localhost:3000
```

---

## 6. Azure infrastructure

### Provision infrastructure from scratch

```bash
cd /Users/justinv/pl-stats-platform/infra/terraform
terraform init
terraform plan
terraform apply
```

### Destroy all Azure resources (zero cost)

```bash
cd /Users/justinv/pl-stats-platform/infra/terraform
terraform destroy
# Type 'yes' when prompted
# Recreate anytime with terraform apply
```

### Check Azure resource costs

```bash
# Open Cost Management in Azure Portal
open "https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/overview"
```

---

## 7. ACR (Container Registry)

### List images in ACR

```bash
az acr repository list --name plstatsacr -o table
```

### List tags for an image

```bash
az acr repository show-tags \
  --name plstatsacr \
  --repository pl-stats-agent \
  -o table
```

### Log in to ACR

```bash
az acr login --name plstatsacr
```

---

## 8. Kubernetes services

### Check services and public IP

```bash
kubectl get services
```

### Check HPA (autoscaler) status

```bash
kubectl get hpa
```

### Check all resources

```bash
kubectl get all
```

---

## 9. Troubleshooting

### Pod stuck in ImagePullBackOff

```bash
# Check the exact error
kubectl describe pod <pod-name> | grep -A 10 "Events:"

# Re-attach ACR to AKS
az aks update \
  --name plstats-aks \
  --resource-group pl-stats-rg \
  --attach-acr plstatsacr

# Restart deployment
kubectl rollout restart deployment pl-stats-agent
```

### App returns "Failed to fetch"

```bash
# Test agent is reachable internally
kubectl run test-curl --image=curlimages/curl --rm -it --restart=Never \
  -- curl http://pl-stats-agent-svc:8000/health

# Check agent logs
kubectl logs -l app=pl-stats-agent --tail=50
```

### Pod stuck in Pending

```bash
# Check why
kubectl describe pod <pod-name> | grep -A 10 "Events:"

# Usually means insufficient resources — check node
kubectl describe node
```

### Check API quota usage

```bash
curl http://4.147.108.223/api/health
# Returns: {"status": "healthy", "api_calls_today": X}
```

---

## 10. Azure Portal quick links

| Resource | Link |
|---|---|
| AKS cluster | https://portal.azure.com — search "Kubernetes services" → plstats-aks |
| Container Registry | https://portal.azure.com — search "Container registries" → plstatsacr |
| Key Vault | https://portal.azure.com — search "Key vaults" → plstats-kv |
| Resource Group | https://portal.azure.com — search "Resource groups" → pl-stats-rg |
| Cost Management | https://portal.azure.com — search "Cost Management" |
| Log Analytics | https://portal.azure.com — search "Log Analytics workspaces" → plstats-logs |
| GitHub Actions | https://github.com/justinvu-au/Agent-PL-Player-Stats/actions |

---

## 11. Environment variables reference

| Variable | Where | Purpose |
|---|---|---|
| `RAPIDAPI_KEY` | Azure Key Vault + `.env` | RapidAPI authentication |
| `ANTHROPIC_API_KEY` | Azure Key Vault + `.env` | Claude API authentication |
| `AGENT_URL` | K8s deployment env | Frontend → agent internal URL |

---

*Last updated: June 2026*