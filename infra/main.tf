terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

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
# Firestore Database (Native Mode)
# ------------------------------------------------------------------------------

resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# ------------------------------------------------------------------------------
# Secret Manager Containers & Versions
# ------------------------------------------------------------------------------

resource "google_secret_manager_secret" "whatsapp_token" {
  secret_id = "WHATSAPP_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "whatsapp_token_version" {
  secret      = google_secret_manager_secret.whatsapp_token.id
  secret_data = var.whatsapp_access_token
}

resource "google_secret_manager_secret" "verify_token" {
  secret_id = "VERIFY_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "verify_token_version" {
  secret      = google_secret_manager_secret.verify_token.id
  secret_data = var.whatsapp_verify_token
}

resource "google_secret_manager_secret" "cron_secret" {
  secret_id = "CRON_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cron_secret_version" {
  secret      = google_secret_manager_secret.cron_secret.id
  secret_data = var.cron_secret
}

# ------------------------------------------------------------------------------
# Cloud Run v2 Service (FastAPI Container)
# ------------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "irrigagent_app" {
  name     = "irrigagent-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloudrun_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = var.container_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name = "WHATSAPP_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.whatsapp_token.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "VERIFY_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.verify_token.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "JOB_SECRET_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.cron_secret.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_iam_member.cloudrun_firestore,
    google_project_iam_member.cloudrun_secrets
  ]
}

# Explicitly allow unauthenticated HTTP invocations for public Meta WhatsApp webhooks
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.irrigagent_app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ------------------------------------------------------------------------------
# Cloud Scheduler Job (18:45 GMT+1 Daily Trigger)
# ------------------------------------------------------------------------------

resource "google_cloud_scheduler_job" "daily_advisory_trigger" {
  name        = "irrigagent-daily-advisory-trigger"
  description = "Triggers proactive evening irrigation recommendation batch job daily at 18:45 GMT+1."
  schedule    = "45 17 * * *" # 17:45 UTC = 18:45 GMT+1 (UTC+1)
  time_zone   = "UTC"

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
