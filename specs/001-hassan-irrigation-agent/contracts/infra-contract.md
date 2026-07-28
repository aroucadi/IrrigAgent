# Interface Contract: Terraform GCP Infrastructure Module (`infra/`)

**Module Location**: `infra/` (`main.tf`, `variables.tf`, `outputs.tf`)  
**Provider**: `hashicorp/google` (v5.0+)  
**Purpose**: Provision GCP Cloud Run, Firestore Native DB, Cloud Scheduler 18:45 GMT+1 job, Secret Manager secrets, and IAM service accounts declaratively per Constitution Principle VII.

---

## Inputs (`infra/variables.tf`)

| Variable Name | Type | Default | Description | Required |
|---|---|---|---|---|
| `project_id` | `string` | N/A | GCP Project ID | Yes |
| `region` | `string` | `"europe-west1"` | GCP Region for deployment | No |
| `container_image` | `string` | `"gcr.io/irrigagent-project/app:latest"` | Container image URL for Cloud Run service | Yes |
| `whatsapp_access_token` | `string` | N/A | Meta WhatsApp Cloud API access token (stored in Secret Manager) | Yes |
| `whatsapp_verify_token` | `string` | N/A | Webhook verification handshake token (stored in Secret Manager) | Yes |
| `cron_secret` | `string` | N/A | Batch endpoint authorization token (stored in Secret Manager) | Yes |

---

## Outputs (`infra/outputs.tf`)

| Output Name | Type | Description |
|---|---|---|
| `cloud_run_url` | `string` | Public HTTPS URL of provisioned Cloud Run service |
| `cloudrun_service_account_email` | `string` | Service Account email associated with Cloud Run runtime |
| `scheduler_service_account_email` | `string` | Service Account email associated with Cloud Scheduler trigger |
| `firestore_database_name` | `string` | Name of the provisioned Firestore Native database |

---

## Terraform Operations & Commands

```bash
# Initialize Terraform provider plugins
terraform -chdir=infra init

# Validate syntax and configuration integrity
terraform -chdir=infra validate

# Generate execution plan against target GCP project
terraform -chdir=infra plan -var="project_id=my-gcp-project" -var-file="terraform.tfvars"

# Apply declarative infrastructure resources
terraform -chdir=infra apply -auto-approve -var="project_id=my-gcp-project" -var-file="terraform.tfvars"
```
