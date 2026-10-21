# 답변 근거 충실도 (2026-10-20)

채점 모델: nvidia/nvidia/nemotron-3-super-120b-a12b. 답변 모델은 설정별 기본값(baseline은 Gemini flash-lite). 질문은 답이 있는 질문만.

### 답변 근거 충실도 (채점 결과 그대로)

| 설정 | 세트 | 질문 | 답변/거절 | 주장 수 | 충실도(주장 기준) | 번호만 틀림 | 근거 없음·반대 | 번호까지 맞음 | 완결성(답변한 질문) | 완결성(전체) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | field | 14 | 9/5 | 34 | 88.2% | 0.0% | 11.8% | 100.0% | 48.4% | 31.1% |
| baseline | original | 27 | 27/0 | 110 | 96.4% | 0.0% | 3.6% | 100.0% | 75.0% | 75.0% |
| max_judge | field | 14 | 12/2 | 46 | 87.0% | 0.0% | 13.0% | 100.0% | 47.2% | 40.4% |
| max_judge | original | 27 | 27/0 | 115 | 99.1% | 0.0% | 0.9% | 100.0% | 77.6% | 77.6% |

### 한계 표시 문장('논문에서 확인되지 않음' 등)을 주장에서 제외한 수치

| 설정 | 세트 | 질문 | 답변/거절 | 주장 수 | 충실도(주장 기준) | 번호만 틀림 | 근거 없음·반대 | 번호까지 맞음 | 완결성(답변한 질문) | 완결성(전체) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | field | 14 | 9/5 | 32 | 90.6% | 0.0% | 9.4% | 100.0% | 48.4% | 31.1% |
| baseline | original | 27 | 27/0 | 110 | 96.4% | 0.0% | 3.6% | 100.0% | 75.0% | 75.0% |
| max_judge | field | 14 | 12/2 | 42 | 95.2% | 0.0% | 4.8% | 100.0% | 47.2% | 40.4% |
| max_judge | original | 27 | 27/0 | 115 | 99.1% | 0.0% | 0.9% | 100.0% | 77.6% | 77.6% |

### 문제가 있는 주장 (일부)

- [baseline/F06] [한계 표시 문장] unsupported: 질문하신 '기울기 변화'가 구체적으로 어떤 현상을 의미하는지에 대해서는 논문에서 확인되지 않으나, 고전계 구간에서의 전도 메커니즘은 위와 같이 다양하게 나타날 수 있습니다. (인용 [], 뒷받침 []) — None of the provided abstracts mention slope change, so the claim that it is not mentioned cannot be verified as supported.
- [baseline/F07] unsupported: Scherrer 방법은 결정립 크기(crystallite size)에 의한 피크 확장을 계산하는 데 사용됩니다. (인용 [3], 뒷받침 []) — Reference [3] mentions Scherrer method among those used to analyze broadening but does not state it calculates crystallite size contribution.
- [baseline/F07] unsupported: 피크가 퍼진 원인이 결정립 크기 감소 때문인지, 격자 변형 때문인지는 위와 같은 분석 기법들을 적용하여 판단해야 합니다. (인용 [3], 뒷받침 []) — Reference [3] does not explicitly state that applying these methods determines the cause; it only attributes broadening to both factors.
- [baseline/F12] unsupported: 패드 컨디셔닝은 패드의 상태를 유지하고 공정 효율을 최적화하기 위해 수행됩니다. (인용 [2], 뒷받침 []) — Reference [2] discusses the influence of conditioning temperature on effectiveness/aggressiveness and optimization of parameters, but does not explicitly state that pad conditioning is performed to maintain pad condition or optimize process efficiency.
- [baseline/Q04] unsupported: 이때 펄스 시간은 0.5초 이상을 적용해야 합니다. (인용 [1], 뒷받침 []) — 초록에는 펄스 시간에 대한 구체적인 수치(0.5초 이상)가 언급되어 있지 않습니다.
- [baseline/Q06] unsupported: 이러한 결함은 하프늄 산화물에 20%의 실리콘(Si)을 첨가하여 하프늄 실리케이트(hafnium silicate)를 형성함으로써 결정화(crystallization)를 방지하는 방식으로 억제할 수 있습니다. (인용 [1], 뒷받침 []) — 참고 논문 [1] 초록은 20% Si 첨가로 하프늄 실리케이트 형성이 결정화를 방지한다고만 서술하고 결함 억제에 대한 직접적인 언급은 없다.
- [baseline/Q19] unsupported: 밀도 기반 군집화(density-based clustering, DBC)를 활용한 웨이퍼맵(wafer map) 분석을 통해 존(zone), 스크래치(scratch), 링(ring) 패턴과 같은 불량 칩의 공간적 패턴을 식별할 수 있습니다 (인용 [1], 뒷받침 []) — 초록 [1]은 존, 스크래치, 링 패턴을 웨이퍼 맵의 공간적 패턴의 예시로 언급하고 DBC 기반 결함 패턴 분석 방법을 제안하지만, 해당 방법이 이들 특정 패턴을 식별할 수 있다는 직접적인 진술은 포함되어 있지 않습니다.
- [baseline/Q27] unsupported: PF 전도는 절연체 내 트랩(trap)을 통한 방출을 의미하는. (인용 [1], 뒷받침 []) — 초록[1]에서는 PF 메커니즘의 구체적인 설명을 제공하지 않으며,仅仅提及 PF 전도와의 전기장 의존성 유사성만 언급한다.
- [max_judge/F03] [한계 표시 문장] unsupported: Other factors such as gas flow problems, precursor supply efficiency, or specific process condition mismatches are not confirmed in the provided papers. (인용 [], 뒷받침 []) — No citation was provided for this claim, and none of the referenced abstracts mention gas flow issues, precursor supply efficiency, or specific process condition mismatches.
- [max_judge/F05] unsupported: 게이트 스택(gate stack)에서 계면 산화막(interfacial layer, IL)인 SiO2의 존재는 장단점이 모두 존재합니다. (인용 [], 뒷받침 []) — The answer provides no citation for this general statement, and while the cited references discuss both advantages and disadvantages, the claim itself lacks a direct supporting citation.
- [max_judge/F06] [한계 표시 문장] unsupported: 질문하신 I-V 곡선상 고전계 구간의 기울기 변화가 구체적으로 어떤 물리적 원인에 의한 것인지, 혹은 특정 조건에서의 변화 양상에 대해서는 논문에서 확인되지 않는다. (인용 [], 뒷받침 []) — No reference explicitly states that the papers do not confirm the cause of I-V curve slope change; the claim is an inference not directly supported by the abstracts.
- [max_judge/F07] [한계 표시 문장] contradicted: 질문하신 현상이 결정립 크기 감소 때문인지 격자 변형 때문인지는 제공된 논문에서 특정 샘플에 대한 분석 결과가 없으므로 단정할 수 없으며, 위 방법들을 통해 개별 기여도를 분석해야 합니다. (인용 [1, 3], 뒷받침 []) — The abstract provides analysis attributing peak broadening to crystallite size and lattice strain, contradicting the claim that no specific sample analysis results are present.
- [max_judge/F12] unsupported: CMP 공정 중 패드 컨디셔닝은 패드의 표면 상태를 유지하고 공정 효율을 높이기 위해 수행됩니다. (인용 [], 뒷받침 []) — 참고 논문 초록에서 패드 컨디셔닝의 목적을 명시적으로 언급한 내용이 없습니다.
- [max_judge/F13] [한계 표시 문장] unsupported: 이러한 결함들이 수율에 미치는 구체적인 수치나 상관관계는 논문에서 확인되지 않음 (인용 [3], 뒷받침 []) — [3] 초록에서는 결함의 분류와 최소화 방안을 설명하지만, 수율에 대한 구체적인 수치나 상관관계가 absent하다는 언급은 없다.
- [max_judge/Q04] unsupported: 이때 펄스 시간은 0.5초 이상을 적용해야 합니다. (인용 [1], 뒷받침 []) — 초록에는 펄스 시간에 대한 구체적인 수치(0.5초 이상)가 언급되어 있지 않습니다.
