# Technical Research & Architectural Decisions: Hassan Persona & Darija Voice Teaser

**Branch**: `001-hassan-irrigation-agent` | **Date**: 2026-07-28 | **Spec**: [spec.md](spec.md)

## Overview

This document outlines key technical decisions, architectural research, and design choices for the Hassan Irrigation Agent and the opt-in **Darija Voice Teaser Module** using Google Cloud Text-to-Speech (`ar-MA`).

---

## Technical Decisions

### Decision 1: Moroccan Darija Abstraction & Normalized Intent Schema
- **Decision**: Implement a two-way translation abstraction layer. All internal business logic, ET₀ calculations, and CropDoctor disease triage execute strictly in English / structured Pydantic models. Incoming Arabic script, Arabizi, or voice transcriptions map to normalized English intent schemas before hitting decision logic. Outgoing text is converted into standard Arabic-script Darija (e.g., `دير ليا 10 دقايق زيادة غدا مع الـ 05:00`) for TTS rendering.
- **Rationale**: Keeps decision engine 100% deterministic and eliminates AI hallucination risk in agronomy calculations and ONSSA chemical safety pointers.
- **Alternatives Considered**: Direct LLM decision-making in Darija (rejected: high risk of numeric and chemical hallucination).

---

### Decision 2: Google Cloud Text-to-Speech (ar-MA) & OGG_OPUS Encoding
- **Decision**: Use `google-cloud-texttospeech` Python client library with `languageCode='ar-MA'` (Moroccan Arabic) and `AudioEncoding.OGG_OPUS` (`audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.OGG_OPUS)`).
- **Rationale**: `ar-MA` provides authentic Moroccan Arabic phoneme synthesis. `OGG_OPUS` matches Meta WhatsApp Cloud API voice message requirements (`audio/ogg; codecs=opus`) natively, enabling direct upload without requiring heavy `ffmpeg` binary dependencies in the Cloud Run container.
- **Alternatives Considered**:
  - MP3 encoding (rejected: requires local `ffmpeg` transcoding to OGG OPUS for WhatsApp native voice note waveform rendering).
  - External TTS APIs like ElevenLabs (rejected: adds external cost, network latency, and non-standard GCP integration).

---

### Decision 3: Asynchronous Non-Blocking Voice Teaser Workflow
- **Decision**: Primary WhatsApp text/button confirmations execute synchronously within the HTTP webhook response loop (<1.0s latency SLA). Voice note generation (TTS synthesis, audio file staging, Meta Cloud API media upload, and `send_audio_message`) is dispatched asynchronously via FastAPI `BackgroundTasks` or `asyncio.create_task`.
- **Rationale**: Preserves core sub-second production performance SLA while allowing live demo recordings to receive audio notes 1.5–2.5s later without blocking text delivery.
- **Alternatives Considered**: Synchronous voice synthesis inside webhook response (rejected: total webhook duration exceeds 3.0s, risking Meta Cloud API webhook timeout and retries).

---

### Decision 4: Latin Arabizi Pre-Translation Pipeline
- **Decision**: Route incoming or generated Latin Arabizi text through an LLM translation step to convert Arabizi strings into standard Arabic script Darija (e.g., `dir 10 min zeyada` → `دير 10 دقايق زيادة`) prior to sending text to GCP TTS `ar-MA`.
- **Rationale**: GCP TTS `ar-MA` synthesizer is tuned for Arabic script text. Passing Latin characters with numbers (e.g., `3afak`, `9dim`) results in garbled letter-by-letter English pronunciation or synthesis errors.
- **Alternatives Considered**: Rule-based regex translation for Arabizi numbers (rejected: Arabizi vocabulary varies too widely for simple regex replacement).

---

### Decision 5: Feature Flag Control (`ENABLE_DARIJA_VOICE_TEASER`)
- **Decision**: Expose environment variable `ENABLE_DARIJA_VOICE_TEASER` (`bool`, default `false`). When set to `false`, voice note dispatch is completely bypassed at zero runtime cost.
- **Rationale**: Protects automated integration tests, CI pipelines, and core production runs from unwanted TTS API quota usage and latency. Enables demo mode seamlessly during live incubator pitches.
- **Alternatives Considered**: Hardcoded feature toggles (rejected: requires code edits for demo vs testing).
