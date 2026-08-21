import httpx

LLAMA_SERVER_URL = "http://127.0.0.1:8080"

class GemmaService:
    def __init__(self,server_url: str = LLAMA_SERVER_URL):
        self.server_url = server_url.rstrip("/")

    def health_check(self) -> bool:
        try:
            response = httpx.get(
                f"{self.server_url}/health",
                timeout = 5.0,
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def generate(
            self,
            prompt: str,
            temperature: float =0.1,
            max_tokens: int = 600,
    ) -> str:
        payload = {"prompt":prompt,
                   "temperature": temperature,
                   "n_predict": max_tokens,
        }
        response = httpx.post(
            f"{self.server_url}/completion",
            json=payload,
            timeout = 120.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("content", "")

    def analyze_citizen_message(
        self,
        message: str,
        language: str = "en",
    ) -> dict:

        prompt = f"""You are the classification and initial-response engine
for NyayaPath, a civic-rights navigator for citizens in India.

Your job is to understand the citizen's problem and produce a
structured preliminary analysis.

IMPORTANT ARCHITECTURE RULE:
You are NOT the final decision-maker for workflows.
Do not select, invent, or recommend a workflow ID.
The backend's deterministic workflow engine will decide whether
a supported workflow applies.

Your responsibilities are ONLY:
1. Understand the citizen's message.
2. Identify the broad issue category.
3. Identify the citizen's intent.
4. Detect the language.
5. Give a short, cautious initial explanation.
6. Identify information that is missing and could materially improve
   the result.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
  "category": "string",
  "intent": "string",
  "language": "string",
  "initial_advice": "string",
  "missing_information": ["string"]
}}

FIELD RULES:

1. category
- Describe the broad civic/legal problem.
- Use a concise, meaningful category.
- Examples:
  - "RTI / access to government information"
  - "tenant security deposit dispute"
  - "consumer grievance"
  - "employment grievance"
  - "police complaint"
  - "identity/document issue"
- Do not invent a highly specific legal category when the message
  does not contain enough information.

2. intent
- Describe what the citizen is trying to achieve.
- Examples:
  - "obtain government records"
  - "recover withheld security deposit"
  - "file a complaint"
  - "understand available options"
  - "draft an application"
- Focus on the citizen's actual objective, not assumptions.

3. language
- Return "en" for English.
- Return "hi" for Hindi.
- If the message mixes Hindi and English, choose the dominant
  language.
- Do not translate the user's message unless necessary to understand it.

4. initial_advice
- Give a short preliminary response in the detected language.
- Keep it practical and easy to understand.
- Explain what the citizen may consider doing next.
- Mention useful evidence or documents only when reasonably
  supported by the user's message.
- Clearly avoid presenting uncertain information as a fact.
- Do not claim that the citizen will win, receive compensation,
  obtain a document, or get a particular legal outcome.
- Do not provide a final workflow recommendation.
- Do not provide specific legal sections unless they are explicitly
  present in the user's message.
- Do not invent deadlines, fees, authorities, websites, portals,
  procedures, or legal rights.

5. missing_information
- Return a JSON array of concise pieces of information that would
  materially improve the analysis.
- Include only information that is genuinely relevant.
- Do not ask for information that is already clearly provided.
- Do not include unnecessary personal information.
- Prioritize information needed to determine the applicable
  jurisdiction, procedure, documents, or next step.
- Examples:
  [
    "state where the issue occurred",
    "name of the concerned government department",
    "date the tenancy ended",
    "amount of security deposit",
    "whether a written agreement exists"
  ]
- If the available information is already sufficient for a
  preliminary result, return an empty array.

GENERAL RULES:

- Do not fabricate facts.
- Do not assume facts that the citizen did not provide.
- Do not fabricate laws or legal provisions.
- Do not fabricate authorities.
- Do not fabricate URLs.
- Do not fabricate fees or deadlines.
- Do not make a final legal determination.
- Do not claim to be a lawyer or legal authority.
- Do not expose internal reasoning.
- Do not include markdown.
- Do not include ```json or code fences.
- Do not add any text before or after the JSON.
- Ensure the response is valid JSON that can be parsed directly
  by Python's json.loads().
- Keep the response concise.

IMPORTANT DISTINCTION:

The following are classification tasks:
- category
- intent
- language
- missing information

The following is only preliminary guidance:
- initial_advice

The following are NOT your responsibility:
- selecting a workflow
- deciding whether a workflow is supported
- selecting authorities from the database
- selecting official sources from the database
- deciding which documents are required
- deciding escalation paths

Those decisions are handled deterministically by NyayaPath's
backend workflow and retrieval services.

CITIZEN MESSAGE:
{message}

DETECTED / REQUESTED LANGUAGE:
{language}
"""
        raw_response = self.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=450,
        )

        return self._parse_json_response(raw_response)

    def generate_draft(
        self,
        category: str,
        information: dict,
        language: str = "en",
    ) -> dict:
        import json

        prompt = f"""You are the drafting engine for NyayaPath, a civic-rights
navigator for citizens in India.

Generate a simple formal civic/legal document draft based on
the information provided.

Return ONLY valid JSON with exactly these fields:

{{
  "title": "string",
  "content": "string",
  "language": "string"
}}

Rules:
- Write in clear, simple language.
- Do not invent facts.
- Use only the information supplied.
- Do not provide legal advice.
- Do not claim that the document guarantees any legal outcome.
- The document should be suitable as a starting draft that a citizen
  can review before submitting.
- language must be "en" or "hi".

Category:
{category}

Information:
{json.dumps(information, ensure_ascii=False)}

Requested language:
{language}
"""

        raw_response = self.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=700,
        )

        return self._parse_json_response(raw_response)

    @staticmethod
    def _parse_json_response(raw_response: str) -> dict:
        import json

        text = raw_response.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        return json.loads(text)


gemma_service = GemmaService()