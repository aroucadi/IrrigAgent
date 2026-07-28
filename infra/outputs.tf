output "cloud_run_url" {
  value       = google_cloud_run_v2_service.irrigagent_app.uri
  description = "Public HTTPS URL of the provisioned Cloud Run FastAPI service."
}

output "cloudrun_service_account_email" {
  value       = google_service_account.cloudrun_sa.email
  description = "IAM Service Account email associated with Cloud Run runtime."
}

output "scheduler_service_account_email" {
  value       = google_service_account.scheduler_sa.email
  description = "IAM Service Account email associated with Cloud Scheduler trigger."
}

output "firestore_database_name" {
  value       = google_firestore_database.database.name
  description = "Name of the provisioned Firestore Native database."
}
