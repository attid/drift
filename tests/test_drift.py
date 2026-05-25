from drift_tg_bot.drift import _extract_content


def test_extract_content_from_openai_compatible_response() -> None:
    payload = {"choices": [{"message": {"content": " answer "}}]}

    assert _extract_content(payload) == "answer"


def test_extract_content_returns_empty_string_for_missing_choices() -> None:
    assert _extract_content({}) == ""
