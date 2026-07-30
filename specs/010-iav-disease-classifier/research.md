# Research: Fine-Tuned Disease Classifier & IAV Hassan II Strategy

**Feature**: `010-iav-disease-classifier`
**Status**: Completed

## 1. IAV Hassan II Moroccan Dataset Sourcing & Annotation Schema

### Decision
Implement a standardized dataset validation and ingestion schema for field images collected by IAV Hassan II agronomists across Souss-Massa and Gharb regions.

### Key Requirements & Constraints
- **Target Crop Focus**: Tomatoes (TYLCV, Tuta Absoluta, Early Blight) & Citrus (Citrus Greening/HLB, Alternaria Leaf Spot, Red Spider Mite).
- **Minimum Volume Trigger**: ≥ 500 verified field photos per disease class taken under natural sunlight.
- **Annotation Schema**:
  - `disease_id`: ONSSA registration code (string).
  - `severity_index`: Integer grade from 1 to 5.
  - `bounding_boxes`: List of `[xmin, ymin, xmax, ymax]` normalized coordinates (0.0–1.0).
  - `region`: Souss-Massa or Gharb.
  - `cultivar`: e.g., Moneymaker, Nadorcott.

### Alternatives Considered
- *Using public PlantVillage dataset directly*: Rejected because PlantVillage leaf photos are captured under sterile laboratory lighting without dust or solar radiation conditions representative of Moroccan field environments.

---

## 2. Model Architecture & Temperature Scaling Calibration

### Decision
Use PyTorch to fine-tune an EfficientNet-B4 vision model, combined with Temperature Scaling Calibration (Platt scaling extension) on a held-out validation set.

### Key Technical Details
- **Architecture**: EfficientNet-B4 pre-trained backbone with customized classification head mapped to target ONSSA disease codes.
- **Temperature Scaling**: Adjust raw uncalibrated logits $z$ using learned temperature parameter $T > 0$ such that calibrated probability $\hat{p} = \max_i \text{softmax}(z / T)_i$ reflects true empirical accuracy ($|\hat{p} - \text{Accuracy}| \le 0.05$).
- **Fail-Closed Threshold**: If $\hat{p} < 0.75$ (75% calibrated confidence), the system suppresses specific chemical active ingredients and defaults to general cultural/sanitary advice.

---

## 3. Interim 2-Stage Vision Pipeline (Phase 2.2a Zero-Shot Gemini Flash + Quality Gate)

### Decision
Maintain the interim 2-stage production pipeline while dataset collection is ongoing.

### Execution Flow
1. **Stage 1 (Quality Gate)**:
   - Blur Check: Laplacian variance $\text{Var}(\nabla^2 I) \ge 100.0$.
   - Green Foliage Check: $\ge 30\%$ of pixels in HSV range $35^\circ \le H \le 85^\circ$.
   - Resolution Check: Width and height $\ge 400\text{ px}$.
   - *Failure Action*: Return immediate WhatsApp retake advice ("Photo is blurry or unreadable. Please take a close-up photo of the leaf under direct light.").
2. **Stage 2 (Zero-Shot Gemini 1.5 Flash + ONSSA RAG)**:
   - Multimodal prompt for initial triage.
   - ONSSA chemical registry vector/lookup integration (`data/onssa_authorized_products.json`).
   - Appends verbatim disclaimer: *"This is a first-pass triage only. Consult a licensed agronomist."*
