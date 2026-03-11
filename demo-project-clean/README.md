# DevOps Capstone Project: Containerized Flask Notes Application (Clean Version)

This project demonstrates a complete DevOps pipeline for a containerized Python Flask notes application. It utilizes Google Cloud Platform (GCP) services for everything from development to deployment, monitoring, and security. This is a "clean" version that removes the dependency on Secret Manager and the Gemini API key to simplify the core deployment process.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Architecture](#architecture)
3.  [Prerequisites](#prerequisites)
4.  [Local Development](#local-development)
5.  [GCP Setup](#gcp-setup)
6.  [Containerization](#containerization)
7.  [CI/CD with Cloud Build](#ci/cd-with-cloud-build)
8.  [Cloud Run Deployment](#cloud-run-deployment)
9.  [API Gateway Configuration](#api-gateway-configuration)
10. [Firestore Database](#firestore-database)
11. [Monitoring with Cloud Monitoring](#monitoring-with-cloud-monitoring)
12. [Logging with Cloud Logging](#logging-with-cloud-logging)
13. [Alerting and Notifications](#alerting-and-notifications)
14. [API Endpoints](#api-endpoints)
15. [Security Considerations](#security-considerations)
16. [Cleanup](#cleanup)

## 1. Project Overview

This project implements a simple Flask-based "notes" application that allows users to create and retrieve notes. The application is containerized using Docker and deployed to Google Cloud Run. A CI/CD pipeline with Cloud Build automates the build and deployment process. API Gateway is used to expose the application's API, and Firestore serves as the backend database. Monitoring, logging, and alerting are integrated using Cloud Monitoring and Cloud Logging.

## 2. Architecture

The application follows a modern serverless architecture on GCP:

```
[Client (e.g., Web App, Postman)]
        |
        v
[API Gateway]
        | (Routes requests)
        v
[Cloud Run Service] (Containerized Flask Application)
        |
        v
[Firestore Database] (Stores notes data)
        ^
        |
[Cloud Logging / Monitoring] (Collects logs and metrics from Cloud Run)
```

## 3. Prerequisites

Before you begin, ensure you have the following:

*   **Google Cloud Platform (GCP) Project:** A GCP project with billing enabled.
*   **`gcloud` CLI:** The Google Cloud SDK installed and configured.
    *   `gcloud auth login`
    *   `gcloud config set project YOUR_PROJECT_ID`
*   **Docker:** Docker Desktop or Docker Engine installed.
*   **Python 3.9+:** Python installed locally (for local development).
*   **`pip`:** Python package installer.

## 4. Local Development

You can run the Flask application locally for testing:

1.  Navigate to the `app` directory:
    ```bash
    cd demo-project-clean/app
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set the `GOOGLE_CLOUD_PROJECT` environment variable:
    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    ```
4.  Run the application:
    ```bash
    python main.py
    ```
    The application should be accessible at `http://127.0.0.1:8080`.

## 5. GCP Setup

The `scripts/setup_gcp.sh` script automates the initial configuration of your GCP project.

1.  Navigate to the project root:
    ```bash
    cd demo-project-clean
    ```
2.  Make the setup script executable:
    ```bash
    chmod +x scripts/setup_gcp.sh
    ```
3.  Run the setup script:
    ```bash
    ./scripts/setup_gcp.sh
    ```
    This script will:
    *   Enable necessary GCP APIs (Artifact Registry, Cloud Build, Cloud Run, API Gateway, Firestore, Logging, Monitoring).
    *   Create an Artifact Registry Docker repository (`notes-app-repo`).
    *   Create a dedicated service account for Cloud Run (`cloud-run-notes-app-sa`) and grant it the necessary IAM roles (Firestore access, Log Writer, Metric Writer).
    *   Grant Cloud Build the necessary permissions to deploy to Cloud Run and push to Artifact Registry.

## 6. Containerization

The application is containerized using Docker. The `app/Dockerfile` defines the image build process.

To build the Docker image locally:
```bash
cd demo-project-clean
docker build -t notes-app-image ./app
```

## 7. CI/CD with Cloud Build

The `cloudbuild.yaml` file defines the CI/CD pipeline using Google Cloud Build. This version deploys a new service called `notes-app-service-clean` to avoid conflicts with any previous, problematic deployments.

### How it works:

1.  **Build Step:** Builds the Docker image from `app/Dockerfile`.
2.  **Push Step:** Pushes the built Docker image to the Artifact Registry repository.
3.  **Deploy Step:** Deploys the new Docker image to a Cloud Run service named `notes-app-service-clean`.

### Setting up a Cloud Build Trigger:

To automate the CI/CD pipeline, you can create a Cloud Build trigger that listens for changes in your Git repository.

1.  **Connect your repository:** Go to **Cloud Build -> Triggers** in the GCP Console.
2.  Click **"Create trigger"**.
3.  Configure the trigger:
    *   **Name:** e.g., `notes-app-clean-ci-cd`
    *   **Event:** `Push to a branch`
    *   **Source:** Select your repository.
    *   **Branch:** e.g., `^main$`
    *   **Build configuration:** `Cloud Build configuration file`
    *   **Cloud Build file location:** `demo-project-clean/cloudbuild.yaml`

Now, every time you push changes to the specified branch, Cloud Build will automatically build, push, and deploy your application.

## 8. Cloud Run Deployment

The application is deployed as a serverless container to Google Cloud Run.

### Manual Deployment (using `deploy.sh`):

The `scripts/deploy.sh` script provides a convenient way to manually build, push, and deploy the application to Cloud Run. It has been cleaned of secret references.

1.  Navigate to the project root:
    ```bash
    cd demo-project-clean
    ```
2.  Make the deployment script executable:
    ```bash
    chmod +x scripts/deploy.sh
    ```
3.  Run the deployment script:
    ```bash
    ./scripts/deploy.sh
    ```
    This script will build, push, and deploy to the `notes-app-service-clean` service.

## 9. API Gateway Configuration

API Gateway can provide a single, consistent entry point to your Cloud Run service.

1.  **Get your Cloud Run Service URL:**
    ```bash
    gcloud run services describe notes-app-service-clean --region us-central1 --format="value(status.url)"
    ```
    Copy this URL.

2.  **Update `api_config.yaml`:**
    Open `demo-project-clean/api_config.yaml` and replace `"CLOUD_RUN_SERVICE_URL"` with the actual URL of your `notes-app-service-clean` service.

3.  **Deploy API Gateway:** Follow the steps in the original `README.md` (section 9), but use `notes-app-service-clean` as the service name where appropriate.

## 10. Firestore Database

The Flask application uses Google Firestore in Native mode to store notes. You can view your data in the GCP Console: **Firestore -> Data**.

## 11. Monitoring with Cloud Monitoring

Cloud Run services automatically integrate with Cloud Monitoring. Find pre-built dashboards in **Cloud Monitoring -> Dashboards**.

## 12. Logging with Cloud Logging

Cloud Run automatically sends container logs to Cloud Logging. View them in **Cloud Logging -> Logs Explorer**, filtering by `Cloud Run Revision` and service name `notes-app-service-clean`.

## 13. Alerting and Notifications

You can set up alerting policies in **Cloud Monitoring -> Alerting** to notify you of critical events or performance issues for the `notes-app-service-clean` service.

## 14. API Endpoints

Once your API Gateway is deployed, you can interact with the notes application using its public URL.

### GET /notes

```bash
curl -X GET "YOUR_API_GATEWAY_URL/notes"
```

### POST /notes

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"title": "New Idea", "content": "Brainstorming for a new project."}' \
     "YOUR_API_GATEWAY_URL/notes"
```

## 15. Security Considerations

*   **Service Accounts:** The use of dedicated service accounts with minimal necessary IAM roles (Principle of Least Privilege) enhances security.
*   **API Gateway Authentication:** For production, secure API Gateway and restrict direct access to the Cloud Run service.
*   **Firestore Security Rules:** For a real application, configure Firestore Security Rules to control data access.

## 16. Cleanup

To avoid incurring unwanted charges, clean up the GCP resources.

1.  **Delete Cloud Run Service:**
    ```bash
    gcloud run services delete notes-app-service-clean --region us-central1 --project=YOUR_PROJECT_ID
    ```
    (Also delete the original `notes-app-service` if it still exists)
    ```bash
    gcloud run services delete notes-app-service --region us-central1 --project=YOUR_PROJECT_ID
    ```

2.  **Delete API Gateway and API Config:**
    ```bash
    gcloud api-gateway gateways delete notes-app-gateway --location us-central1 --project=YOUR_PROJECT_ID
    gcloud api-gateway api-configs delete notes-app-config --api=notes-api-gateway --project=YOUR_PROJECT_ID
    gcloud api-gateway apis delete notes-api-gateway --project=YOUR_PROJECT_ID
    ```

3.  **Delete Artifact Registry Repository:**
    ```bash
    gcloud artifacts repositories delete notes-app-repo --location us-central1 --project=YOUR_PROJECT_ID
    ```

4.  **Delete Service Account:**
    ```bash
    gcloud iam service-accounts delete "cloud-run-notes-app-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" --project=YOUR_PROJECT_ID
    ```
5.  **Delete the entire GCP Project (DANGER!):**
    If this project was created specifically for this demo, you can delete the entire project. This is irreversible.
    ```bash
    gcloud projects delete YOUR_PROJECT_ID
    ```