import pytest

from src.preprocessing.clean import check, math_loss_signals


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


# ---- 수식 누락 초록 탐지 (실제 코퍼스 초록에서 뽑은 문장) ----------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "pulse times of must be applied to achieve saturation in GPC and Cl content.",  # 값과 단위가 통째로 빠짐
        "films were maintained at temperatures ranging from room temperature to . X-ray diffraction patterns of the samples",
        "For a film, a dielectric constant of and a capacitive equivalent thickness were obtained.",
        "Nanostructure and electrical properties of iridium oxide () thin films were characterized.",
        "new materials are introduced in the gate stack (high- dielectrics and metal gates) and the transistor channel",
        "grown on oxide surfaces (thermally grown , HF-cleaned Ge, and ) and inhibited on oxide-free substrates",
        "A leakage current of A/cm 2 is achieved at a breakdown field of MV/cm. The relative dielectric constant is 34.",
        "capacitors was conf irmed . tant high permittivity candidate material for post",
    ],
)
def test_math_loss_is_detected(text):
    assert math_loss_signals(text)


@pytest.mark.parametrize(
    "text",
    [
        "a lower growth rate for ozone than for water-based growth and to incorporation of defects",  # 정상적인 비교 문법
        "leakage currents are measured for Er-doped HfO2 than for HfO2.",
        "films were studied at thicknesses ranging up to and including 5 nm.",
        "the power consumptions for high- and low-resistance states are found to be 0.25 and 0.1 mW",
        "oxides such as HfO 2 , Er 2 O 3 , and TiO 2 were grown by atomic layer deposition",  # 아래첨자 사이 공백은 누락이 아님
        "a dielectric constant of 34 and a capacitive equivalent thickness of 21 Å were obtained",
        "the films were annealed at 500 °C for 1 h in nitrogen",
        "Hafnium oxide is a leading candidate to replace silicon oxide as the gate dielectric.",
    ],
)
def test_normal_sentences_are_not_flagged_as_math_loss(text):
    assert math_loss_signals(text) == []


def test_check_drops_math_loss_papers_unless_told_to_keep_them():
    damaged = paper("Scaling to sub-1 nm EOT", "Pulse times of must be applied to achieve saturation in hafnium oxide ALD.", ["hfo2_ald"])
    assert check(damaged).startswith("math_loss:")
    assert check(damaged, drop_math_loss=False) is None

