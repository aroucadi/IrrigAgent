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
