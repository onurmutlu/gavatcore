# 🚀 GAVATCore v6.0 Production Deployment Guide

## 📋 Overview

Bu guide, GAVATCore OnlyVips platformunu production ortamında Kubernetes veya AWS ECS üzerinde deploy etmeniz için gerekli tüm adımları içerir.

## 🎯 Deployment Options

### 1. Kubernetes (Recommended)
- ✅ Auto-scaling
- ✅ Self-healing
- ✅ Rolling updates
- ✅ Service discovery
- ✅ Resource management

### 2. AWS ECS Fargate
- ✅ Serverless containers
- ✅ AWS managed
- ✅ Auto-scaling
- ✅ Load balancing

## 🔧 Prerequisites

### Required Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Docker
brew install docker

# Install AWS CLI
brew install awscli

# Install Helm (optional)
brew install helm
```

### Required Services
- Docker Registry (GitHub Container Registry or AWS ECR)
- Kubernetes Cluster (EKS, GKE, AKS) or AWS ECS
- Domain name and SSL certificates
- Monitoring stack (Prometheus + Grafana)

## 🐳 Docker Build & Push

### Local Build
```bash
# Build images
./deploy.sh build

# Push to registry
./deploy.sh push
```

### Using GitHub Actions
```bash
# Push to main branch for production
git push origin main

# Create release tag
git tag v6.0.0
git push origin v6.0.0
```

## ☸️ Kubernetes Deployment

### 1. Cluster Setup
```bash
# Create EKS cluster (example)
eksctl create cluster \
  --name gavatcore-production \
  --version 1.28 \
  --region us-west-2 \
  --nodegroup-name worker-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed
```

### 2. Configure kubectl
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name gavatcore-production

# Verify connection
kubectl cluster-info
```

### 3. Create Secrets
```bash
# Create Telegram API key secret
kubectl create secret generic gavatcore-secrets \
  --from-literal=telegram-api-key="YOUR_TELEGRAM_API_KEY" \
  --from-literal=database-password="YOUR_DB_PASSWORD" \
  --from-literal=jwt-secret-key="YOUR_JWT_SECRET" \
  --from-literal=encryption-key="YOUR_ENCRYPTION_KEY" \
  -n gavatcore
```

### 4. Deploy Application
```bash
# Using deployment script
./deploy.sh kubernetes

# Or manually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 5. Verify Deployment
```bash
# Check pod status
kubectl get pods -n gavatcore

# Check services
kubectl get svc -n gavatcore

# Check ingress
kubectl get ingress -n gavatcore

# View logs
kubectl logs -f deployment/gavatcore-app -n gavatcore
```

## 🎯 AWS ECS Deployment

### 1. Create ECS Cluster
```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name gavatcore-cluster \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

# Create task execution role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file://aws/task-execution-role.json

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### 2. Create EFS File System
```bash
# Create EFS for persistent storage
aws efs create-file-system \
  --throughput-mode provisioned \
  --provisioned-throughput-in-mibps 100 \
  --performance-mode generalPurpose \
  --tags Key=Name,Value=gavatcore-efs
```

### 3. Register Task Definition
```bash
# Update task definition with your account ID and EFS ID
aws ecs register-task-definition \
  --cli-input-json file://aws/task-definition.json
```

### 4. Create Service
```bash
# Create ECS service
aws ecs create-service \
  --cluster gavatcore-cluster \
  --service-name gavatcore-service \
  --task-definition gavatcore-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}"
```

### 5. Setup Load Balancer
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name gavatcore-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Create target group
aws elbv2 create-target-group \
  --name gavatcore-targets \
  --protocol HTTP \
  --port 5050 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /api/system/status
```

## 📊 Monitoring Setup

### Prometheus & Grafana
```bash
# Install using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/prometheus-values.yaml

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

### Custom Dashboards
- Import dashboard JSON files from `monitoring/grafana/dashboards/`
- Configure data sources pointing to Prometheus

## 🔐 Security Best Practices

### 1. Network Security
- Use private subnets for application pods
- Configure security groups/network policies
- Enable WAF on load balancers

### 2. Secret Management
```bash
# Use AWS Secrets Manager or Kubernetes Secrets
kubectl create secret generic gavatcore-secrets \
  --from-env-file=.env.production \
  -n gavatcore

# Rotate secrets regularly
kubectl delete secret gavatcore-secrets -n gavatcore
kubectl create secret generic gavatcore-secrets \
  --from-env-file=.env.production.new \
  -n gavatcore
```

### 3. RBAC Configuration
```yaml
# Apply RBAC rules
kubectl apply -f k8s/rbac.yaml
```

## 🚀 Deployment Strategies

### Rolling Update (Default)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

### Blue-Green Deployment
```bash
# Deploy new version with different label
kubectl apply -f k8s/deployment-green.yaml

# Switch traffic
kubectl patch service gavatcore-app-service -p '{"spec":{"selector":{"version":"green"}}}'

# Clean up old version
kubectl delete -f k8s/deployment-blue.yaml
```

### Canary Deployment
```bash
# Deploy canary version with fewer replicas
kubectl apply -f k8s/deployment-canary.yaml

# Monitor metrics and gradually increase traffic
```

## 📈 Performance Optimization

### Resource Limits
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Horizontal Pod Autoscaler
```bash
# Create HPA
kubectl autoscale deployment gavatcore-app \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n gavatcore
```

### Caching Strategy
- Redis for session storage
- CDN for static assets
- Application-level caching

## 🔍 Troubleshooting

### Common Issues

1. **Pod Stuck in Pending**
   ```bash
   kubectl describe pod <pod-name> -n gavatcore
   # Check resource availability and node selector
   ```

2. **Service Unreachable**
   ```bash
   kubectl get endpoints -n gavatcore
   # Verify service selector matches pod labels
   ```

3. **Image Pull Errors**
   ```bash
   kubectl describe pod <pod-name> -n gavatcore
   # Check image registry credentials
   ```

### Log Analysis
```bash
# Application logs
kubectl logs -f deployment/gavatcore-app -n gavatcore

# Previous container logs
kubectl logs deployment/gavatcore-app --previous -n gavatcore

# All containers in pod
kubectl logs <pod-name> --all-containers -n gavatcore
```

## 🔄 Backup & Recovery

### Database Backups
```bash
# Automated backup script
./scripts/backup-database.sh

# Restore from backup
./scripts/restore-database.sh backup-20240106.sql
```

### Persistent Volume Snapshots
```bash
# Create snapshot
kubectl create -f k8s/volumesnapshot.yaml

# Restore from snapshot
kubectl create -f k8s/pvc-from-snapshot.yaml
```

## 📞 Support & Maintenance

### Health Checks
- Application: `/api/system/status`
- Admin: `/api/admin/system/health`
- Database connectivity
- External service dependencies

### Update Procedures
1. Update image tags in deployment files
2. Apply rolling update
3. Monitor health checks
4. Rollback if necessary

### Emergency Procedures
```bash
# Quick rollback
kubectl rollout undo deployment/gavatcore-app -n gavatcore

# Scale down for maintenance
kubectl scale deployment gavatcore-app --replicas=0 -n gavatcore

# Emergency stop
./deploy.sh rollback
```

## 📊 Performance Metrics

### Key Performance Indicators
- Response time: < 200ms (95th percentile)
- Availability: > 99.9%
- Error rate: < 0.1%
- Throughput: > 1000 requests/second

### Monitoring Alerts
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%
- Response time > 1 second
- Error rate > 1%

## 🎯 Scaling Guidelines

### Vertical Scaling
```bash
# Increase resource limits
kubectl patch deployment gavatcore-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"gavatcore-app","resources":{"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'
```

### Horizontal Scaling
```bash
# Increase replica count
kubectl scale deployment gavatcore-app --replicas=5 -n gavatcore
```

### Auto-scaling Configuration
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gavatcore-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gavatcore-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 📞 Contact & Support

- **Email**: support@gavatcore.com
- **Slack**: #gavatcore-production
- **Documentation**: https://docs.gavatcore.com
- **Status Page**: https://status.gavatcore.com

Bu guide sürekli güncellenmektedir. Son versiyonu için repository'yi kontrol edin. 