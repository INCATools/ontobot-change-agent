"""Constants."""

from os import getenv

# GitHUb Template Attributes.
SYNONYMS = "Synonyms"
SYNONYM_TYPE = "Synonym type"
DEFINITION = "Definition"
OWL_EXTENSION = ".owl"

OPENAI_KEY = str(getenv("OPENAI_API_KEY"))
ANTHROPIC_KEY = str(getenv("ANTHROPIC_API_KEY"))
CBORG_KEY = str(getenv("CBORG_API_KEY"))

OPEN_AI_MODEL = "gpt-4o-2024-08-06"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
OLLAMA_MODEL = "llama3.1"  # ! not all models support tools (tool calling)
CBORG_MODEL = "anthropic/claude-sonnet"

OPENAI_PROVIDER = "openai"
ANTHROPIC_PROVIDER = "anthropic"
OLLAMA_PROVIDER = "ollama"
CBORG_PROVIDER = "cborg"
