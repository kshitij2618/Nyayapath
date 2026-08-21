import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================
# PATHS
# =============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

WORKFLOWS_FILE = DATA_DIR / "workflows.json"
AUTHORITIES_FILE = DATA_DIR / "authorities.json"
SOURCES_FILE = DATA_DIR / "sources.json"


# =============================================================
# WORKFLOW SERVICE
# =============================================================

class WorkflowService:
    """
    Deterministic workflow/decision layer for NyayaPath.

    Gemma is responsible for:
        - category
        - intent
        - language
        - initial advice
        - missing information

    WorkflowService is responsible for:
        - normalising Gemma output
        - matching workflow_data
        - workflow selection
        - follow-up questions
        - maximum 3 follow-up questions
        - documents
        - evidence
        - authorities
        - legal sources
        - action plans
        - escalation
        - fallback behavior

    The service supports the current workflows.json structure.
    """

    MAX_FOLLOW_UP_QUESTIONS = 3

    SUPPORTED_LANGUAGES = {
        "en",
        "hi",
    }

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(self):

        self.workflows_data = self._load_json(
            WORKFLOWS_FILE
        )

        self.authorities_data = self._load_json(
            AUTHORITIES_FILE
        )

        self.sources_data = self._load_json(
            SOURCES_FILE
        )

        # -----------------------------------------------------
        # Raw workflow data
        # -----------------------------------------------------

        self.raw_workflow_data = self.workflows_data.get(
            "workflow_data",
            [],
        )

        if not isinstance(
            self.raw_workflow_data,
            list,
        ):
            self.raw_workflow_data = []

        # -----------------------------------------------------
        # Authorities
        # -----------------------------------------------------

        self.authorities = self.authorities_data.get(
            "authorities",
            [],
        )

        if not isinstance(
            self.authorities,
            list,
        ):
            self.authorities = []

        # -----------------------------------------------------
        # Sources
        # -----------------------------------------------------

        self.sources = self.sources_data.get(
            "sources",
            [],
        )

        if not isinstance(
            self.sources,
            list,
        ):
            self.sources = []

        # -----------------------------------------------------
        # Convert workflow_data into searchable workflows.
        # -----------------------------------------------------

        self.workflows = (
            self._normalise_workflow_data(
                self.raw_workflow_data
            )
        )

    # =========================================================
    # JSON LOADING
    # =========================================================

    @staticmethod
    def _load_json(
        path: Path,
    ) -> Dict[str, Any]:

        try:

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

                if isinstance(
                    data,
                    dict,
                ):
                    return data

                return {}

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            return {}

    # =========================================================
    # BASIC NORMALISATION
    # =========================================================

    @staticmethod
    def _normalise(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return re.sub(
            r"\s+",
            " ",
            str(value).strip().lower(),
        )

    # =========================================================
    # SLUG
    # =========================================================

    @classmethod
    def _slug(
        cls,
        value: Any,
    ) -> str:

        value = cls._normalise(
            value
        )

        value = re.sub(
            r"[^a-z0-9]+",
            "_",
            value,
        )

        return value.strip("_")

    # =========================================================
    # LANGUAGE
    # =========================================================

    @classmethod
    def _safe_language(
        cls,
        language: Optional[str],
    ) -> str:

        language = cls._normalise(
            language
        )

        if language in cls.SUPPORTED_LANGUAGES:
            return language

        return "en"

    # =========================================================
    # LOCALIZED VALUE
    # =========================================================

    def _localized(
        self,
        value: Any,
        language: str = "en",
        default: Optional[str] = "",
    ) -> Optional[str]:

        if isinstance(
            value,
            str,
        ):
            return value

        if not isinstance(
            value,
            dict,
        ):
            return default

        language = self._safe_language(
            language
        )

        # Requested language
        result = value.get(
            language
        )

        if result:
            return str(result)

        # English fallback
        result = value.get(
            "en"
        )

        if result:
            return str(result)

        # Hindi fallback
        result = value.get(
            "hi"
        )

        if result:
            return str(result)

        return default

    # =========================================================
    # CATEGORY NORMALISATION
    # =========================================================

    @classmethod
    def _normalise_category(
        cls,
        category: Any,
    ) -> str:

        value = cls._normalise(
            category
        )

        aliases = {

            "tenant security deposit dispute":
                "tenant/security deposit",

            "tenant security deposit":
                "tenant/security deposit",

            "tenant deposit dispute":
                "tenant/security deposit",

            "security deposit dispute":
                "tenant/security deposit",

            "rti":
                "rti",

            "right to information":
                "rti",

            "right to information act":
                "rti",

            "rti access to government information":
                "rti",

            "rti / access to government information":
                "rti",
        }

        return aliases.get(
            value,
            value,
        )

    # =========================================================
    # INTENT NORMALISATION
    # =========================================================

    @classmethod
    def _normalise_intent(
        cls,
        intent: Any,
    ) -> str:

        value = cls._normalise(
            intent
        )

        aliases = {

            "recover withheld security deposit":
                "deposit_withheld_no_reason",

            "recover security deposit":
                "deposit_withheld_no_reason",

            "security deposit withheld":
                "deposit_withheld_no_reason",

            "landlord withheld security deposit":
                "deposit_withheld_no_reason",

            "deposit not returned":
                "deposit_delayed",

            "security deposit delayed":
                "deposit_delayed",

            "deposit return delayed":
                "deposit_delayed",

            "partial security deposit deduction":
                "deposit_partial_deduction_dispute",

            "disputed deposit deduction":
                "deposit_partial_deduction_dispute",

            "deposit deduction dispute":
                "deposit_partial_deduction_dispute",

            "general security deposit rules":
                "general_deposit_rules_query",

            "security deposit rules":
                "general_deposit_rules_query",

            "no written rental agreement":
                "no_written_agreement",

            "verbal rental agreement":
                "no_written_agreement",
        }

        return aliases.get(
            value,
            value,
        )

    # =========================================================
    # WORKFLOW DATA ADAPTER
    # =========================================================

    def _normalise_workflow_data(
        self,
        workflow_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        normalised_workflows = []

        for category_block in workflow_data:

            if not isinstance(
                category_block,
                dict,
            ):
                continue

            raw_category = category_block.get(
                "category",
                "",
            )

            canonical_category = (
                self._normalise_category(
                    raw_category
                )
            )

            intents = category_block.get(
                "intents",
                [],
            )

            if not isinstance(
                intents,
                list,
            ):
                continue

            # -------------------------------------------------
            # Create one internal workflow per intent.
            # -------------------------------------------------

            for intent_data in intents:

                if not isinstance(
                    intent_data,
                    dict,
                ):
                    continue

                intent_id = intent_data.get(
                    "id",
                    "",
                )

                if not intent_id:
                    continue

                canonical_intent = (
                    self._normalise_intent(
                        intent_id
                    )
                )

                workflow_id = str(
                    canonical_intent
                )

                workflow = {

                    "id":
                        workflow_id,

                    "category":
                        raw_category,

                    "canonical_category":
                        canonical_category,

                    "intent":
                        canonical_intent,

                    "description": {
                        "en":
                            intent_data.get(
                                "description",
                                "",
                            ),
                    },

                    "name": {
                        "en":
                            raw_category,

                        "hi":
                            raw_category,
                    },

                    # -----------------------------------------
                    # Workflow data
                    # -----------------------------------------

                    "questions":
                        category_block.get(
                            "questions",
                            [],
                        ),

                    "legal_support":
                        category_block.get(
                            "legal_support",
                            [],
                        ),

                    "actions":
                        category_block.get(
                            "actions",
                            [],
                        ),

                    "evidence":
                        category_block.get(
                            "evidence",
                            [],
                        ),

                    "escalation":
                        category_block.get(
                            "escalation",
                            [],
                        ),

                    "documents":
                        category_block.get(
                            "documents",
                            {},
                        ),

                    "sources":
                        category_block.get(
                            "sources",
                            [],
                        ),

                    "initial_advice":
                        category_block.get(
                            "initial_advice",
                            {},
                        ),

                    "disclaimer":
                        category_block.get(
                            "disclaimer",
                            {},
                        ),

                    "out_of_scope_examples":
                        category_block.get(
                            "out_of_scope_examples",
                            [],
                        ),

                    # -----------------------------------------
                    # Internal aliases
                    # -----------------------------------------

                    "intent_description":
                        intent_data.get(
                            "description",
                            "",
                        ),
                }

                normalised_workflows.append(
                    workflow
                )

        return normalised_workflows

    # =========================================================
    # WORKFLOW TEXT
    # =========================================================

    def _workflow_text(
        self,
        workflow: Dict[str, Any],
    ) -> str:

        parts: List[str] = []

        parts.append(
            workflow.get(
                "id",
                "",
            )
        )

        parts.append(
            workflow.get(
                "category",
                "",
            )
        )

        parts.append(
            workflow.get(
                "canonical_category",
                "",
            )
        )

        parts.append(
            workflow.get(
                "intent",
                "",
            )
        )

        parts.append(
            workflow.get(
                "intent_description",
                "",
            )
        )

        description = workflow.get(
            "description",
            {},
        )

        if isinstance(
            description,
            dict,
        ):

            parts.extend(
                description.values()
            )

        elif description:

            parts.append(
                description
            )

        return self._normalise(
            " ".join(
                str(part)
                for part in parts
                if part is not None
            )
        )

    # =========================================================
    # FIND WORKFLOW
    # =========================================================

    def _find_workflow(
        self,
        category: str,
        intent: str,
        message: str,
    ) -> Optional[Dict[str, Any]]:

        raw_category = self._normalise(
            category
        )

        raw_intent = self._normalise(
            intent
        )

        category_normalised = (
            self._normalise_category(
                category
            )
        )

        intent_normalised = (
            self._normalise_intent(
                intent
            )
        )

        # -----------------------------------------------------
        # Exact category + intent
        # -----------------------------------------------------

        for workflow in self.workflows:

            workflow_category = (
                self._normalise_category(
                    workflow.get(
                        "category",
                        "",
                    )
                )
            )

            workflow_intent = (
                self._normalise_intent(
                    workflow.get(
                        "intent",
                        "",
                    )
                )
            )

            if (
                workflow_category
                == category_normalised
                and
                workflow_intent
                == intent_normalised
            ):

                return workflow

        # -----------------------------------------------------
        # Exact intent
        # -----------------------------------------------------

        for workflow in self.workflows:

            workflow_intent = (
                self._normalise_intent(
                    workflow.get(
                        "intent",
                        "",
                    )
                )
            )

            if (
                workflow_intent
                and
                workflow_intent
                == intent_normalised
            ):

                return workflow

        # -----------------------------------------------------
        # Scoring fallback
        # -----------------------------------------------------

        best_workflow = None
        best_score = 0

        message_words = set(
            re.findall(
                r"[a-z0-9]+",
                self._normalise(
                    message
                ),
            )
        )

        for workflow in self.workflows:

            if not isinstance(
                workflow,
                dict,
            ):
                continue

            score = 0

            workflow_id = self._normalise(
                workflow.get(
                    "id",
                    "",
                )
            )

            workflow_text = self._workflow_text(
                workflow
            )

            workflow_category = (
                self._normalise_category(
                    workflow.get(
                        "category",
                        "",
                    )
                )
            )

            workflow_intent = (
                self._normalise_intent(
                    workflow.get(
                        "intent",
                        "",
                    )
                )
            )

            # Exact workflow ID
            if (
                workflow_id
                and
                workflow_id
                == intent_normalised
            ):
                score += 20

            # Category
            if (
                workflow_category
                == category_normalised
            ):
                score += 10

            elif (
                category_normalised
                and
                category_normalised
                in workflow_text
            ):
                score += 4

            # Intent
            if (
                workflow_intent
                == intent_normalised
            ):
                score += 12

            elif (
                intent_normalised
                and
                intent_normalised
                in workflow_text
            ):
                score += 5

            # Original values
            if (
                raw_category
                and
                raw_category
                in workflow_text
            ):
                score += 3

            if (
                raw_intent
                and
                raw_intent
                in workflow_text
            ):
                score += 3

            # Message keywords
            workflow_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    workflow_text,
                )
            )

            common_words = (
                message_words
                &
                workflow_words
            )

            score += min(
                len(common_words),
                5,
            )

            if score > best_score:

                best_score = score
                best_workflow = workflow

        # -----------------------------------------------------
        # Reject weak accidental matches
        # -----------------------------------------------------

        if best_score < 8:
            return None

        return best_workflow

    # =========================================================
    # ANSWER HELPERS
    # =========================================================

    @staticmethod
    def _answer_text(
        answers: Dict[str, Any],
        question_id: str,
    ) -> str:

        value = answers.get(
            question_id
        )

        if value is None:
            return ""

        if isinstance(
            value,
            bool,
        ):

            return (
                "yes"
                if value
                else "no"
            )

        if isinstance(
            value,
            list,
        ):

            return ", ".join(
                str(item)
                for item in value
            ).strip()

        if isinstance(
            value,
            dict,
        ):

            return json.dumps(
                value,
                ensure_ascii=False,
            )

        return str(
            value
        ).strip()

    # =========================================================
    # QUESTION ANSWER DETECTION
    # =========================================================

    def _question_is_answered(
        self,
        question: Dict[str, Any],
        answers: Dict[str, Any],
        message: str,
    ) -> bool:

        question_id = question.get(
            "id",
            "",
        )

        # -----------------------------------------------------
        # Explicit frontend answer
        # -----------------------------------------------------

        answer = self._answer_text(
            answers,
            question_id,
        )

        if answer:
            return True

        # -----------------------------------------------------
        # Detect answer from original message.
        # -----------------------------------------------------

        message_normalised = self._normalise(
            message
        )

        question_patterns = {

            "q_department": [
                "department",
                "ministry",
                "office",
                "municipality",
                "municipal",
                "passport",
                "police",
                "school",
                "college",
                "revenue department",
                "corporation",
            ],

            "q_info_sought": [
                "information",
                "record",
                "records",
                "document",
                "documents",
                "file",
                "status",
                "why",
                "reason",
                "rejected",
                "delay",
                "information sought",
            ],

            "q_time_period": [
                "from ",
                "between ",
                "dated ",
                "date",
                "year",
                "month",
                "2024",
                "2025",
                "2026",
            ],

            "q_state": [
                "uttar pradesh",
                "up",
                "delhi",
                "maharashtra",
                "karnataka",
                "rajasthan",
                "bihar",
                "west bengal",
                "madhya pradesh",
                "gujarat",
                "tamil nadu",
                "telangana",
                "kerala",
                "punjab",
                "haryana",
                "odisha",
                "jharkhand",
                "chhattisgarh",
                "assam",
                "goa",
                "uttarakhand",
                "himachal pradesh",
                "uttaranchal",
            ],

            "q_agreement_exists": [
                "agreement",
                "lease",
                "rental agreement",
                "written agreement",
                "written lease",
                "verbal agreement",
                "oral agreement",
            ],

            "q_vacate_date": [
                "vacated",
                "vacate",
                "left the property",
                "moved out",
                "moved from",
                "tenancy ended",
                "ended tenancy",
                "after i moved out",
            ],

            "q_amount_disputed": [
                "deposit",
                "amount",
                "withheld",
                "deducted",
                "refund",
                "returned",
                "security deposit",
            ],

            "q_prior_communication": [
                "email",
                "message",
                "messaged",
                "notice",
                "contacted",
                "asked landlord",
                "written communication",
                "told my landlord",
                "informed landlord",
            ],

            "q_already_filed": [
                "already filed",
                "filed an rti",
                "submitted an rti",
                "applied for rti",
                "rti application",
                "first time",
            ],
        }

        patterns = question_patterns.get(
            question_id,
            [],
        )

        return any(
            pattern in message_normalised
            for pattern in patterns
        )

    # =========================================================
    # FOLLOW-UP QUESTIONS
    # =========================================================

    def get_follow_up_questions(
        self,
        workflow: Dict[str, Any],
        message: str,
        answers: Dict[str, Any],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        questions: List[Dict[str, Any]] = []

        language = self._safe_language(
            language
        )

        required_questions = workflow.get(
            "questions",
            [],
        )

        if not isinstance(
            required_questions,
            list,
        ):
            return []

        for question in required_questions:

            if not isinstance(
                question,
                dict,
            ):
                continue

            if self._question_is_answered(
                question,
                answers,
                message,
            ):
                continue

            # -------------------------------------------------
            # Questions use en/hi directly.
            # -------------------------------------------------

            text = self._localized(
                question,
                language,
                default="",
            )

            if not text:

                text = self._localized(
                    question.get(
                        "text",
                        {},
                    ),
                    language,
                    default="",
                )

            questions.append(
                {
                    "id":
                        question.get(
                            "id",
                            "",
                        ),

                    "text":
                        text,

                    "why_asked":
                        question.get(
                            "why_asked",
                        ),

                    "field_type":
                        question.get(
                            "field_type",
                            "text",
                        ),

                    "required":
                        question.get(
                            "required",
                            True,
                        ),

                    "affects":
                        question.get(
                            "affects",
                            [],
                        ),
                }
            )

            if (
                len(questions)
                >= self.MAX_FOLLOW_UP_QUESTIONS
            ):
                break

        return questions

    # =========================================================
    # MISSING INFORMATION LABELS
    # =========================================================

    @staticmethod
    def _missing_information_label(
        question_id: str,
    ) -> Optional[str]:

        missing_labels = {

            "q_department":
                "name of the concerned government department",

            "q_info_sought":
                "specific information being requested",

            "q_time_period":
                "relevant date, time period, or file/reference number",

            "q_state":
                "state where the matter occurred",

            "q_agreement_exists":
                "whether a written rental/lease agreement exists",

            "q_vacate_date":
                "date the tenancy ended",

            "q_amount_disputed":
                "amount or security deposit being disputed",

            "q_prior_communication":
                "whether prior written communication was made",

            "q_already_filed":
                "whether an RTI application has already been filed",
        }

        return missing_labels.get(
            question_id
        )

    # =========================================================
    # NORMALISE MISSING INFORMATION
    # =========================================================

    @classmethod
    def _normalise_missing_information(
        cls,
        value: Any,
    ) -> List[str]:

        if value is None:
            return []

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            return [value] if value else []

        if isinstance(
            value,
            dict,
        ):

            # Support common Gemma formats such as:
            # {"items": [...]}
            # {"missing_information": [...]}

            for key in (
                "items",
                "missing_information",
                "missing",
                "information",
            ):

                if key in value:

                    return cls._normalise_missing_information(
                        value.get(key)
                    )

            return []

        if isinstance(
            value,
            list,
        ):

            results = []

            for item in value:

                if isinstance(
                    item,
                    str,
                ):

                    text = item.strip()

                    if text:
                        results.append(text)

                elif isinstance(
                    item,
                    dict,
                ):

                    text = (
                        item.get("text")
                        or item.get("label")
                        or item.get("name")
                    )

                    if text:

                        text = str(
                            text
                        ).strip()

                        if text:
                            results.append(text)

            return results

        return []

    @staticmethod
    def _merge_unique(
        *lists: List[str],
    ) -> List[str]:

        result = []

        for items in lists:

            if not isinstance(
                items,
                list,
            ):
                continue

            for item in items:

                if not item:
                    continue

                item = str(
                    item
                ).strip()

                if not item:
                    continue

                if item not in result:
                    result.append(item)

        return result

    # =========================================================
    # LEGAL SUPPORT
    # =========================================================

    def _get_legal_support(
        self,
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        legal_support = workflow.get(
            "legal_support",
            [],
        )

        if not isinstance(
            legal_support,
            list,
        ):
            return []

        results = []

        for item in legal_support:

            if not isinstance(
                item,
                dict,
            ):
                continue

            law = item.get(
                "law",
                "",
            )

            explanation = self._localized(
                item.get(
                    "explanation",
                    {},
                ),
                language,
                default=None,
            )

            title = str(
                law
            ).strip()

            if not title:

                title = str(
                    item.get(
                        "title",
                        "",
                    )
                ).strip()

            if not title:
                continue

            results.append(
                {
                    "title":
                        title,

                    "description":
                        explanation,

                    "type":
                        item.get(
                            "type"
                        ),

                    "url":
                        item.get(
                            "url"
                        ),

                    "verify_before_use":
                        True,
                }
            )

        return results

    # =========================================================
    # SOURCES
    # =========================================================

    def _get_sources(
        self,
        workflow: Optional[Dict[str, Any]],
        workflow_id: Optional[str],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        results = []

        embedded_sources = workflow.get(
            "sources",
            [],
        )

        if not isinstance(
            embedded_sources,
            list,
        ):
            embedded_sources = []

        # -----------------------------------------------------
        # Sources embedded in workflows.json
        # -----------------------------------------------------

        for source in embedded_sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            results.append(
                {
                    "source_id":
                        source.get(
                            "source_id"
                        ),

                    "title":
                        self._localized(
                            source.get(
                                "title",
                                {},
                            ),
                            language,
                            default=source.get(
                                "title",
                                "",
                            ),
                        ),

                    "description":
                        self._localized(
                            source.get(
                                "description",
                                {},
                            ),
                            language,
                            default=None,
                        ),

                    "type":
                        source.get(
                            "type"
                        ),

                    "url":
                        source.get(
                            "url"
                        ),

                    "verify_before_use":
                        source.get(
                            "verify_before_use",
                            True,
                        ),
                }
            )

        # -----------------------------------------------------
        # Sources from sources.json
        # -----------------------------------------------------

        embedded_ids = {
            item.get("source_id")
            for item in embedded_sources
            if isinstance(item, dict)
            and item.get("source_id")
        }

        for source in self.sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            source_id = source.get(
                "source_id"
            )

            source_workflow_ids = source.get(
                "workflow_ids",
                [],
            )

            if not isinstance(
                source_workflow_ids,
                list,
            ):
                source_workflow_ids = []

            matches = (
                source_id in embedded_ids
                or
                workflow_id in source_workflow_ids
            )

            if not matches:
                continue

            already_added = any(
                item.get(
                    "source_id"
                ) == source_id
                for item in results
            )

            if already_added:
                continue

            results.append(
                {
                    "source_id":
                        source_id,

                    "title":
                        self._localized(
                            source.get(
                                "title",
                                {},
                            ),
                            language,
                            default="",
                        ),

                    "description":
                        self._localized(
                            source.get(
                                "description",
                                {},
                            ),
                            language,
                            default=None,
                        ),

                    "type":
                        source.get(
                            "type"
                        ),

                    "url":
                        source.get(
                            "url"
                        ),

                    "verify_before_use":
                        source.get(
                            "verify_before_use",
                            True,
                        ),
                }
            )

        return results

    # =========================================================
    # DOCUMENTS
    # =========================================================

    def _get_documents(
        self,
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        documents = workflow.get(
            "documents",
            {},
        )

        if not documents:
            return []

        # -----------------------------------------------------
        # Current JSON object format
        # -----------------------------------------------------

        if isinstance(
            documents,
            dict,
        ):

            document_text = self._localized(
                documents,
                language,
                default="",
            )

            if document_text:

                return [
                    {
                        "id":
                            documents.get(
                                "type",
                                "workflow_document",
                            ),

                        "name":
                            document_text,

                        "required":
                            documents.get(
                                "required",
                                False,
                            ),

                        "type":
                            documents.get(
                                "type"
                            ),

                        "applicable_when":
                            documents.get(
                                "applicable_when"
                            ),
                    }
                ]

            return []

        # -----------------------------------------------------
        # Future list format
        # -----------------------------------------------------

        if isinstance(
            documents,
            list,
        ):

            results = []

            for document in documents:

                if not isinstance(
                    document,
                    dict,
                ):
                    continue

                results.append(
                    {
                        "id":
                            document.get(
                                "id",
                                "",
                            ),

                        "name":
                            self._localized(
                                document.get(
                                    "name",
                                    {},
                                ),
                                language,
                                default="",
                            ),

                        "required":
                            document.get(
                                "required",
                                False,
                            ),

                        "type":
                            document.get(
                                "type"
                            ),

                        "applicable_when":
                            document.get(
                                "applicable_when"
                            ),
                    }
                )

            return results

        return []

    # =========================================================
    # EVIDENCE
    # =========================================================

    def _get_evidence(
        self,
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        evidence_data = workflow.get(
            "evidence",
            [],
        )

        if not isinstance(
            evidence_data,
            list,
        ):
            return []

        results = []

        for index, item in enumerate(
            evidence_data
        ):

            # -------------------------------------------------
            # Simple string evidence
            # -------------------------------------------------

            if isinstance(
                item,
                str,
            ):

                text = item.strip()

                if not text:
                    continue

                results.append(
                    {
                        "id":
                            f"evidence_{index + 1}",

                        "name":
                            text,

                        "description":
                            None,

                        "required":
                            False,
                    }
                )

                continue

            # -------------------------------------------------
            # Dictionary evidence
            # -------------------------------------------------

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = (
                self._localized(
                    item.get(
                        "name",
                        {},
                    ),
                    language,
                    default="",
                )
                or
                self._localized(
                    item.get(
                        "title",
                        {},
                    ),
                    language,
                    default="",
                )
                or
                self._localized(
                    item.get(
                        "description",
                        {},
                    ),
                    language,
                    default="",
                )
            )

            if not name:
                continue

            description = self._localized(
                item.get(
                    "description",
                    {},
                ),
                language,
                default=None,
            )

            results.append(
                {
                    "id":
                        item.get(
                            "id",
                            f"evidence_{index + 1}",
                        ),

                    "name":
                        name,

                    "description":
                        description,

                    "required":
                        item.get(
                            "required",
                            False,
                        ),

                    "type":
                        item.get(
                            "type"
                        ),

                    "applicable_when":
                        item.get(
                            "applicable_when"
                        ),
                }
            )

        return results

    # =========================================================
    # AUTHORITIES
    # =========================================================

    def _get_authorities(
        self,
        workflow_id: Optional[str],
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, Any]]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        results = []

        possible_ids = {
            workflow_id,
            workflow.get(
                "intent"
            ),
            self._slug(
                workflow.get(
                    "category",
                    "",
                )
            ),
        }

        possible_ids = {
            item
            for item in possible_ids
            if item
        }

        for authority in self.authorities:

            if not isinstance(
                authority,
                dict,
            ):
                continue

            workflow_ids = authority.get(
                "workflow_ids",
                [],
            )

            if not isinstance(
                workflow_ids,
                list,
            ):
                workflow_ids = []

            if not (
                possible_ids
                &
                set(workflow_ids)
            ):
                continue

            results.append(
                {
                    "id":
                        authority.get(
                            "id",
                            "",
                        ),

                    "name":
                        self._localized(
                            authority.get(
                                "name",
                                {},
                            ),
                            language,
                            default="",
                        ),

                    "role":
                        self._localized(
                            authority.get(
                                "role",
                                {},
                            ),
                            language,
                            default=None,
                        ),

                    "jurisdiction":
                        authority.get(
                            "jurisdiction"
                        ),
                }
            )

        return results

    # =========================================================
    # ESCALATION
    # =========================================================

    def _build_escalation(
        self,
        workflow: Optional[Dict[str, Any]],
        authorities: List[Dict[str, Any]],
        language: str = "en",
    ) -> Dict[str, Any]:

        if not workflow:

            return {
                "appropriate": False,
                "reason": None,
                "authorities": [],
            }

        escalation_data = workflow.get(
            "escalation",
            [],
        )

        if not escalation_data:

            return {
                "appropriate": False,
                "reason": None,
                "authorities": [],
            }

        # -----------------------------------------------------
        # List of escalation levels
        # -----------------------------------------------------

        if isinstance(
            escalation_data,
            list,
        ):

            steps = []

            for item in escalation_data:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                text = self._localized(
                    item,
                    language,
                    default="",
                )

                if text:

                    steps.append(
                        {
                            "level":
                                item.get(
                                    "level"
                                ),

                            "text":
                                text,
                        }
                    )

            if not steps:

                return {
                    "appropriate": False,
                    "reason": None,
                    "authorities": [],
                }

            return {
                "appropriate": True,

                "reason":
                    "The workflow provides an escalation path "
                    "if the matter remains unresolved.",

                "authorities":
                    authorities,

                "steps":
                    steps,
            }

        return {
            "appropriate": True,

            "reason":
                "Follow the applicable escalation path "
                "for this workflow.",

            "authorities":
                authorities,
        }

    # =========================================================
    # ACTION PLAN
    # =========================================================

    def _get_action_plan(
        self,
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> List[str]:

        if not workflow:
            return []

        language = self._safe_language(
            language
        )

        actions = workflow.get(
            "actions",
            [],
        )

        if not isinstance(
            actions,
            list,
        ):
            return []

        results = []

        for action in actions:

            # Support both:
            # {"en": "...", "hi": "..."}
            # and:
            # {"text": {"en": "...", "hi": "..."}}

            if isinstance(
                action,
                str,
            ):

                text = action.strip()

            elif isinstance(
                action,
                dict,
            ):

                text = self._localized(
                    action,
                    language,
                    default="",
                )

                if not text:

                    text = self._localized(
                        action.get(
                            "text",
                            {},
                        ),
                        language,
                        default="",
                    )

            else:
                continue

            if text:
                results.append(
                    text
                )

        return results

    # =========================================================
    # FINAL RECOMMENDATION
    # =========================================================

    def build_final_recommendation(
        self,
        workflow: Optional[Dict[str, Any]],
        language: str = "en",
    ) -> Dict[str, Any]:

        language = self._safe_language(
            language
        )

        # -----------------------------------------------------
        # UNSUPPORTED
        # -----------------------------------------------------

        if not workflow:

            return {
                "workflow": None,

                "workflow_name": None,

                "legal_support": [],

                "documents": [],

                "authorities": [],

                "action_plan": [],

                "evidence": [],

                "escalation": {
                    "appropriate": False,
                    "reason": None,
                    "authorities": [],
                },

                "sources": [],

                "disclaimer":
                    "NyayaPath could not identify a supported "
                    "workflow for this request.",
            }

        # -----------------------------------------------------
        # WORKFLOW ID
        # -----------------------------------------------------

        workflow_id = workflow.get(
            "id"
        )

        # -----------------------------------------------------
        # SOURCES
        # -----------------------------------------------------

        sources = self._get_sources(
            workflow=workflow,
            workflow_id=workflow_id,
            language=language,
        )

        # -----------------------------------------------------
        # LEGAL SUPPORT
        # -----------------------------------------------------

        legal_support = self._get_legal_support(
            workflow,
            language,
        )

        # -----------------------------------------------------
        # DOCUMENTS
        # -----------------------------------------------------

        documents = self._get_documents(
            workflow,
            language,
        )

        # -----------------------------------------------------
        # AUTHORITIES
        # -----------------------------------------------------

        authorities = self._get_authorities(
            workflow_id=workflow_id,
            workflow=workflow,
            language=language,
        )

        # -----------------------------------------------------
        # ACTION PLAN
        # -----------------------------------------------------

        action_plan = self._get_action_plan(
            workflow,
            language,
        )

        # -----------------------------------------------------
        # EVIDENCE
        # -----------------------------------------------------

        evidence = self._get_evidence(
            workflow,
            language,
        )

        # -----------------------------------------------------
        # WORKFLOW NAME
        # -----------------------------------------------------

        workflow_name = self._localized(
            workflow.get(
                "name",
                {},
            ),
            language,
            default=workflow.get(
                "category"
            ),
        )

        # -----------------------------------------------------
        # ESCALATION
        # -----------------------------------------------------

        escalation = self._build_escalation(
            workflow,
            authorities,
            language,
        )

        # -----------------------------------------------------
        # DISCLAIMER
        # -----------------------------------------------------

        disclaimer = self._localized(
            workflow.get(
                "disclaimer",
                {},
            ),
            language,
            default=None,
        )

        # -----------------------------------------------------
        # FINAL
        # -----------------------------------------------------

        return {
            "workflow":
                workflow_id,

            "workflow_name":
                workflow_name,

            "legal_support":
                legal_support,

            "documents":
                documents,

            "authorities":
                authorities,

            # IMPORTANT:
            # action_plan is already List[str].
            "action_plan":
                action_plan,

            "evidence":
                evidence,

            "escalation":
                escalation,

            "sources":
                sources,

            "disclaimer":
                disclaimer,
        }

    # =========================================================
    # MAIN ANALYSIS FUNCTION
    # =========================================================

    def analyze_workflow(
        self,
        category: str,
        intent: str,
        message: str,
        language: str = "en",
        answers: Optional[Dict[str, Any]] = None,
        skip_follow_up: bool = False,
        initial_advice: str = "",

        # -----------------------------------------------------
        # IMPORTANT:
        # This parameter fixes:
        #
        # unexpected keyword argument
        # 'missing_information'
        #
        # Gemma can send missing_information here.
        # -----------------------------------------------------

        missing_information: Optional[Any] = None,
    ) -> Dict[str, Any]:

        # -----------------------------------------------------
        # Normalise answers
        # -----------------------------------------------------

        answers = (
            answers
            if isinstance(
                answers,
                dict,
            )
            else {}
        )

        # -----------------------------------------------------
        # Normalise language
        # -----------------------------------------------------

        language = self._safe_language(
            language
        )

        # -----------------------------------------------------
        # Normalise Gemma values
        # -----------------------------------------------------

        category = self._normalise_category(
            category
        )

        intent = self._normalise_intent(
            intent
        )

        message = str(
            message or ""
        ).strip()

        # =====================================================
        # FIND WORKFLOW
        # =====================================================

        workflow = self._find_workflow(
            category=category,
            intent=intent,
            message=message,
        )

        # =====================================================
        # UNSUPPORTED REQUEST
        # =====================================================

        if not workflow:

            gemma_missing_information = (
                self._normalise_missing_information(
                    missing_information
                )
            )

            return {
                "category":
                    category,

                "intent":
                    intent,

                "language":
                    language,

                "initial_advice":
                    initial_advice,

                "missing_information":
                    gemma_missing_information,

                "needs_more_information":
                    False,

                "can_skip_follow_up":
                    True,

                "skipped_follow_up":
                    skip_follow_up,

                "follow_up_questions":
                    [],

                "workflow":
                    None,

                "supported":
                    False,

                "legal_support":
                    [],

                "documents":
                    [],

                "evidence":
                    [],

                "action_plan":
                    [],

                "escalation": {
                    "appropriate": False,
                    "reason": None,
                    "authorities": [],
                },

                "sources":
                    [],

                "disclaimer":
                    "NyayaPath could not identify a "
                    "supported workflow for this request.",

                "final_recommendation":
                    {
                        "workflow": None,
                        "workflow_name": None,
                        "legal_support": [],
                        "documents": [],
                        "authorities": [],
                        "action_plan": [],
                        "evidence": [],
                        "escalation": {
                            "appropriate": False,
                            "reason": None,
                            "authorities": [],
                        },
                        "sources": [],
                        "disclaimer":
                            "NyayaPath could not identify a "
                            "supported workflow for this request.",
                    },
            }

        # =====================================================
        # FOLLOW-UP QUESTIONS
        # =====================================================

        questions = []

        if not skip_follow_up:

            questions = (
                self.get_follow_up_questions(
                    workflow=workflow,
                    message=message,
                    answers=answers,
                    language=language,
                )
            )

        # =====================================================
        # CALCULATED MISSING INFORMATION
        # =====================================================

        calculated_missing_information = []

        for question in questions:

            question_id = question.get(
                "id",
                "",
            )

            label = (
                self._missing_information_label(
                    question_id
                )
            )

            if label:

                calculated_missing_information.append(
                    label
                )

        # =====================================================
        # GEMMA MISSING INFORMATION
        # =====================================================

        gemma_missing_information = (
            self._normalise_missing_information(
                missing_information
            )
        )

        # =====================================================
        # COMBINE BOTH SOURCES
        # =====================================================

        combined_missing_information = (
            self._merge_unique(
                gemma_missing_information,
                calculated_missing_information,
            )
        )

        # =====================================================
        # SKIP FOLLOW-UP
        # =====================================================

        if skip_follow_up:

            questions = []

            # If user explicitly skipped follow-up,
            # don't claim that additional questions are
            # currently required.
            #
            # We still preserve Gemma's missing_information
            # because it is useful for the frontend.

        needs_more_information = (
            bool(questions)
            and not skip_follow_up
        )

        # =====================================================
        # FINAL RECOMMENDATION
        # =====================================================

        recommendation = (
            self.build_final_recommendation(
                workflow=workflow,
                language=language,
            )
        )

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {

            "category":
                category,

            "intent":
                intent,

            "language":
                language,

            "initial_advice":
                initial_advice,

            "missing_information":
                combined_missing_information,

            "needs_more_information":
                needs_more_information,

            "can_skip_follow_up":
                True,

            "skipped_follow_up":
                skip_follow_up,

            "follow_up_questions":
                questions,

            "workflow":
                recommendation.get(
                    "workflow"
                ),

            "supported":
                True,

            "legal_support":
                recommendation.get(
                    "legal_support",
                    [],
                ),

            "documents":
                recommendation.get(
                    "documents",
                    [],
                ),

            "evidence":
                recommendation.get(
                    "evidence",
                    [],
                ),

            # -------------------------------------------------
            # IMPORTANT:
            # Do NOT convert action_plan items here.
            #
            # _get_action_plan() already returns:
            # ["step 1", "step 2", "step 3"]
            # -------------------------------------------------

            "action_plan":
                recommendation.get(
                    "action_plan",
                    [],
                ),

            "escalation":
                recommendation.get(
                    "escalation",
                    {
                        "appropriate": False,
                        "reason": None,
                        "authorities": [],
                    },
                ),

            "sources":
                recommendation.get(
                    "sources",
                    [],
                ),

            "disclaimer":
                recommendation.get(
                    "disclaimer"
                ),

            # -------------------------------------------------
            # Complete recommendation
            # -------------------------------------------------

            "final_recommendation":
                recommendation,
        }


# =============================================================
# SINGLE SERVICE INSTANCE
# =============================================================

workflow_service = WorkflowService()