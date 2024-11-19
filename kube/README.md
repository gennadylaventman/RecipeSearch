Recipe Search Application Kubernetes Deployment

This repository contains Kubernetes manifests for deploying a recipe search application. The application consists of the following components:

    FastAPI Application: Provides the API for searching recipes by title or ingredients.
    PostgreSQL Database: Stores recipe data and ingredient details.
    Qdrant Vector Database: Handles vector-based title search using embeddings.
    Initialization Job: Prepares the database with initial data.

Deployment Overview
Secrets

    File: secrets.yaml
    Contains sensitive information such as database credentials.
    Keys:
        POSTGRES_USER: Encoded database user.
        POSTGRES_PASSWORD: Encoded database password.
        POSTGRES_DB: Encoded database name.

PostgreSQL

    Files:
        postgres-deployment.yaml
        postgres-service.yaml
        postgres-pvc.yaml
    Deployment:
        Uses a postgres:14 image.
        Stores data in a Persistent Volume (postgres-pvc) with 5Gi of storage.
        Credentials fetched from db-secrets.
    Service:
        Exposes PostgreSQL internally via ClusterIP on port 5432.

Qdrant

    Files:
        qdrant-deployment.yaml
        qdrant-service.yaml
        qdrant-pvc.yaml
    Deployment:
        Uses the qdrant/qdrant:latest image.
        Stores data in a Persistent Volume (qdrant-pvc) with 5Gi of storage.
        Exposes HTTP (port 6333) and gRPC (port 6334) APIs.
    Service:
        Accessible internally within the cluster using ClusterIP.

FastAPI Application

    Files:
        fastapi-app-deployment.yaml
        fastapi-app-service.yaml
    Deployment:
        Uses a custom image lgennady/my-recipe-search-app:latest.
        Launches the FastAPI server (search_recipe.py) with database and Qdrant connection details.
        Environment variables are sourced from db-secrets.
    Service:
        Exposes the application externally via LoadBalancer on port 8000.

Database Initialization Job

    File: dbinit-job.yaml
    Purpose:
        Initializes the database with required schema and data.
        Executes the script /app/run_init_tasks.sh.
    Execution:
        Runs as a Kubernetes job with no retries on failure.

Persistent Storage

    PostgreSQL:
        Storage provisioned through postgres-pvc (5Gi).
    Qdrant:
        Storage provisioned through qdrant-pvc (5Gi).
    Storage Class:
        gp2 (modifiable depending on the cluster setup).

Service Summary
Component	Type	Ports	Access Scope
PostgreSQL	ClusterIP	5432	Internal
Qdrant	ClusterIP	6333 (HTTP), 6334 (gRPC)	Internal
FastAPI App	LoadBalancer	8000	External
Deployment Instructions

    Apply the manifests in the following order to ensure proper dependency setup:

kubectl apply -f secrets.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
kubectl apply -f qdrant-pvc.yaml
kubectl apply -f qdrant-deployment.yaml
kubectl apply -f qdrant-service.yaml
kubectl apply -f fastapi-app-deployment.yaml
kubectl apply -f fastapi-app-service.yaml
kubectl apply -f dbinit-job.yaml

Verify all components are running:

    kubectl get pods
    kubectl get services

    Access the FastAPI application via the external IP of the fastapi-service.

