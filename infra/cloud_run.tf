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
