#!/bin/bash

# 🚀 GAVATCore v6.0 Production Deployment Script
# Kubernetes & AWS ECS deployment automation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="gavatcore"
APP_VERSION=${VERSION:-"6.0.0"}
REGISTRY=${REGISTRY:-"ghcr.io/gavatcore"}
ENVIRONMENT=${ENVIRONMENT:-"production"}

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check if required tools are installed
    command -v docker >/dev/null 2>&1 || error "Docker is not installed"
    command -v kubectl >/dev/null 2>&1 || error "kubectl is not installed"
    command -v aws >/dev/null 2>&1 || error "AWS CLI is not installed"
    
    # Check if Docker is running
    docker info >/dev/null 2>&1 || error "Docker is not running"
    
    success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    log "🐳 Building Docker images..."
    
    # Build main application image
    log "Building GAVATCore App image..."
    docker build \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION="${APP_VERSION}" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
        -t "${REGISTRY}/gavatcore-app:${APP_VERSION}" \
        -t "${REGISTRY}/gavatcore-app:latest" \
        -f Dockerfile .
    
    # Build admin dashboard image
    log "Building GAVATCore Admin image..."
    docker build \
        -t "${REGISTRY}/gavatcore-admin:${APP_VERSION}" \
        -t "${REGISTRY}/gavatcore-admin:latest" \
        -f Dockerfile.admin .
    
    success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log "📤 Pushing images to registry..."
    
    docker push "${REGISTRY}/gavatcore-app:${APP_VERSION}"
    docker push "${REGISTRY}/gavatcore-app:latest"
    docker push "${REGISTRY}/gavatcore-admin:${APP_VERSION}"
    docker push "${REGISTRY}/gavatcore-admin:latest"
    
    success "Images pushed to registry"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "☸️ Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply ConfigMaps and Secrets
    log "Applying ConfigMaps and Secrets..."
    kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE}
    
    # Update image tags in deployment
    log "Updating deployment with new images..."
    sed -i.bak "s|gavatcore/app:6.0.0|${REGISTRY}/gavatcore-app:${APP_VERSION}|g" k8s/deployment.yaml
    sed -i.bak "s|gavatcore/admin:6.0.0|${REGISTRY}/gavatcore-admin:${APP_VERSION}|g" k8s/deployment.yaml
    
    # Apply all Kubernetes manifests
    kubectl apply -f k8s/ -n ${NAMESPACE}
    
    # Wait for deployments to be ready
    log "Waiting for deployments to be ready..."
    kubectl rollout status deployment/gavatcore-app -n ${NAMESPACE} --timeout=600s
    kubectl rollout status deployment/gavatcore-admin -n ${NAMESPACE} --timeout=600s
    kubectl rollout status deployment/gavatcore-redis -n ${NAMESPACE} --timeout=300s
    
    # Restore original deployment file
    mv k8s/deployment.yaml.bak k8s/deployment.yaml
    
    success "Kubernetes deployment completed"
}

# Deploy to AWS ECS
deploy_ecs() {
    log "🎯 Deploying to AWS ECS..."
    
    # Update ECS task definition
    aws ecs register-task-definition \
        --cli-input-json file://aws/task-definition.json \
        --region us-west-2
    
    # Update ECS service
    aws ecs update-service \
        --cluster gavatcore-cluster \
        --service gavatcore-service \
        --task-definition gavatcore-task:LATEST \
        --force-new-deployment \
        --region us-west-2
    
    # Wait for service to stabilize
    log "Waiting for ECS service to stabilize..."
    aws ecs wait services-stable \
        --cluster gavatcore-cluster \
        --services gavatcore-service \
        --region us-west-2
    
    success "AWS ECS deployment completed"
}

# Health check
health_check() {
    log "🏥 Performing health checks..."
    
    # Get service URLs
    if [ "${DEPLOYMENT_TARGET}" = "kubernetes" ]; then
        APP_URL=$(kubectl get service gavatcore-app-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        ADMIN_URL=$(kubectl get service gavatcore-admin-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    else
        # ECS URLs would be retrieved differently
        APP_URL="https://gavatcore.com"
        ADMIN_URL="https://admin.gavatcore.com"
    fi
    
    # Health check with retries
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://${APP_URL}/api/system/status" >/dev/null 2>&1; then
            success "Application health check passed"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Application health check failed after ${max_attempts} attempts"
        fi
        
        log "Health check attempt ${attempt}/${max_attempts} failed, retrying in 10s..."
        sleep 10
        ((attempt++))
    done
}

# Rollback function
rollback() {
    warning "🔄 Rolling back deployment..."
    
    if [ "${DEPLOYMENT_TARGET}" = "kubernetes" ]; then
        kubectl rollout undo deployment/gavatcore-app -n ${NAMESPACE}
        kubectl rollout undo deployment/gavatcore-admin -n ${NAMESPACE}
        kubectl rollout status deployment/gavatcore-app -n ${NAMESPACE}
        kubectl rollout status deployment/gavatcore-admin -n ${NAMESPACE}
    else
        # ECS rollback logic
        aws ecs update-service \
            --cluster gavatcore-cluster \
            --service gavatcore-service \
            --task-definition gavatcore-task:PREVIOUS \
            --region us-west-2
    fi
    
    success "Rollback completed"
}

# Cleanup old images
cleanup() {
    log "🧹 Cleaning up old Docker images..."
    
    # Remove old images (keep last 3 versions)
    docker images "${REGISTRY}/gavatcore-app" --format "table {{.Tag}}" | \
        tail -n +4 | \
        xargs -I {} docker rmi "${REGISTRY}/gavatcore-app:{}" 2>/dev/null || true
    
    docker images "${REGISTRY}/gavatcore-admin" --format "table {{.Tag}}" | \
        tail -n +4 | \
        xargs -I {} docker rmi "${REGISTRY}/gavatcore-admin:{}" 2>/dev/null || true
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "🚀 Starting GAVATCore v${APP_VERSION} deployment to ${ENVIRONMENT}"
    
    # Parse command line arguments
    DEPLOYMENT_TARGET=${1:-"kubernetes"}
    
    # Trap to handle rollback on failure
    trap 'error "Deployment failed! Run ./deploy.sh rollback to revert changes"' ERR
    
    case "${1:-deploy}" in
        "build")
            check_prerequisites
            build_images
            ;;
        "push")
            push_images
            ;;
        "kubernetes"|"k8s")
            check_prerequisites
            build_images
            push_images
            deploy_kubernetes
            health_check
            cleanup
            ;;
        "ecs")
            check_prerequisites
            build_images
            push_images
            deploy_ecs
            health_check
            cleanup
            ;;
        "rollback")
            rollback
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 {build|push|kubernetes|ecs|rollback|health|cleanup}"
            echo ""
            echo "Commands:"
            echo "  build      - Build Docker images only"
            echo "  push       - Push images to registry"
            echo "  kubernetes - Full deployment to Kubernetes"
            echo "  ecs        - Full deployment to AWS ECS"
            echo "  rollback   - Rollback to previous version"
            echo "  health     - Perform health check"
            echo "  cleanup    - Clean up old Docker images"
            echo ""
            echo "Environment variables:"
            echo "  VERSION    - Application version (default: 6.0.0)"
            echo "  REGISTRY   - Docker registry (default: ghcr.io/gavatcore)"
            echo "  ENVIRONMENT- Deployment environment (default: production)"
            exit 1
            ;;
    esac
    
    success "🎉 Deployment completed successfully!"
    log "📊 Deployment summary:"
    log "   Version: ${APP_VERSION}"
    log "   Environment: ${ENVIRONMENT}"
    log "   Target: ${DEPLOYMENT_TARGET}"
    log "   Timestamp: $(date)"
}

# Run main function
main "$@" 