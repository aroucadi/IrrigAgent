variable "project_id" {
  type        = string
  description = "The GCP Project ID where resources will be provisioned."
}

variable "region" {
  type        = string
  description = "The GCP region for Cloud Run and Firestore resources."
  default     = "europe-west1"
}

variable "container_image" {
  type        = string
  description = "The full gcr.io or artifact registry URL of the FastAPI container image."
  default     = "gcr.io/irrigagent-project/app:latest"
}

variable "whatsapp_access_token" {
  type        = string
  description = "Meta WhatsApp Cloud API Access Token stored in Secret Manager."
  sensitive   = true
  default     = "dummy_whatsapp_access_token"
}

variable "whatsapp_verify_token" {
  type        = string
  description = "Webhook verification handshake token stored in Secret Manager."
  sensitive   = true
  default     = "dummy_whatsapp_verify_token"
}

variable "cron_secret" {
  type        = string
  description = "Authorization secret token for daily recommendation batch trigger."
  sensitive   = true
  default     = "dummy_cron_secret"
}
