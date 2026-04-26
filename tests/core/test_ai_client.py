from unittest.mock import MagicMock, patch
import pytest
from src.core.ai_client import get_client, ClaudeClient, OpenAIClient, OllamaClient


def test_get_client_returns_none_when_provider_none():
    assert get_client("none", "", "") is None


def test_get_client_returns_none_when_provider_empty():
    assert get_client("", "", "") is None


def test_get_client_returns_claude_client():
    client = get_client("claude", "sk-ant-test", "")
    assert isinstance(client, ClaudeClient)


def test_get_client_returns_openai_client():
    client = get_client("openai", "sk-test", "")
    assert isinstance(client, OpenAIClient)


def test_get_client_returns_ollama_client():
    client = get_client("ollama", "", "http://localhost:11434")
    assert isinstance(client, OllamaClient)


@patch("src.core.ai_client.anthropic")
def test_claude_client_summarize(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Summary text")]
    )
    client = ClaudeClient(api_key="sk-ant-test")
    result = client.summarize("transcript text", "Summarize this")
    assert result == "Summary text"
    mock_client.messages.create.assert_called_once()


@patch("src.core.ai_client.openai")
def test_openai_client_summarize(mock_openai):
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Summary text"))]
    )
    client = OpenAIClient(api_key="sk-test")
    result = client.summarize("transcript text", "Summarize this")
    assert result == "Summary text"


@patch("src.core.ai_client.httpx")
def test_ollama_client_summarize(mock_httpx):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Summary text"}
    mock_httpx.post.return_value = mock_response
    client = OllamaClient(base_url="http://localhost:11434", model="llama3")
    result = client.summarize("transcript text", "Summarize this")
    assert result == "Summary text"


def test_claude_client_raises_import_error_when_anthropic_missing():
    import src.core.ai_client as mod
    original = mod.anthropic
    mod.anthropic = None
    try:
        with pytest.raises(ImportError, match="pip install anthropic"):
            ClaudeClient(api_key="test")
    finally:
        mod.anthropic = original


def test_openai_client_raises_import_error_when_openai_missing():
    import src.core.ai_client as mod
    original = mod.openai
    mod.openai = None
    try:
        with pytest.raises(ImportError, match="pip install openai"):
            OpenAIClient(api_key="test")
    finally:
        mod.openai = original


def test_ollama_client_raises_import_error_when_httpx_missing():
    import src.core.ai_client as mod
    original = mod.httpx
    mod.httpx = None
    try:
        with pytest.raises(ImportError, match="pip install httpx"):
            OllamaClient().summarize("text", "prompt")
    finally:
        mod.httpx = original
