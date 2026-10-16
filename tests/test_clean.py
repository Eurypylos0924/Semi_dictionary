from src.preprocessing.clean import check


def paper(title: str, summary: str, topics: list[str]) -> dict:
    return {"title": title, "summary": summary, "topics": topics}


def test_keeps_generic_xrd_primer_even_if_abstract_mentions_polymer():
    p = paper("X-ray diffraction: a powerful method", "XRD for thin film and polymer samples, grain size.", ["xrd_thin_film"])
    assert check(p) is None


def test_removes_organic_material_by_abstract_keyword():
    p = paper("Nickel Phthalocyanine Thin Films", "Structural analysis of thin film by XRD.", ["xrd_thin_film"])
    assert check(p).startswith("exclude:")


def test_removes_polymer_when_in_title():
    p = paper("High-k polymer-ceramic composite", "leakage and breakdown of capacitor.", ["high_k_leakage"])
    assert check(p).startswith("exclude_title:")


def test_removes_generic_manufacturing_review_from_yield_topic():
    p = paper("Big data in manufacturing", "A systematic mapping of analytics in industry.", ["yield_process"])
    assert check(p).startswith("require:")


def test_keeps_semiconductor_yield_paper():
    p = paper("Root cause analysis for wafer yield", "Semiconductor fab excursion detection.", ["yield_process"])
    assert check(p) is None


def test_every_collector_topic_has_a_require_rule():
    # REQUIRE에 없는 주제는 논문이 전부 걸러지므로, 수집 주제를 추가하면 규칙도 함께 추가해야 한다
    from src.collector.openalex_collect import TOPICS
    from src.preprocessing.clean import REQUIRE

    assert set(TOPICS) <= set(REQUIRE)
