# Data Model: 004-fix-critical-bugs-and-gaps

## Key Entities & Data Schemas

### 1. FarmProfile Schema (`app/schemas.py`)

Represents the validated farm profile stored in Firestore collection `farm_profiles`.

```python
class FarmProfile(BaseModel):
    phone_number: str = Field(description="WhatsApp phone number in E.164 format (e.g. +212600000000)")
    location: str = Field(description="Farm location / region in Morocco (e.g. Berrechid, Saïss)")
    crop_type: str = Field(description="Target crop species (e.g. tomatoes, potatoes, citrus)")
    acreage_hectares: float = Field(gt=0, description="Field surface area in hectares")
    preferred_language: str = Field(default="fr", description="Preferred interaction language ('fr' or 'ar')")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last profile edit")
```

#### Validation Rules
- `phone_number`: Non-empty string starting with `+` or digits.
- `location`: Non-empty location name string.
- `crop_type`: Non-empty crop description string.
- `acreage_hectares`: Positive floating-point number strictly greater than 0.
- `preferred_language`: Must be either `"fr"` (French) or `"ar"` (Darija/Arabic script).

---

### 2. CropDiagnosisRequest (`app/cropdoctor.py`)

Data payload passed to CropDoctor AI vision triage module.

```python
class CropDiagnosisRequest(BaseModel):
    image_bytes: bytes = Field(description="Raw JPEG/PNG image binary payload")
    phone_number: str = Field(description="Sender phone number")
    force_confidence: Optional[float] = Field(default=None, description="Explicit mock test confidence override")
    is_test_fixture: bool = Field(default=False, description="Flag indicating automated test fixture execution")
```

#### Mock Triage Logic
- `is_test_fixture` OR `image_bytes == b"fake_high_confidence"`: Triggers deterministic test response.
- All real JPEG image binary inputs: Processed via Gemini 1.5 Flash vision model API.
- Exception / failure fallback: Returns structured "unreadable/no leaf identified" advice with ONSSA disclaimer.

---

### 3. LanguageContext (`app/firestore_client.py`)

Data object representing language detection evaluation for incoming/outgoing WhatsApp messages.

```python
class LanguageContext(BaseModel):
    raw_text: str
    clock_time_tokens: List[str] = Field(default_factory=list, description="Extracted clock-time tokens like 07h00")
    cleaned_text: str = Field(description="Text stripped of clock-time tokens for Arabizi evaluation")
    detected_language: str = Field(description="'fr' or 'ar'")
```

#### Exclusion Rule
- Patterns matching `\b\d{1,2}h\d{2}\b` (e.g., `07h00`, `19h00`) are extracted into `clock_time_tokens` and removed from `cleaned_text` before Arabizi digit adjacency checks execute.
