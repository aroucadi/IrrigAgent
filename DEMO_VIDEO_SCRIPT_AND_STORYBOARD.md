# IrrigAgent AI — StartGate Pitch & Demo Video Master Script & Storyboard

**Target Duration:** 100 Seconds (1 Min 40 Sec)  
**Target Audience:** StartGate Incubator Selection Panel, Investors, AgTech Partners  
**Core Value Proposition:** Climate-resilient AI irrigation & crop protection agent for Moroccan smallholders, operating over WhatsApp with zero hardware required, hardware-ready sensor fusion, real Sentinel-2 satellite NDVI canopy health, and Gemini 1.5 Flash Darija voice/vision.

---

## 🎬 Video Production Overview

| Parameter | Specification |
|---|---|
| **Total Length** | 100 seconds (0:00 – 1:40) |
| **Aspect Ratio** | 16:9 (Horizontal Desktop/YouTube) + 9:16 (Vertical Reels/Shorts cutout) |
| **Primary Voiceover** | French (Standard for Moroccan AgTech / Incubation pitches) |
| **Alternative Voiceovers** | English & Moroccan Darija (Provided in script below) |
| **On-Screen Subtitles** | English + French captions hardcoded on screen |
| **Key Codebase Highlights** | 183 automated tests passing, 100% human-in-the-loop, GCP Cloud Run ready |

---

## ⏱️ Scene-by-Scene Storyboard & Script Breakdown

### Act 1: The Problem & FAO-56 Daily WhatsApp Advisory (0:00 – 0:25)

**Visual (0:00 - 0:10):**
- Opening shot: Split screen showing water-stressed tomato crop in Souss-Massa region on left, and live WhatsApp interface on smartphone screen on right.
- On-screen Title Overlay: **IrrigAgent AI — Autonomous Precision Irrigation for Moroccan Smallholders**.

**Visual (0:10 - 0:25):**
- Focus on WhatsApp chat. An incoming **Meta Utility Template Message** (`irrigagent_daily_advisory`) arrives:
  > 🌾 *IrrigAgent Advisory for Tomorrow*  
  > High crop water demand expected (5.75 mm ETc [ET₀ 5.0 × Kc 1.15]). Recommendation: Increase irrigation duration by +15 min tomorrow morning.  
  > [ Button: Approve ] [ Button: Skip ] [ Button: Modify ]
- The user taps **`Approve`**. Instant confirmation message appears:  
  > ✅ *Irrigation approved! Schedule updated (+15 min).*

**Narration:**
- 🇫🇷 **French:** *"Au Maroc, le stress hydrique menace nos agriculteurs. IrrigAgent résout ce défi en envoyant chaque soir une recommandation d'irrigation ultra-précise sur WhatsApp, calculée selon la méthode FAO-56. Sans aucun équipement payant requis, l'agriculteur valide d'un seul clic."*
- 🇬🇧 **English:** *"In Morocco, water scarcity threatens smallholders. IrrigAgent solves this by delivering daily FAO-56 precision irrigation advisories over WhatsApp—requiring zero paid hardware. Farmers approve or adjust with a single tap."*
- 🇲🇦 **Darija:** *"F L'Maroc, naqs l'ma kayhded l'fellaha. IrrigAgent kayjeb l'hal: nasiha d'l'ssqi kol lila f WhatsApp hssab FAO-56, bla ma tchri hta chi capteur. L'fellah kaykonfirmi b clik wahed."*

---

### Act 2: Closed-Loop IoT Sensor Fusion Calibration (0:25 – 0:45)

**Visual (0:25 - 0:35):**
- Split screen: Terminal on left, WhatsApp on right.
- Live Terminal Execution:
  ```bash
  py scripts/simulate_sensor.py --farm "+212600000000" --vwc 14.5 --depth 15
  ```
- Output in terminal: `📡 Transmitting soil moisture telemetry... ✅ Telemetry recorded.`

**Visual (0:35 - 0:45):**
- Live WhatsApp screen updates automatically with a new sensor-calibrated advisory:
  > 🌾 *IrrigAgent Advisory for Tomorrow*  
  > High crop water demand expected (5.75 mm ETc).  
  > 📡 *Données Capteur Sol (15cm): Humidité mesurée à 14.5% (Épuisement détecté → ajustement +15 min).*  
  > [ Button: Approve ] [ Button: Skip ] [ Button: Modify ]

**Narration:**
- 🇫🇷 **French:** *"Mais IrrigAgent est aussi Hardware-Ready. Lorsqu'une sonde d'humidité est connectée, notre moteur de Fusion de Données réétalonne automatiquement les calculs météo avec l'humidité réelle du sol, tout en maintenant un contrôle 100% humain."*
- 🇬🇧 **English:** *"IrrigAgent is also Hardware-Ready. When a soil moisture probe is available, our Sensor Fusion engine fuses real-time soil moisture ground-truth with weather math—with 100% human approval safety."*
- 🇲🇦 **Darija:** *"W IrrigAgent hardware-ready. Mli kaykon capteur d'rrotoba, l'moteur de fusion kayqad l'hssab b rrotoba d'l'ard l'hsaqiyya, w dima l'fellah huwa l'mass'oul."*

---

### Act 3: CropDoctor Leaf Photo Disease Triage & ONSSA Compliance (0:45 – 1:05)

**Visual (0:45 - 0:55):**
- Farmer takes a live camera photo of a tomato leaf showing early blight / mildew lesions and sends it over WhatsApp.
- OpenCV prefilter runs instantly (rejecting blurry photos fast).

**Visual (0:55 - 1:05):**
- Gemini 1.5 Flash multimodal vision processes the image and responds in 1.8 seconds with diagnosis in French and Darija:
  > 🔬 *CropDoctor Diagnosis: Mildiou de la tomate (Phytophthora infestans)*  
  > 🇲🇦 Darija: *Hada l'mildiou f tmatem.*  
  > 💊 *Produit ONSSA Autorisé:* Ridomil Gold MZ (Indice ONSSA #2024-89).  
  > ⚠️ *Avertissement:* Respecter le délai avant récolte (DAR: 7 jours).

**Narration:**
- 🇫🇷 **French:** *"En cas de maladie, l'agriculteur envoie une photo de la feuille. CropDoctor, alimenté par Gemini 1.5 Flash et OpenCV, diagnostique le problème en moins de deux secondes et recommande exclusivement des produits homologués ONSSA."*
- 🇬🇧 **English:** *"When crops show disease, farmers snap a photo. CropDoctor, powered by Gemini 1.5 Flash and OpenCV, diagnoses issues in under two seconds and references official ONSSA-registered treatments."*
- 🇲🇦 **Darija:** *"Mli kaykon mard, l'fellah kaysswr l'wroqa. CropDoctor b Gemini 1.5 Flash kayfhes l'mard f aqall mnn jouj thwani w kay'tik l'dwa l'mourakhas mnn ONSSA."*

---

### Act 4: Real Sentinel-2 Satellite Canopy Heatmap & Darija Voice ASR (1:05 – 1:30)

**Visual (1:05 - 1:18):**
- Farmer drops 4 GPS location pins on WhatsApp to mark parcel boundaries.
- IrrigAgent queries STAC API (Copernicus / Element84), fetches 10m Sentinel-2 COG imagery, and renders a crisp high-resolution **NDVI Canopy Health Heatmap** (Matplotlib colored geotiff overlay) directly into the WhatsApp thread.

**Visual (1:18 - 1:30):**
- Farmer sends a 5-second audio voice note in Moroccan Darija: *"Zid 15 dqiqa f'ssqi d'ghdda"* (Add 15 minutes to tomorrow's irrigation).
- Gemini 1.5 Flash Audio ASR transcribes the audio note and sends a confirmation request:
  > 🌾 *Demande Vocale Reçue (Confiance: 94%)*  
  > Transcription: *"Zid 15 dqiqa f ssqi"*  
  > Modification proposée: +15 minutes.  
  > Répondez: 1 = Confirmer | 2 = Annuler

**Narration:**
- 🇫🇷 **French:** *"Pour le suivi spatial, IrrigAgent télécharge les imageries satellites Sentinel-2 pour générer une carte thermique NDVI de la santé de la canopée. Et grâce à l'ASR Darija de Gemini Flash, même les agriculteurs peu alphabétisés contrôlent leur ferme à la voix."*
- 🇬🇧 **English:** *"For spatial tracking, IrrigAgent pulls real Sentinel-2 satellite imagery to generate NDVI canopy health heatmaps. And with Gemini Flash Darija Voice ASR, even low-literacy farmers control irrigation using simple voice notes."*
- 🇲🇦 **Darija:** *"W l'kharta d'l'satellit Sentinel-2 katwrrih sihhat l mehsoul (NDVI). W b l'ssawt b Darija b Gemini Flash, hta l'fellah lli ma kayqrach kayt-hekkem f l'ssqi b ssawtou."*

---

### Act 5: Enterprise Governance & StartGate Pitch Call-to-Action (1:30 – 1:40)

**Visual (1:30 - 1:40):**
- Screen transitions to developer dashboard showing:
  - `183 / 183 tests passing` (`pytest`)
  - Fast single-container FastAPI architecture deployed on **GCP Cloud Run**
  - Text Banner: **StartGate 2026 Ready — Built for Scale, Security, and Smallholder Impact.**

**Narration:**
- 🇫🇷 **French:** *"Avec 183 tests automatisés valides, une architecture GCP Cloud Run évolutive et le respect strict du contrôle humain, IrrigAgent est prêt à transformer l'agriculture marocaine avec StartGate."*
- 🇬🇧 **English:** *"Backed by 183 verified automated tests, scalable GCP Cloud Run architecture, and strict human governance, IrrigAgent is ready to scale across Morocco with StartGate."*
- 🇲🇦 **Darija:** *"B 183 test m'valider, architecture GCP Cloud Run qwiya, IrrigAgent wajed bash ybdel l'filaha f l'Maroc m'a StartGate."*

---

## 🛠️ Step-by-Step Recording Command Sheet (Live Demo Execution)

Follow these exact steps during video recording to capture live, flawless footage:

### 1. Terminal Window Setup
Open 2 terminal windows side-by-side:
- **Terminal A (Server Logs):** `uvicorn app.main:app --reload`
- **Terminal B (Simulator CLI):** Ready in `d:\rouca\DVM\workPlace\IrrigAgent`

### 2. Pre-Run Test Verification (Show 183/183 Tests Passing)
Run in Terminal B (record screen for 3 seconds):
```bash
pytest
```
*Expected Output:* `183 passed in 20.82s`

### 3. Trigger Live Sensor Telemetry Simulator (Act 2 Shot)
Run in Terminal B:
```bash
py scripts/simulate_sensor.py --farm "+212600000000" --vwc 14.5 --depth 15
```
*Expected Output:*
```text
📡 Transmitting soil moisture telemetry to http://localhost:8000/telemetry/sensor...
  • Farm ID : +212600000000
  • VWC %   : 14.5%
  • Depth   : 15 cm
  • Battery : 95%
✅ Telemetry successfully recorded!
```

### 4. Trigger Daily Advisory Batch Run (Act 1 & 2 WhatsApp Shot)
Run in Terminal B:
```bash
curl -X POST "http://localhost:8000/jobs/daily-recommendations" -H "X-Job-Secret: internal_secret"
```

---

## 🎨 On-Screen Captions & Visual Polish Checklist

1. **Overlay 1 (0:05):** `🌾 FAO-56 Reference Evapotranspiration Math (ETc = ET₀ × Kc)`
2. **Overlay 2 (0:30):** `📡 Closed-Loop Sensor Fusion (VWC % Telemetry + Weather Math)`
3. **Overlay 3 (0:50):** `🔬 CropDoctor Multimodal AI (Gemini 1.5 Flash + OpenCV + ONSSA Registry)`
4. **Overlay 4 (1:10):** `🛰️ Real Sentinel-2 STAC 10m NDVI Satellite Canopy Heatmap`
5. **Overlay 5 (1:20):** `🎙️ Gemini 1.5 Flash Audio ASR (Moroccan Darija Voice-to-Intent)`
6. **Overlay 6 (1:35):** `✅ 183 Passing Tests | GCP Cloud Run | 100% Human-in-the-Loop`
