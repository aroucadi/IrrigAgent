# ------------------------------------------------------------------------------
# Dedicated IAM Service Accounts (Least-Privilege Identities)
# ------------------------------------------------------------------------------

resource "google_service_account" "cloudrun_sa" {
  account_id   = "irrigagent-cloudrun-sa"
  display_name = "IrrigAgent Cloud Run Runtime Service Account"
  description  = "Least-privilege runtime identity for FastAPI Cloud Run container."
}

resource "google_service_account" "scheduler_sa" {
  account_id   = "irrigagent-scheduler-sa"
  display_name = "IrrigAgent Cloud Scheduler Invoker Service Account"
  description  = "Identity for Cloud Scheduler OIDC authentication to Cloud Run endpoint."
}

# ------------------------------------------------------------------------------
# IAM Role Bindings (Minimal Permissions)
# ------------------------------------------------------------------------------

resource "google_project_iam_member" "cloudrun_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

resource "google_project_iam_member" "cloudrun_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

resource "google_project_iam_member" "scheduler_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# ------------------------------------------------------------------------------
# Cloud Scheduler Job (18:45 Africa/Casablanca Daily Trigger)
# ------------------------------------------------------------------------------

resource "google_cloud_scheduler_job" "daily_advisory_trigger" {
  name        = "irrigagent-daily-advisory-trigger"
  description = "Triggers proactive evening irrigation recommendation batch job daily at 18:45 Africa/Casablanca."
  schedule    = "45 18 * * *"
  time_zone   = "Africa/Casablanca"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.irrigagent_app.uri}/jobs/daily-recommendations"

    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [
    google_cloud_run_v2_service.irrigagent_app,
    google_project_iam_member.scheduler_invoker
  ]
}
