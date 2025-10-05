import pytest

from src import utils


def test_clean_text_strips_and_collapses_whitespace():
    assert utils.clean_text("  hello   world\n") == "hello world"


def test_clean_text_raises_on_none():
    with pytest.raises(TypeError):
        utils.clean_text(None)  # type: ignore[arg-type]


def test_clean_corpus_drops_empty_entries():
    cleaned = utils.clean_corpus(["  policy A  ", "\n", "policy B\t"])
    assert cleaned == ["policy A", "policy B"]


def test_clean_corpus_requires_non_empty():
    with pytest.raises(ValueError):
        utils.clean_corpus(["\n", "   "])
