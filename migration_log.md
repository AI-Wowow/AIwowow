# Migration Log - July 7, 2025

## Objective
Successfully migrate the local Django application to use a Google Cloud SQL (PostgreSQL) database and Google Cloud Storage for file hosting.

---

## 1. Database Migration (Google Cloud SQL)

### Solution: Cloud SQL Auth Proxy
- The application is configured to connect to a Google Cloud SQL PostgreSQL instance using the **Cloud SQL Auth Proxy**.
- The proxy runs locally and securely tunnels connections to the Cloud SQL instance, allowing the Django application to connect as if it were a standard local database on `127.0.0.1:5432`.
- **Outcome:** Database migrations were successfully applied to the Cloud SQL database.

---

## 2. File Storage Migration (Google Cloud Storage)

### Solution: Separate Storage Backends for Static and Media Files
- The application uses Google Cloud Storage for both static and media files, with distinct security policies for each.
- **Public Static Files:** Configured to be publicly accessible for efficient serving of CSS, JavaScript, and other static assets.
- **Private Media Files:** User-uploaded content (e.g., videos) is stored privately and accessed via **Google Cloud Storage Signed URLs**. These URLs provide secure, time-limited access.
- **Authentication for Signed URLs:** Service Account Impersonation is used to securely generate signed URLs. The application leverages a service account (`django-app-runner@ai-wowow.iam.gserviceaccount.com`) to sign URLs, ensuring private content remains protected without requiring downloadable private keys.
- **Outcome:** Static files were successfully collected and uploaded to GCS. The application is now correctly configured to serve both public static files and private media files from Google Cloud Storage.

---

## Current Status & How to Resume Work

All migration tasks are complete, and the application is fully configured for cloud development.

To run the application, you must perform two steps:

1.  **Start the Database Proxy:** In a dedicated terminal, run this command from the project root:
    ```bash
    ./cloud-sql-proxy ai-wowow:us-central1:video-compete-app-db
    ```

2.  **Run the Django Server:** In your main terminal, start the development server as usual:
    ```bash
    python manage.py runserver
    ```

This log provides a concise overview of the successful migration and setup.