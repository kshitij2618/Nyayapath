# NyayaPath — Frontend (Member 2)

Streamlit implementation of the frozen frontend layout:
`input → advice → [questions → anything_else] → result → draft`

## 1. Run it right now (no backend needed)

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

It opens with `USE_MOCK = True` (default), so every screen — including the
conditional result sections and the generated draft — works standalone using
realistic fake data in `services/api_client.py`. Try typing something with
"deposit"/"landlord" vs "RTI" vs anything else — the mock layer fakes
Gemma's classification just enough to show all three result shapes
(tenant / RTI / generic civic with no document section).

## 2. Folder structure

```
frontend/
├── app.py                     # header, footer, stage router
├── components/
│   ├── input_form.py          # landing screen
│   ├── advice_view.py         # initial understanding screen
│   ├── question_view.py       # optional follow-up questions (>=3)
│   ├── anything_else_view.py  # optional free-text screen
│   ├── result_view.py         # final result, conditional sections
│   └── draft_view.py          # generated document, edit/copy/download
├── services/
│   └── api_client.py          # THE ONLY file that talks to the backend
└── utils/
    ├── state.py                # session_state defaults + stage machine
    └── i18n.py                 # English/Hindi UI string labels
```

## 3. Connecting to the real backend

When Member 1's FastAPI endpoints are ready:

1. Confirm the exact request/response field names against the contract
   documented at the top of `services/api_client.py`.
2. Set:
   ```bash
   export NYAYAPATH_USE_MOCK=0
   export NYAYAPATH_BACKEND_URL=http://localhost:8000
   ```
3. Don't touch the components — they only ever call functions in
   `api_client.py`, so switching from mock to real data is a one-file change.
4. Each `api_client.py` function still falls back to mock data on a failed
   request. Remove that fallback once the backend is stable if you want
   failures to surface loudly instead.

## 4. Why the flow is built this way (mirrors the frozen spec)

- **Never shows every result section.** `result_view.py` only renders a
  card if the backend/mock returned data for it (e.g. no "Document" card
  for a generic civic issue, no "Escalation" card unless relevant).
- **Never fabricates a law.** If `analysis["laws_found"]` is `False`,
  `advice_view.py` shows an honest "not confident yet" message instead of
  inventing a rule.
- **At least 3 follow-up questions, never padded.** `question_view.py`
  asserts this at render time as a guardrail during development.
- **"Anything else" is always optional** — no validation blocks continuing
  with it empty.
- **Header stays minimal** — no login/profile/dashboard, per the frozen
  spec, unless a later requirement explicitly needs one.

## 5. Known MVP shortcuts (intentional, per the 4-day scope freeze)

- "Copy" uses `st.popover` + `st.code` (built-in copy icon) instead of a
  custom JS clipboard component.
- "Download" currently exports plain text. Swap the `download_button` data
  for the PDF bytes Member 1's `/generate-draft` (ReportLab) endpoint
  returns once it exists.
- Evidence checklist checkboxes are local UI state only — nothing is
  persisted, which matches "avoid unnecessary database complexity" from
  the project brief.
