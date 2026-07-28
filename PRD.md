\# IrrigAgent AI — Product Requirements Document



\*\*Version:\*\* 0.4 (Application Draft — Solo Founder / Realistic Scope, Spec-Kit Ready) | \*\*Prepared for:\*\* StartGate Agri-Food Tech Incubator — 5th Cohort (UM6P × IAV Hassan II)

\*\*Application Deadline:\*\* September 13, 2026

\*\*Founder availability:\*\* Solo, building today through August 20; offline for vacation from August 21

\*\*Target Users:\*\* Small/medium farmers, farm managers, and cooperatives in Morocco



\---



\## Table of Contents



1\. Executive Summary

2\. Problem \& Market Opportunity

3\. Strategic Alignment with StartGate / Génération Green

4\. Target User Persona

5\. MVP Scope (Tightened for Solo Founder + Fixed Runway)

6\. Technical Architecture

7\. Business Model

8\. Competitive Landscape

9\. Validation \& Pilot Plan

10\. Milestones

11\. Risks \& Mitigations

12\. Team

13\. Success Metrics for StartGate Demo

14\. Spec-Kit Alignment \& Bootstrap

15\. Day 1 Quick-Start — Project Structure \& Webhook Code

16\. Appel à Candidatures — Submission Narrative



\---



\## 1. Executive Summary



IrrigAgent AI is a WhatsApp-native AI agent that helps small and medium Moroccan farms make daily irrigation decisions, without asking farmers to learn a dashboard. A farmer's phone receives a daily, weather- and soil-driven irrigation recommendation and approves or adjusts it with a one-tap WhatsApp reply. A lightweight companion feature, CropDoctor, lets a farmer send a photo of a sick leaf and get a first-pass diagnosis and treatment pointer.



The project sits directly inside StartGate's Agri-Food Tech Incubator mandate — smart and sustainable agriculture, in line with the Génération Green 2020–2030 strategy — co-run by UM6P and IAV Hassan II, a natural agronomic-validation partner for the disease-triage feature. Our ask of the program is not just funding, but the mentorship, technical capacity-building, and IAV agronomic review the incubator is built to provide.



\*\*Scope note (v0.4):\*\* this version deliberately narrows the MVP to what one solo founder can build, test with real farmers, and demo convincingly in roughly three focused weeks before an August 21 vacation, with the application submitted by September 13. The proactive irrigation agent is the hero feature and must work end-to-end with real users. CropDoctor is a light secondary feature: text-only, no voice, no full regulatory RAG. Everything else from the original concept (voice I/O, valve automation, multi-farm scheduling, payments, sensor integration, full WhatsApp Business Verification) is explicitly deferred past the application stage. This is a narrower but fully believable and demo-able product, which matters more at idea stage than feature breadth.



\*\*Regulatory stance:\*\* ONSSA (Morocco's food-safety and plant-health authority) has no formal certification standard for AI advisory tools to pass, so we make no claim of official approval. Instead, any treatment guidance from CropDoctor references only products on the official ONSSA register of authorized plant protection products, and every response carries a mandatory disclaimer that it is a first-pass triage only — not a substitute for a licensed agronomist or the official product label. Formal agronomic validation with IAV Hassan II is requested as a core incubation deliverable, not claimed as already in place.



\*\*Build methodology:\*\* the technical build will run through GitHub's \[spec-kit](https://github.com/github/spec-kit) spec-driven development workflow (constitution → specify → plan → tasks → implement) rather than ad-hoc prompting, so that intent stays traceable and Claude Code implements against an explicit spec, not chat history. See Section 14.



\## 2. Problem \& Market Opportunity



\*\*Water scarcity is structural, not seasonal.\*\* Morocco's natural rainfall has fallen sharply — from roughly 12 billion cubic meters a year to about 5 billion cubic meters in 2023 — and the country now ranks among the 25 most water-stressed nations globally. Agriculture accounts for the large majority of national water withdrawals, so small efficiency gains at the farm level scale into meaningful national impact.



\*\*The efficient-irrigation gap is concentrated among smallholders.\*\* Of Morocco's roughly 9.6 million hectares of cropland, only about 1.5–1.7 million hectares are irrigated, and a small fraction of that uses efficient systems like drip irrigation. National modernization programs have disproportionately reached larger operations; a large majority of small farm holdings remain outside their technical and financial support, relying instead on static timers or intuition.



\*\*Dashboard fatigue is real and specific to this segment.\*\* Existing AgTech software generally assumes desktop-style engagement and multi-screen navigation. Farm managers in this segment already run their business over WhatsApp, so a channel-native agent has a materially lower adoption barrier than another app to download.



\*\*Why now / why us:\*\* open weather and evapotranspiration data (Open-Meteo), a capable low-cost multimodal LLM (Gemini via GCP credits), and free-tier WhatsApp messaging (Meta Cloud API sandbox) make a real, farmer-tested pilot buildable by one person at near-zero infrastructure cost.



\## 3. Strategic Alignment with StartGate / Génération Green



\- \*\*Sector fit:\*\* falls squarely under "smart and sustainable agriculture," the incubator's lead vertical.

\- \*\*Génération Green 2020–2030:\*\* directly serves resource-efficiency and rural-development goals, targeting smallholders historically underserved by prior modernization plans.

\- \*\*IAV Hassan II partnership:\*\* we plan to request two concrete things from IAV Hassan II during incubation — agronomic review of CropDoctor outputs on Moroccan cultivars, and support exploring structured access to the official ONSSA register of authorized plant protection products — turning a stated program resource into named validation steps rather than a vague aspiration.

\- \*\*Program process fit:\*\* the pilot plan (Section 9) is designed to produce evidence of real farmer contact before submission, which matters more to an idea-stage incubator than a fully-featured build.



\## 4. Target User Persona



\*\*Hassan — Farm Manager / Farmer\*\*

Manages 5–20 hectares (tomatoes, citrus). Communicates in Darija/French, primarily by WhatsApp. Owns a smartphone but has low tolerance for app-based software. Trusts advice that comes with a clear, low-effort action ("reply 1 to approve") over analytics he has to interpret himself.



\*Validation note:\* this persona is a working hypothesis until confirmed by real conversations. Given solo-founder bandwidth, the realistic target is 3 solid farmer/cooperative conversations before submission (not the 5–8 originally planned) — see Section 9. Quality of conversation matters more than count.



\## 5. MVP Scope (Tightened for Solo Founder + Fixed Runway)



\### Hero feature — must work end-to-end for the demo: IrrigAgent (Proactive Water Recommendation Agent)

\- Daily pull from Open-Meteo (weather + ET₀) for a given farm location.

\- Simple rule-based or lightweight-LLM decision logic: given tomorrow's forecast and ET₀, recommend an irrigation adjustment.

\- Proactive WhatsApp message with one-tap options:

&#x20; - Reply 1 = Approve

&#x20; - Reply 2 = Skip today

&#x20; - Reply 3 = Modify (then free text)

\- Farm profile (location, crop type, approximate area, preferred language) stored in Firestore.

\- Human-in-the-loop only — no real solenoid/valve control in this version.



\### Secondary feature — kept deliberately light: CropDoctor (Basic Photo Triage)

\- Farmer sends a leaf photo via WhatsApp.

\- Gemini 1.5 Flash (via Vertex AI) returns: likely issue (French + simple Darija), a confidence indicator, treatment guidance that references only products on the official ONSSA-authorized register, and a strong disclaimer — \*"This is a first-pass triage only. It does not replace advice from a licensed agronomist or the official product label. Always verify with ONSSA-authorized products."\*

\- No full ONSSA RAG catalog or structured register integration in v1, no supplier locator, no voice reply. Text response only, with the disclaimer above on every reply.



\### Explicitly cut for the application period

\- Full voice-in / voice-out Darija support

\- Autonomous valve/solenoid control

\- Complex multi-farm scheduling

\- Pricing or payment flows

\- Advanced soil-sensor integration

\- Full WhatsApp Business Verification (stays in sandbox for the pilot)



This scope still tells a complete, credible story — "WhatsApp-native agentic irrigation decision support, with an early disease-triage module" — while being achievable by one person in the time available.



\## 6. Technical Architecture



```

\[ WhatsApp (Meta Cloud API — sandbox) ] ◄──Webhook──► \[ FastAPI on GCP Cloud Run ]

&#x20;                                                             │

&#x20;                                                     ┌───────┴───────┐

&#x20;                                                     ▼               ▼

&#x20;                                             \[ Decision Logic ]  \[ Firestore DB ]

&#x20;                                             (rules / lightweight    (Farm Profiles,

&#x20;                                              LLM via PydanticAI)     Message Log)

&#x20;                                                     │

&#x20;                                   ┌─────────────────┴─────────────────┐

&#x20;                                   ▼                                   ▼

&#x20;                            \[ Open-Meteo ]                     \[ Gemini 1.5 Flash ]

&#x20;                             (Weather / ET₀)                    (leaf photo triage)

```



| Layer | Choice | Notes |

|---|---|---|

| Messaging | Meta WhatsApp Cloud API (sandbox) | Free, up to 5 verified numbers, no Business Verification needed for the pilot |

| Backend | Python 3.11+, FastAPI | Single service, kept simple |

| Agent logic | PydanticAI (or plain rules to start) | Start rule-based; add LLM reasoning only if time allows |

| AI model | Gemini 1.5 Flash via Vertex AI | Funded by GCP credits; Flash, not Pro, to control cost/latency |

| Database | Firestore | Farm profiles + message log only — no complex schema |

| Hosting | GCP Cloud Run | Serverless, scales to zero, minimal idle cost |



\*\*Why this stays de-risked:\*\* no paid messaging vendor, no business-verification blocker, no infrastructure that needs babysitting, and a decision engine that can start as plain rules (fast to build, easy to demo, upgradeable to an LLM agent later without changing the interface).



\## 7. Business Model



\- \*\*Cooperative subscription (primary hypothesis):\*\* monthly per-hectare or per-member fee billed to agricultural cooperatives, which already aggregate smallholder relationships and payment collection. Comparable agtech advisory subscriptions elsewhere in Africa and the Mediterranean typically land in a modest per-hectare-per-season range rather than large flat fees — a useful anchor to test, not a committed number.

\- \*\*Freemium for individual farmers:\*\* free tier covers basic CropDoctor triage; paid tier unlocks proactive IrrigAgent alerts.

\- \*\*B2B2F channel (medium-term):\*\* partnerships with agri-input suppliers or crop insurers who want irrigation/disease signals to reduce their own risk exposure.

\- \*\*Public/NGO grant alignment (medium-term):\*\* Génération Green alignment makes the product a plausible fit for rural-development or water-efficiency grant programs.



This remains a hypothesis explicitly flagged for pressure-testing during the farmer conversations in Section 9 — appropriate honesty for idea stage, not a weakness to over-correct with invented numbers.



\## 8. Competitive Landscape (initial scan)



International precision-agriculture platforms and African mobile-first agtech players demonstrate the underlying model works, but none combine WhatsApp-native delivery with ONSSA-aware guidance for the Moroccan market specifically. This is a real gap, not an untested category. A fuller local scan — including a direct check with the incubator team for any existing UM6P/IAV Hassan II-affiliated projects — is a lightweight task to complete before submission, not a blocker to building.



\## 9. Validation \& Pilot Plan (realistic for solo bandwidth)



\- Reach out to 4–6 farm managers/cooperative contacts through personal network, LinkedIn, and local farming groups; target \*\*3 solid conversations\*\*, not a large sample.

\- Recruit 2–3 of them as verified numbers in the WhatsApp sandbox.

\- Run at least one full recommendation cycle with each; if time allows, one real photo triage.

\- Capture screen recordings of the real WhatsApp exchanges for the demo video — this is the evidence that matters most to reviewers, more than interview volume.



\## 10. Milestones (fitted to the August 21 vacation, submission by September 13)



\*\*Today → August 10 — Build the core\*\*

\- Set up spec-kit and generate constitution.md + spec.md + plan.md (Section 14) \*before\* writing application code.

\- Meta Developer account + WhatsApp Cloud API app in \*\*sandbox\*\* mode; verify personal number + 1–2 test numbers.

\- Webhook endpoint (Day 1 code, Section 15) working end-to-end with FastAPI on Cloud Run.

\- Open-Meteo integration + simple rule-based irrigation recommendation logic.

\- Basic farm profile stored in Firestore; proactive daily message + reply handling (1/2/3).



\*\*August 11–18 — Validation + light secondary feature\*\*

\- Outreach to 4–6 farm contacts; target 3 solid conversations.

\- Recruit 2–3 real numbers into the sandbox.

\- Run at least one full recommendation cycle with each.

\- If time allows: basic photo → Gemini diagnosis flow (CropDoctor).

\- Capture screen recordings of real WhatsApp exchanges.



\*\*August 19–20 — Demo + package\*\*

\- Record a 90–120 second demo video: onboarding, live recommendation + farmer reply, optional photo triage, and a short spoken explanation of the agentic loop and why WhatsApp is the right channel.

\- Finalize the application narrative (Section 16) and this PRD.

\- Update this PRD with real farmer quotes if available.



\*\*August 21 onward — Vacation\*\*

\- Application is essentially complete before departure.

\- Submit any time before September 13 — earlier is safer, but no need to rush the final night.

\- Only light polish if something critical is missing on return.



\## 11. Risks \& Mitigations



| Risk | Mitigation |

|---|---|

| Solo founder, fixed 25-day runway before vacation | Scope cut to one hero feature that must work, one light secondary feature that's optional |

| Sandbox cap of 5 numbers limits pilot size | Sufficient for application evidence; full verification deferred to post-selection |

| Real farmer recruitment takes longer than expected | Target lowered to 3 solid conversations via warm/near-warm channels, not cold outreach at scale |

| Vision model not tuned to Moroccan cultivars/pests | Explicitly flagged as a known MVP limitation with disclaimer; IAV validation proposed post-selection |

| Debugging time on webhooks/async loops eats the schedule | Rule-based decision logic first; LLM reasoning is an upgrade, not a dependency, for the demo to work |

| Regulatory exposure on treatment advice | Mandatory disclaimer + "consult a licensed agronomist" framing on every CropDoctor response |

| Solo founder, no formal agronomy background | Named explicitly in Section 12; addressed by requesting IAV Hassan II validation during incubation rather than claiming false expertise |

| Vibe-coding drift (agent builds something that doesn't match intent) | Spec-kit workflow (Section 14) makes the spec the source of truth; code is generated against it, not against ad-hoc chat |



\## 12. Team



\*\*Solo founder: \[Your Full Name]\*\*



I am an Agile Coach with a previous background as Technical Leader and IT Manager, and international professional experience across France, Switzerland, and remote global teams. I recently won a Gemini hackathon, securing $10,000 in Google Cloud credits that fully fund the infrastructure for this pilot.



I bring strong experience in technical leadership, system design, and rapid delivery under constraints. While I do not have a formal agronomy background, I have a clear thesis: smallholder farmers in Morocco will not adopt another dashboard. IrrigAgent is therefore built exclusively around the channel they already use every day — WhatsApp — and the single high-frequency decision that matters most: daily irrigation.



As a solo founder I am executing with high velocity using AI-assisted, spec-driven development (Claude Code + GitHub spec-kit) and the GCP credits from the hackathon. The product is deliberately scoped so that one experienced technical leader can deliver a working, farmer-tested agentic loop before the application deadline.



During incubation I will specifically need two things the program is uniquely positioned to provide:



1\. Agronomic validation of the CropDoctor triage outputs by IAV Hassan II faculty for Moroccan cultivars and local pest pressure.

2\. Access to cooperatives and farm managers to expand beyond the initial 2–3 pilot users.



I am open to adding a complementary co-founder later for go-to-market and cooperative relationships once the technical core is proven.



\## 13. Success Metrics for StartGate Demo



\- One full end-to-end irrigation-recommendation cycle completed with a real pilot farmer.

\- Ideally one real leaf-photo triage completed with a real pilot farmer.

\- A 90–120 second demo video showing the live WhatsApp exchange and a short spoken explanation of the agentic loop.

\- A clear, evidence-backed answer to "have you talked to real farmers?" — even three good conversations, honestly presented, beats a large but shallow batch.



\---



\## 14. Spec-Kit Alignment \& Bootstrap



We're using \[GitHub spec-kit](https://github.com/github/spec-kit) to define what to build \*before\* building it, so that Claude Code implements against an explicit, versioned spec rather than accumulated chat context. This section maps this PRD onto spec-kit's artifacts and gives the exact bootstrap commands.



\### 14.1 How this PRD maps to spec-kit artifacts



| Spec-kit artifact | Sourced from this PRD | Content |

|---|---|---|

| `constitution.md` | Sections 5 (cut list), 11 (risks) | Non-negotiable principles: rule-based logic before LLM reasoning, human-in-the-loop only, no voice/valve/payments in v1, mandatory ONSSA disclaimer on every CropDoctor response, sandbox messaging only |

| `spec.md` (via `/speckit.specify`) | Sections 1, 2, 4, 5 | The \*what and why\*: proactive irrigation recommendation loop + light photo triage, for Hassan persona, with no tech stack detail |

| `plan.md` (via `/speckit.plan`) | Section 6 | The \*how\*: FastAPI on Cloud Run, Meta WhatsApp Cloud API sandbox, Firestore, Open-Meteo, Gemini 1.5 Flash via Vertex AI |

| `tasks.md` (via `/speckit.tasks`) | Section 10 milestones | Broken into dependency-ordered, file-specific tasks — models → services → webhook endpoints, per user story |



\### 14.2 Bootstrap commands



```bash

\# 1. Install the Specify CLI (one-time)

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git



\# 2. Initialize the project, targeting Claude Code as the coding agent

specify init irrigagent --integration claude-code

cd irrigagent



\# 3. Inside Claude Code, run the workflow in order:

\#    /speckit.constitution   -> paste the principles from Section 14.1 above

\#    /speckit.specify        -> paste the "what/why" from Sections 1, 2, 4, 5

\#    /speckit.plan           -> paste the architecture from Section 6

\#    /speckit.tasks          -> let it break Section 10's Week 1 milestone into tasks

\#    /speckit.implement      -> execute tasks in order, checkpointing after each

```



\### 14.3 Suggested constitution.md seed text



```markdown

\# IrrigAgent AI — Project Constitution



1\. Human-in-the-loop only. No automated valve/solenoid control in this phase.

2\. Rule-based decision logic ships first. LLM reasoning is an optional upgrade,

&#x20;  never a dependency for the core loop to function.

3\. Every CropDoctor response must include the ONSSA disclaimer verbatim:

&#x20;  "This is a first-pass triage only. It does not replace advice from a

&#x20;  licensed agronomist or the official product label. Always verify with

&#x20;  ONSSA-authorized products."

4\. Messaging stays on the WhatsApp Cloud API sandbox tier (max 5 verified

&#x20;  numbers) for this phase. No Twilio, no paid messaging vendor, no full

&#x20;  Business Verification until after program selection.

5\. No voice I/O, no payments, no multi-farm scheduling, no sensor integration

&#x20;  in this phase — see PRD Section 5 for the full cut list.

6\. Every feature must be demoable end-to-end with a real WhatsApp number

&#x20;  before it is considered done.

```



Feeding this constitution in first means `/speckit.plan` and `/speckit.implement` won't quietly reintroduce cut scope (e.g. Claude Code deciding voice support would be "nice to add") — the constitution is the guardrail.



\## 15. Day 1 Quick-Start — Project Structure \& Webhook Code



This is the reference implementation to get the send/receive loop working today. Once spec-kit is bootstrapped (Section 14), this becomes the seed that `/speckit.plan` formalizes — start here, then let spec-kit take over structuring the remaining build.



\### 15.1 Project structure



```

irrigagent/

├── app/

│   ├── \_\_init\_\_.py

│   ├── main.py              # FastAPI app, webhook routes

│   ├── config.py             # env var loading

│   ├── whatsapp.py           # send/receive helpers for Meta Cloud API

│   ├── weather.py            # Open-Meteo client

│   ├── decision.py           # rule-based irrigation logic

│   └── firestore\_client.py   # Firestore read/write helpers

├── requirements.txt

├── Dockerfile

├── .env.example

├── .gitignore

└── README.md

```



\### 15.2 requirements.txt



```

fastapi==0.115.0

uvicorn\[standard]==0.30.6

httpx==0.27.2

python-dotenv==1.0.1

google-cloud-firestore==2.19.0

pydantic==2.9.2

```



\### 15.3 app/config.py



```python

import os

from dotenv import load\_dotenv



load\_dotenv()



WHATSAPP\_TOKEN = os.environ\["WHATSAPP\_TOKEN"]              # temporary or permanent token from Meta App Dashboard

WHATSAPP\_PHONE\_NUMBER\_ID = os.environ\["WHATSAPP\_PHONE\_NUMBER\_ID"]  # from the sandbox test number

VERIFY\_TOKEN = os.environ\["VERIFY\_TOKEN"]                  # any string you choose, used for webhook handshake

GRAPH\_API\_VERSION = os.environ.get("GRAPH\_API\_VERSION", "v20.0")

GCP\_PROJECT\_ID = os.environ\["GCP\_PROJECT\_ID"]

```



\### 15.4 app/whatsapp.py



```python

import httpx

from app.config import WHATSAPP\_TOKEN, WHATSAPP\_PHONE\_NUMBER\_ID, GRAPH\_API\_VERSION



GRAPH\_URL = f"https://graph.facebook.com/{GRAPH\_API\_VERSION}/{WHATSAPP\_PHONE\_NUMBER\_ID}/messages"



async def send\_text\_message(to: str, body: str) -> dict:

&#x20;   """Send a plain text WhatsApp message to a verified sandbox number."""

&#x20;   headers = {

&#x20;       "Authorization": f"Bearer {WHATSAPP\_TOKEN}",

&#x20;       "Content-Type": "application/json",

&#x20;   }

&#x20;   payload = {

&#x20;       "messaging\_product": "whatsapp",

&#x20;       "to": to,

&#x20;       "type": "text",

&#x20;       "text": {"body": body},

&#x20;   }

&#x20;   async with httpx.AsyncClient(timeout=15) as client:

&#x20;       resp = await client.post(GRAPH\_URL, headers=headers, json=payload)

&#x20;       resp.raise\_for\_status()

&#x20;       return resp.json()





def extract\_incoming\_message(payload: dict) -> dict | None:

&#x20;   """Pull the sender number + message text out of a webhook POST body.

&#x20;   Returns None if the payload isn't a user message (e.g. a status update)."""

&#x20;   try:

&#x20;       entry = payload\["entry"]\[0]

&#x20;       change = entry\["changes"]\[0]\["value"]

&#x20;       messages = change.get("messages")

&#x20;       if not messages:

&#x20;           return None  # status callback, not an incoming message

&#x20;       msg = messages\[0]

&#x20;       return {

&#x20;           "from": msg\["from"],

&#x20;           "type": msg\["type"],

&#x20;           "text": msg.get("text", {}).get("body"),

&#x20;           "image\_id": msg.get("image", {}).get("id"),

&#x20;       }

&#x20;   except (KeyError, IndexError):

&#x20;       return None

```



\### 15.5 app/main.py



```python

from fastapi import FastAPI, Request, Response, Query

from app.config import VERIFY\_TOKEN

from app.whatsapp import send\_text\_message, extract\_incoming\_message

from app.weather import get\_et0\_forecast

from app.decision import recommend\_irrigation

from app.firestore\_client import get\_farm\_profile, log\_interaction



app = FastAPI()





@app.get("/webhook")

async def verify\_webhook(

&#x20;   hub\_mode: str = Query(alias="hub.mode"),

&#x20;   hub\_verify\_token: str = Query(alias="hub.verify\_token"),

&#x20;   hub\_challenge: str = Query(alias="hub.challenge"),

):

&#x20;   """Meta calls this once when you register the webhook URL."""

&#x20;   if hub\_mode == "subscribe" and hub\_verify\_token == VERIFY\_TOKEN:

&#x20;       return Response(content=hub\_challenge, media\_type="text/plain")

&#x20;   return Response(status\_code=403)





@app.post("/webhook")

async def receive\_message(request: Request):

&#x20;   """Meta calls this every time a test number sends a message."""

&#x20;   payload = await request.json()

&#x20;   incoming = extract\_incoming\_message(payload)

&#x20;   if incoming is None:

&#x20;       return {"status": "ignored"}



&#x20;   sender = incoming\["from"]

&#x20;   text = (incoming.get("text") or "").strip()



&#x20;   farm = await get\_farm\_profile(sender)



&#x20;   if text == "1":

&#x20;       reply = "Approved. Irrigation adjustment applied for tomorrow."

&#x20;   elif text == "2":

&#x20;       reply = "Understood, skipping today's adjustment."

&#x20;   elif text == "3":

&#x20;       reply = "Reply with your preferred adjustment (e.g. '+10 min at 06:00')."

&#x20;   else:

&#x20;       et0 = await get\_et0\_forecast(farm.get("location"))

&#x20;       recommendation = recommend\_irrigation(et0, farm)

&#x20;       reply = (

&#x20;           f"{recommendation}\\n\\n"

&#x20;           "Reply 1 to approve, 2 to skip today, or 3 to modify."

&#x20;       )



&#x20;   await send\_text\_message(sender, reply)

&#x20;   await log\_interaction(sender, incoming, reply)

&#x20;   return {"status": "ok"}

```



\### 15.6 app/weather.py



```python

import httpx



OPEN\_METEO\_URL = "https://api.open-meteo.com/v1/forecast"



async def get\_et0\_forecast(location: dict | None) -> float | None:

&#x20;   """location = {'lat': ..., 'lon': ...}. Returns tomorrow's ET0 (mm), or None if unavailable."""

&#x20;   if not location:

&#x20;       return None

&#x20;   params = {

&#x20;       "latitude": location\["lat"],

&#x20;       "longitude": location\["lon"],

&#x20;       "daily": "et0\_fao\_evapotranspiration",

&#x20;       "forecast\_days": 2,

&#x20;       "timezone": "Africa/Casablanca",

&#x20;   }

&#x20;   async with httpx.AsyncClient(timeout=10) as client:

&#x20;       resp = await client.get(OPEN\_METEO\_URL, params=params)

&#x20;       resp.raise\_for\_status()

&#x20;       data = resp.json()

&#x20;       try:

&#x20;           return data\["daily"]\["et0\_fao\_evapotranspiration"]\[1]  # tomorrow

&#x20;       except (KeyError, IndexError):

&#x20;           return None

```



\### 15.7 app/decision.py



```python

def recommend\_irrigation(et0: float | None, farm: dict) -> str:

&#x20;   """Plain rule-based logic. No LLM dependency for the core loop."""

&#x20;   if et0 is None:

&#x20;       return "Could not fetch tomorrow's forecast — keeping your usual schedule."

&#x20;   if et0 > 6.0:

&#x20;       return f"High evapotranspiration expected tomorrow ({et0:.1f} mm). Recommended: increase irrigation by +15 min."

&#x20;   if et0 < 2.5:

&#x20;       return f"Low evapotranspiration expected tomorrow ({et0:.1f} mm). Recommended: reduce irrigation by -10 min."

&#x20;   return f"Normal conditions expected tomorrow ({et0:.1f} mm). Recommended: keep today's schedule."

```



\### 15.8 app/firestore\_client.py



```python

from google.cloud import firestore

from app.config import GCP\_PROJECT\_ID



db = firestore.AsyncClient(project=GCP\_PROJECT\_ID)



async def get\_farm\_profile(phone\_number: str) -> dict:

&#x20;   doc = await db.collection("farms").document(phone\_number).get()

&#x20;   return doc.to\_dict() or {}



async def log\_interaction(phone\_number: str, incoming: dict, reply: str) -> None:

&#x20;   await db.collection("farms").document(phone\_number).collection("messages").add({

&#x20;       "incoming": incoming,

&#x20;       "reply": reply,

&#x20;       "timestamp": firestore.SERVER\_TIMESTAMP,

&#x20;   })

```



\### 15.9 .env.example



```

WHATSAPP\_TOKEN=your\_meta\_temporary\_or\_permanent\_token

WHATSAPP\_PHONE\_NUMBER\_ID=your\_sandbox\_phone\_number\_id

VERIFY\_TOKEN=choose\_any\_string\_here

GRAPH\_API\_VERSION=v20.0

GCP\_PROJECT\_ID=your-gcp-project-id

```



\### 15.10 Dockerfile (for Cloud Run)



```dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD \["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

```



\### 15.11 Deploy to Cloud Run



```bash

gcloud run deploy irrigagent \\

&#x20; --source . \\

&#x20; --region europe-west1 \\

&#x20; --allow-unauthenticated \\

&#x20; --set-env-vars WHATSAPP\_TOKEN=...,WHATSAPP\_PHONE\_NUMBER\_ID=...,VERIFY\_TOKEN=...,GCP\_PROJECT\_ID=...

```



Then, in the Meta App Dashboard, register `https://<your-cloud-run-url>/webhook` as the webhook callback URL, using the same `VERIFY\_TOKEN` from your `.env`.



\*\*Definition of done for Day 1:\*\* send a WhatsApp message from a verified test number to the sandbox number and receive a rule-based irrigation recommendation back, with reply handling for 1/2/3 working. Nothing else needs to work yet.



\## 16. Appel à Candidatures — Submission Narrative



Ready-to-paste content for the StartGate application form fields. Written in English for drafting speed — translate to French before submitting, since the portal and reviewer panel operate primarily in French.



\*\*Nom du projet / Product name:\*\* IrrigAgent (AI)



\*\*Problème (Problem):\*\*

Small and medium Moroccan farms lose water and yield to reactive, intuition-based irrigation, while national modernization programs have largely bypassed smallholders. Existing AgTech tools require dashboard engagement this segment won't adopt.



\*\*Solution:\*\*

A WhatsApp-native AI agent that sends farmers a daily irrigation recommendation, driven by live weather and evapotranspiration data, approved with a one-tap reply. A lightweight companion feature lets farmers photograph a sick leaf for a first-pass diagnosis, with treatment guidance limited to ONSSA-authorized products and a clear non-prescriptive disclaimer.



\*\*Marché cible (Target market):\*\* Small and medium farms (5–20 ha) and agricultural cooperatives in Morocco's irrigation-intensive regions (e.g. Souss-Massa, Agadir).



\*\*Modèle économique (Business model):\*\* Cooperative subscription as the primary channel (co-ops already aggregate smallholder relationships and billing), with a freemium tier for individual farmers and medium-term B2B2F potential with input suppliers and crop insurers. Currently a hypothesis, being pressure-tested with real farmer/cooperative conversations ahead of submission.



\*\*Stade d'avancement (Stage):\*\* Idea-stage, solo founder, pre-pilot. Technical build in progress on a spec-driven development workflow (GitHub spec-kit); pilot with 2–3 real farmers targeted before the application deadline, using a free WhatsApp Cloud API sandbox — no infrastructure spend required beyond the $10,000 in GCP credits already secured via a Gemini hackathon win.



\*\*Équipe (Team):\*\* Solo founder — Agile Coach with a background as Technical Leader and IT Manager, international experience across France, Switzerland, and remote teams. No formal agronomy background; addressing that explicitly through the IAV Hassan II partnership requested below, rather than overclaiming expertise.



\*\*Alignement avec Génération Green:\*\* Directly targets the resource-efficiency and rural-development goals of Génération Green 2020–2030, focused on the smallholder segment historically underserved by prior irrigation modernization programs.



\*\*Ce que nous demandons au programme (The ask):\*\*

1\. Agronomic validation of CropDoctor's diagnostic outputs from IAV Hassan II faculty, specific to Moroccan cultivars and pest pressure.

2\. Support exploring structured access to the ONSSA-authorized product register.

3\. Mentorship on cooperative go-to-market and pricing.

4\. Network access to cooperatives and farm managers to expand the pilot beyond the initial 2–3 users.



\*\*Preuve d'exécution (Evidence of execution):\*\* \[Insert once available — screen recording of a live WhatsApp irrigation-recommendation exchange with a real farmer, plus 2–3 quotes from farmer/cooperative conversations.]



\---



\*Prepared for StartGate Agri-Food Tech Incubator — 5th Cohort application. This single document now serves as the PRD, the spec-kit bootstrap reference, the Day 1 build guide, and the source for the appel à candidatures submission fields.\*

