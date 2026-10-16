from src.collector.openalex_collect import restore_abstract


def test_restore_abstract_orders_words_by_position():
    inverted = {"films": [3], "Hafnium": [0], "oxide": [1], "thin": [2]}
    assert restore_abstract(inverted) == "Hafnium oxide thin films"


def test_restore_abstract_handles_missing_abstract():
    assert restore_abstract(None) == ""
    assert restore_abstract({}) == ""
