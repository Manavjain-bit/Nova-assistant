from app.services import memory


def test_extract_facts_name_and_preference():
    facts = memory.extract_facts(1, "Hi, my name is Arjun and I like jazz music.")
    fact_dict = dict(facts)
    assert fact_dict.get("name") == "Arjun"
    assert "preference" in fact_dict


def test_extract_facts_returns_empty_for_unrelated_text():
    facts = memory.extract_facts(1, "What's the weather like today?")
    assert facts == []
