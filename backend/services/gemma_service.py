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
        prompt = f"""You are the classification engine for NyayaPath, a civic-rights
navigator for citizens in India.

Analyze the citizen's message and return ONLY valid JSON.

The JSON must have exactly these fields:

{{
  "category": "string",
  "intent": "string",
  "language": "string",
  "missing_information": ["string"]
}}

Rules:
- category should identify the broad civic/legal issue.
- intent should identify what the citizen wants or needs.
- language should be "en" for English or "hi" for Hindi.
- missing_information should contain information that would be useful
  to give the citizen a more specific answer.
- Do not provide legal advice.
- Do not add explanations outside the JSON.

Citizen message:
{message}

Detected/requested language:
{language}
"""
        raw_response = self.generate(
            prompt = prompt,
            temperature=0.1,
            max_tokens = 300,
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
            prompt =  prompt,
            temperature=0.2,
            max_tokens = 700,
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
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)

gemma_service = GemmaService()
