
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class SecurityAgent:
    """
    Security Agent: Validates user input and prevents prompt injection.
    Framework: Custom Python (no external LLM framework needed here).

    Guardrails implemented:
    - Input length limit (max 500 chars)
    - Prompt injection pattern detection
    - Blocked topic list (no PII, no harmful content)
    - HTML/script injection prevention
    - Input sanitization
    """

    # Patterns that indicate prompt injection attempts
    INJECTION_PATTERNS = [
        r"ignore (previous|all) instructions",
        r"forget your instructions",
        r"you are now",
        r"act as (a|an)",
        r"pretend (you are|to be)",
        r"disregard all",
        r"override",
        r"system prompt",
        r"<script",
        r"javascript:",
        r"DROP TABLE",
        r"SELECT \* FROM",
        r"jailbreak",
        r"bypass",
        r"do anything now",
        r"DAN",
    ]

    # Blocked/sensitive topics (PII and harm prevention)
    BLOCKED_TOPICS = [
        "how to make weapons",
        "how to hack",
        "how to make bombs",
        "how to make drugs",
        "credit card number",
        "social security",
        "password",
        "ssn",
        "personal information of",
    ]

    MAX_INPUT_LENGTH = 500

    def validate(self, user_input: str) -> Tuple[bool, str]:
        """
        Validates user input.
        Returns: (is_valid: bool, message: str)
        """
        logger.info(f"Security Agent: Checking input length={len(user_input)}")

        # Check 1: Empty input
        if not user_input or not user_input.strip():
            return False, "❌ Input cannot be empty."

        # Check 2: Input length limit
        if len(user_input) > self.MAX_INPUT_LENGTH:
            return False, f"❌ Input too long. Max {self.MAX_INPUT_LENGTH} characters."

        # Check 3: Prompt injection patterns
        input_lower = user_input.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"Security Agent: Injection attempt detected: {pattern}")
                return False, "❌ Potentially harmful input detected. Please enter a valid research topic."

        # Check 4: Blocked topics
        for blocked in self.BLOCKED_TOPICS:
            if blocked in input_lower:
                logger.warning(f"Security Agent: Blocked topic: {blocked}")
                return False, "❌ This topic is not allowed. Please choose an appropriate research subject."

        # Check 5: Only printable characters allowed
        if not all(c.isprintable() for c in user_input):
            return False, "❌ Input contains invalid characters."

        logger.info("Security Agent: Input validated ✅")
        return True, "✅ Input is safe and valid."

    def sanitize(self, user_input: str) -> str:
        """Removes potentially harmful content from input."""
        # Strip HTML tags
        sanitized = re.sub(r'<[^>]+>', '', user_input)
        # Remove extra whitespace
        sanitized = ' '.join(sanitized.split())
        return sanitized.strip()
