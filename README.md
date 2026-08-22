# NYAYPATH

### AI-Powered Legal Guidance & Navigation Platform

NYAYPATH is an AI-powered platform designed to make legal information and problem navigation simpler and more accessible.

Users can describe their problem in natural language without needing to know the relevant law, legal terminology, or authority. NYAYPATH analyzes the problem, identifies the relevant category and intent, connects it with structured legal workflows and sources, and provides progressively refined guidance.

> **Describe your problem → Understand it → Find the relevant path → Get informed guidance**

---

## Why NYAYPATH?

Legal systems can be difficult to navigate for people who do not know:

* Which law or rule applies
* Which authority they should approach
* What information is important
* What their next step should be
* How to explain their problem formally

NYAYPATH aims to bridge this gap by combining **AI, structured workflows, legal sources, authority information, and guided information collection** into a single user-friendly platform.

It is designed to be more than a generic AI chatbot: the system follows structured workflows so that legal guidance can be more consistent, explainable, and actionable.

---

## How It Works

```text
User describes problem
        ↓
AI understands the problem
        ↓
Category & intent identification
        ↓
Relevant legal workflow
        ↓
Relevant sources / authorities
        ↓
Initial guidance
        ↓
Additional information
        ↓
Refined analysis
        ↓
Action-oriented guidance / draft
```

The user can start with a simple description and progressively provide more information when a more accurate result is needed.

---

## Key Features

* 🧠 Natural-language problem understanding
* ⚖️ Structured legal workflows
* 📚 Legal sources and references
* 🏛️ Authority information
* 🔍 Missing-information detection
* 💬 Progressive information collection
* 📝 AI-assisted draft generation
* 🌐 Multilingual support architecture
* 🔄 Initial and refined analysis
* 🎯 Action-oriented legal guidance
* 🧩 Modular and scalable architecture

---

## Example

A user might say:

> "I bought a phone online and it stopped working shortly after delivery. The seller refuses to replace it."

NYAYPATH can identify the problem as a potential **consumer grievance**, determine the user's likely objective, identify relevant information, and guide the user through the appropriate workflow.

The user does not need to know the applicable law before starting.

---

## Technology Stack

* **Python**
* **Streamlit**
* **Gemma / AI model integration**
* **Structured JSON data**
* **Workflow-based processing**
* **Vector-based retrieval**
* **Git & GitHub**

---

## Project Structure

```text
nyayapath/
│
├── backend/              # Backend services, APIs and workflow logic
├── frontend/             # Streamlit user interface
├── model/                # AI / model integration
├── vectorstore/          # Retrieval and knowledge-store components
├── docs/                 # Technical and project documentation
├── screenshots/          # UI and project screenshots
├── tests/                # Automated tests
│
├── .env.example          # Environment configuration template
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
└── run.py                # Application runner
```

The architecture is intentionally modular so that new legal workflows, sources, languages, AI capabilities, and frontend features can be added as the project grows.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd nyayapath
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables using:

```text
.env
```

Use `.env.example` as the configuration reference.

---

## Running the Application

Start NYAYPATH using the project's runner:

```bash
python run.py
```

If the project is configured to run directly through Streamlit, the frontend can also be started using the appropriate Streamlit entry point.

---

## Future Development

NYAYPATH is designed with future expansion in mind.

Planned and possible areas of development include:

* More legal workflows
* Expanded legal and government sources
* Additional Indian languages
* Improved legal-document retrieval
* Larger and better-maintained vector knowledge bases
* More authority and process recommendations
* Document and evidence assistance
* Improved draft generation
* Better explainability
* Automated workflow testing
* User history and case tracking
* Production deployment and scaling
* Accessibility improvements

The `backend`, `frontend`, `model`, `vectorstore`, `docs`, and `tests` layers are maintained as separate components to support this future expansion.

---

## Vision

NYAYPATH aims to make the first step toward understanding a legal problem easier.

Instead of asking:

> **"Which law applies to me?"**

a user can simply say:

> **"This is what happened."**

NYAYPATH then helps transform that real-world problem into a structured and understandable path forward.

---

## Disclaimer

NYAYPATH provides **AI-assisted legal information and guidance** and is not a substitute for professional legal advice.

AI-generated results may be incomplete or inaccurate. Important legal matters should be verified using authoritative sources or with a qualified legal professional.

---

## Project Status

**Active Development**

NYAYPATH is being developed as a scalable legal-guidance platform with an emphasis on structured workflows, AI-assisted analysis, accessibility, and future expansion.

---

### NYAYPATH

**Understand your problem.
Understand your options.
Take the next informed step.**
