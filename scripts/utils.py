"""
scripts/utils.py

Shared utilities for skill evals:
  - SensitiveDataMasker   : masks PII fields before logging/reporting
  - SyntheticDataFactory  : generates fake-but-realistic PII for test fixtures
  - FixtureLoader         : loads synthetic OR real fixtures safely
  - EnvSecrets            : reads secrets from environment, never from files
"""

import json
import os
import re
import hashlib
from pathlib import Path
from datetime import date
from typing import Any


# ---------------------------------------------------------------------------
# 1. Sensitive field registry
#    Add any field name your skills handle that could carry sensitive data.
# ---------------------------------------------------------------------------

SENSITIVE_FIELDS = {
    # Identity
    "ssn", "social_security_number", "sin", "national_id",
    "dob", "date_of_birth", "birthdate",
    "passport_number", "drivers_license",

    # Employment
    "employer_id", "employee_id", "payroll_id", "tax_id", "ein",

    # Credentials
    "password", "passwd", "secret", "api_key", "api_secret",
    "token", "access_token", "refresh_token", "private_key",

    # Financial
    "credit_card", "card_number", "cvv", "bank_account", "routing_number",
    "iban", "swift",

    # Contact
    "email", "phone", "mobile", "address", "zip", "postal_code",
}

# Patterns for detecting sensitive values even when field names aren't flagged
SENSITIVE_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),                          # SSN
    (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "CARD"),      # Credit card
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "EMAIL"),  # Email
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API_KEY"),                    # API key
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "DATE"),                         # ISO date
]


# ---------------------------------------------------------------------------
# 2. SensitiveDataMasker
# ---------------------------------------------------------------------------

class SensitiveDataMasker:
    """
    Masks sensitive values in dicts/strings before they reach logs or reports.

    Usage:
        masker = SensitiveDataMasker()
        safe = masker.mask(record)          # returns masked copy
        print(masker.mask_string(raw_str))  # masks a plain string
    """

    def __init__(self, mask_char: str = "X", show_length: bool = True):
        self.mask_char = mask_char
        self.show_length = show_length

    def _mask_value(self, value: str) -> str:
        if not isinstance(value, str) or not value:
            return value
        length = len(value)
        if self.show_length:
            return f"[MASKED:{length}]"
        return self.mask_char * min(length, 8)

    def mask(self, data: Any, _depth: int = 0) -> Any:
        """Recursively mask sensitive fields in a dict or list."""
        if _depth > 20:
            return data  # guard against infinite recursion

        if isinstance(data, dict):
            return {
                k: self._mask_value(v) if k.lower() in SENSITIVE_FIELDS
                else self.mask(v, _depth + 1)
                for k, v in data.items()
            }
        if isinstance(data, list):
            return [self.mask(item, _depth + 1) for item in data]
        return data

    def mask_string(self, text: str) -> str:
        """Mask sensitive patterns found in a plain string."""
        for pattern, label in SENSITIVE_PATTERNS:
            text = pattern.sub(f"[{label}:MASKED]", text)
        return text

    def safe_repr(self, data: Any) -> str:
        """Return a JSON string safe for logging."""
        return json.dumps(self.mask(data), indent=2, default=str)


# ---------------------------------------------------------------------------
# 3. SyntheticDataFactory
# ---------------------------------------------------------------------------

class SyntheticDataFactory:
    """
    Generates deterministic fake PII for test fixtures.
    Values are obviously fake but structurally realistic.

    Usage:
        factory = SyntheticDataFactory()
        record = factory.employee(index=1)
    """

    def ssn(self, index: int = 0) -> str:
        """Returns obviously fake SSN: 000-00-XXXX"""
        return f"000-00-{index:04d}"

    def dob(self, index: int = 0) -> str:
        """Returns obviously fake DOB in the year 1900"""
        day = (index % 28) + 1
        month = (index % 12) + 1
        return f"1900-{month:02d}-{day:02d}"

    def employer_id(self, index: int = 0) -> str:
        return f"TEST-EMP-{index:04d}"

    def email(self, name: str = "test.user", index: int = 0) -> str:
        return f"{name.lower().replace(' ', '.')}.{index}@example-test.com"

    def api_key(self, prefix: str = "sk") -> str:
        return f"{prefix}-test-{'X' * 20}"

    def password(self) -> str:
        return "TEST_PASSWORD_PLACEHOLDER"

    def employee(self, index: int = 1, name: str = "Test User") -> dict:
        """Returns a complete fake employee record."""
        return {
            "name": name,
            "dob": self.dob(index),
            "ssn": self.ssn(index),
            "employer_id": self.employer_id(index),
            "email": self.email(name, index),
            "api_key": self.api_key(),
            "password": self.password(),
        }

    def tokenize(self, real_value: str, label: str = "TOKEN") -> str:
        """
        Replaces a real sensitive value with a deterministic token.
        Use when you need realistic format but can't use fully fake data.

        e.g. tokenize("EMP-BGFMS-2024", "employer_id") → "EMP-[employer_id:a3f2]"
        """
        short_hash = hashlib.md5(real_value.encode()).hexdigest()[:4]
        return f"[{label}:{short_hash}]"


# ---------------------------------------------------------------------------
# 4. FixtureLoader
# ---------------------------------------------------------------------------

class FixtureLoader:
    """
    Loads test fixtures from either:
      - fixtures/synthetic/  : fake data, always available, safe to commit
      - fixtures/real/       : real data, .gitignored, loaded only when available

    Usage:
        loader = FixtureLoader()
        cases = loader.load("pii_test_cases.json")
    """

    def __init__(self, prefer_real: bool = False, fixtures_root: Path = None):
        self.prefer_real  = prefer_real
        self.masker       = SensitiveDataMasker()
        # Default: <repo_root>/fixtures/
        self.FIXTURES_ROOT = fixtures_root or Path(__file__).parent.parent / "fixtures"

    def load(self, filename: str) -> list[dict]:
        """
        Load fixtures by filename. Prefers real data if available and
        prefer_real=True, otherwise falls back to synthetic.
        """
        real_path = self.FIXTURES_ROOT / "real" / filename
        synthetic_path = self.FIXTURES_ROOT / "synthetic" / filename

        if self.prefer_real and real_path.exists():
            print(f"[FixtureLoader] Loading REAL fixtures: {real_path}")
            print("[FixtureLoader] ⚠️  Real data active — ensure logs are not stored")
            return self._read(real_path)

        if synthetic_path.exists():
            print(f"[FixtureLoader] Loading synthetic fixtures: {synthetic_path}")
            return self._read(synthetic_path)

        raise FileNotFoundError(
            f"No fixture found for '{filename}' in synthetic/ or real/.\n"
            f"Expected at: {synthetic_path}"
        )

    def _read(self, path: Path) -> list[dict]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("evals", data)
        return data

    def load_from_env(self, env_var: str) -> list[dict]:
        """
        Load real fixtures from a path specified in an env var.
        Keeps real data paths out of the codebase entirely.

        Usage:
            cases = loader.load_from_env("TEST_REAL_FIXTURES_PATH")
        """
        path_str = os.environ.get(env_var)
        if not path_str:
            raise EnvironmentError(
                f"Environment variable '{env_var}' is not set.\n"
                f"Set it to the path of your real fixtures file, or use synthetic fixtures instead."
            )
        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"Real fixtures path not found: {path}")
        print(f"[FixtureLoader] Loading real fixtures from env {env_var}: {path}")
        return self._read(path)


# ---------------------------------------------------------------------------
# 5. EnvSecrets
# ---------------------------------------------------------------------------

class EnvSecrets:
    """
    Reads secrets from environment variables only — never from files.
    Raises a clear error if a required secret is missing.

    Usage:
        secrets = EnvSecrets()
        key = secrets.require("TEST_API_KEY")
        key = secrets.get("OPTIONAL_KEY", default="fallback")
    """

    def require(self, name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise EnvironmentError(
                f"Required secret '{name}' is not set in environment.\n"
                f"See .env.example for setup instructions."
            )
        return value

    def get(self, name: str, default: str = "") -> str:
        return os.environ.get(name, default)

    def anthropic_key(self) -> str:
        return self.require("ANTHROPIC_API_KEY")
