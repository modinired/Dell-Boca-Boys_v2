#!/bin/bash
# One-Click GCP Deployment Script for Dell Boca Boys V2
# Usage: ./deploy-gcp.sh [PROJECT_ID] [REGION]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
CLUSTER_NAME="dell-boca-boys-v2"
DB_INSTANCE_NAME="${CLUSTER_NAME}-db"
REDIS_INSTANCE_NAME="${CLUSTER_NAME}-redis"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Install from: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

    if [ -z "$PROJECT_ID" ]; then
        log_error "Usage: $0 PROJECT_ID [REGION]"
        exit 1
    fi

    log_info "✅ Prerequisites met"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    gcloud services enable \
        container.googleapis.com \
        sqladmin.googleapis.com \
        redis.googleapis.com \
        secretmanager.googleapis.com \
        compute.googleapis.com \
        --project="$PROJECT_ID"

    log_info "✅ APIs enabled"
}

create_gke_cluster() {
    log_info "Creating GKE Autopilot cluster (this takes ~5-10 minutes)..."

    if gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Cluster $CLUSTER_NAME already exists, skipping creation"
    else
        gcloud container clusters create-auto "$CLUSTER_NAME" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --release-channel=stable \
            --enable-private-nodes \
            --enable-private-endpoint \
            --workload-pool="${PROJECT_ID}.svc.id.goog" \
            --enable-autorepair \
            --enable-autoupgrade

        log_info "✅ GKE cluster created"
    fi

    # Get credentials
    gcloud container clusters get-credentials "$CLUSTER_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID"
}

create_cloud_sql() {
    log_info "Creating Cloud SQL PostgreSQL instance (this takes ~10-15 minutes)..."

    if gcloud sql instances describe "$DB_INSTANCE_NAME" --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Database instance $DB_INSTANCE_NAME already exists, skipping creation"
    else
        gcloud sql instances create "$DB_INSTANCE_NAME" \
            --database-version=POSTGRES_15 \
            --tier=db-custom-2-7680 \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --network=default \
            --no-assign-ip \
            --enable-bin-log \
            --backup-start-time=02:00 \
            --maintenance-window-day=SUN \
            --maintenance-window-hour=03 \
            --database-flags=cloudsql.enable_pgvector=on

        log_info "✅ Cloud SQL instance created"
    fi

    # Create database
    log_info "Creating database..."
    gcloud sql databases create dell_boca_boys \
        --instance="$DB_INSTANCE_NAME" \
        --project="$PROJECT_ID" || log_warn "Database may already exist"

    # Create user with strong password
    DB_PASSWORD=$(openssl rand -base64 32)
    gcloud sql users create dbuser \
        --instance="$DB_INSTANCE_NAME" \
        --password="$DB_PASSWORD" \
        --project="$PROJECT_ID" || log_warn "User may already exist"

    # Store password in Secret Manager
    echo -n "$DB_PASSWORD" | gcloud secrets create dell-boca-db-password \
        --data-file=- \
        --replication-policy=automatic \
        --project="$PROJECT_ID" || log_warn "Secret may already exist"
}

create_redis() {
    log_info "Creating Memorystore Redis instance (this takes ~5-10 minutes)..."

    if gcloud redis instances describe "$REDIS_INSTANCE_NAME" --region="$REGION" --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Redis instance $REDIS_INSTANCE_NAME already exists, skipping creation"
    else
        gcloud redis instances create "$REDIS_INSTANCE_NAME" \
            --tier=basic \
            --size=1 \
            --region="$REGION" \
            --redis-version=redis_7_0 \
            --project="$PROJECT_ID"

        log_info "✅ Redis instance created"
    fi
}

setup_workload_identity() {
    log_info "Setting up Workload Identity for secure authentication..."

    # Create GCP service accounts
    for SA in api n8n webui; do
        gcloud iam service-accounts create "${SA}" \
            --display-name="Dell Boca Boys ${SA} Service Account" \
            --project="$PROJECT_ID" || log_warn "Service account ${SA} may already exist"

        # Grant permissions
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/cloudsql.client" \
            --condition=None

        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/secretmanager.secretAccessor" \
            --condition=None

        # Bind to K8s service account
        gcloud iam service-accounts add-iam-policy-binding \
            "${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role=roles/iam.workloadIdentityUser \
            --member="serviceAccount:${PROJECT_ID}.svc.id.goog[dell-boca-boys-v2/dell-boca-${SA}]" \
            --project="$PROJECT_ID"
    done

    log_info "✅ Workload Identity configured"
}

create_secrets() {
    log_info "Creating secrets in Secret Manager..."

    # N8N API Token
    N8N_TOKEN=$(openssl rand -hex 32)
    echo -n "$N8N_TOKEN" | gcloud secrets create dell-boca-n8n-token \
        --data-file=- \
        --replication-policy=automatic \
        --project="$PROJECT_ID" || log_warn "Secret may already exist"

    # N8N Encryption Key
    N8N_KEY=$(openssl rand -hex 32)
    echo -n "$N8N_KEY" | gcloud secrets create dell-boca-n8n-encryption \
        --data-file=- \
        --replication-policy=automatic \
        --project="$PROJECT_ID" || log_warn "Secret may already exist"

    log_info "✅ Secrets created"
}

build_and_push_images() {
    log_info "Building and pushing Docker images to GCR..."

    # Enable Container Registry
    gcloud services enable containerregistry.googleapis.com --project="$PROJECT_ID"

    # Configure Docker auth
    gcloud auth configure-docker --quiet

    # Build and push API image
    log_info "Building API image..."
    docker build -t "gcr.io/${PROJECT_ID}/dell-boca-boys-api:latest" \
        -f ../Dell-Boca-Boys-main/Dockerfile \
        ../Dell-Boca-Boys-main/
    docker push "gcr.io/${PROJECT_ID}/dell-boca-boys-api:latest"

    # Build and push WebUI image (same Dockerfile, different entrypoint)
    log_info "Building WebUI image..."
    docker build -t "gcr.io/${PROJECT_ID}/dell-boca-boys-webui:latest" \
        -f ../Dell-Boca-Boys-main/Dockerfile \
        ../Dell-Boca-Boys-main/
    docker push "gcr.io/${PROJECT_ID}/dell-boca-boys-webui:latest"

    log_info "✅ Images pushed to GCR"
}

deploy_application() {
    log_info "Deploying application to GKE..."

    # Get Redis host
    REDIS_HOST=$(gcloud redis instances describe "$REDIS_INSTANCE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(host)")

    # Update kustomization with actual values
    cd ../cloud/k8s/overlays/gcp

    # Create a temporary patch with actual values
    cat > temp-values.yaml <<EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: dell-boca-boys-v2

bases:
  - ../../base

resources:
  - workload-identity.yaml
  - cloud-sql-proxy.yaml

configMapGenerator:
  - name: database-config
    behavior: merge
    literals:
      - host=127.0.0.1
      - port=5432
      - database=dell_boca_boys
  - name: redis-config
    behavior: merge
    literals:
      - host=${REDIS_HOST}
      - port=6379

images:
  - name: dell-boca-boys-api
    newName: gcr.io/${PROJECT_ID}/dell-boca-boys-api
    newTag: latest
  - name: dell-boca-boys-webui
    newName: gcr.io/${PROJECT_ID}/dell-boca-boys-webui
    newTag: latest
EOF

    # Deploy with kubectl
    kubectl apply -k .

    log_info "✅ Application deployed"
    cd -
}

wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."

    kubectl wait --for=condition=available --timeout=300s \
        deployment/api -n dell-boca-boys-v2

    kubectl wait --for=condition=available --timeout=300s \
        deployment/n8n -n dell-boca-boys-v2

    kubectl wait --for=condition=available --timeout=300s \
        deployment/webui -n dell-boca-boys-v2

    log_info "✅ All deployments ready"
}

display_access_info() {
    log_info "======================================"
    log_info "Deployment Complete! 🎉"
    log_info "======================================"

    INGRESS_IP=$(kubectl get ingress -n dell-boca-boys-v2 -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')

    echo ""
    log_info "Access your services at:"
    echo "  Dashboard: http://${INGRESS_IP}"
    echo "  n8n:       http://${INGRESS_IP}/n8n"
    echo "  API Docs:  http://${INGRESS_IP}/api/docs"
    echo ""
    log_warn "Note: It may take a few minutes for DNS to propagate"
    echo ""
    log_info "Database credentials stored in Secret Manager:"
    echo "  gcloud secrets versions access latest --secret=dell-boca-db-password --project=${PROJECT_ID}"
    echo ""
    log_info "To access kubectl:"
    echo "  gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION} --project=${PROJECT_ID}"
    echo ""
}

# Main execution
main() {
    log_info "Starting Dell Boca Boys V2 deployment to GCP..."
    log_info "Project: $PROJECT_ID"
    log_info "Region: $REGION"
    echo ""

    check_prerequisites
    enable_apis
    create_gke_cluster
    create_cloud_sql &
    create_redis &

    # Wait for parallel operations
    wait

    setup_workload_identity
    create_secrets
    build_and_push_images
    deploy_application
    wait_for_deployment
    display_access_info

    log_info "Deployment script completed successfully! ✅"
}

# Run main function
main "$@"
