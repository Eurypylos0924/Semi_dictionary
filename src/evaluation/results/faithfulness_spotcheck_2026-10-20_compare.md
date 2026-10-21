# 채점 검수용 표본 (2026-10-20)

채점 LLM의 판정이 맞는지 사람이 확인하기 위한 무작위 표본(seed 0)이다.

### max_judge / Q12
- 질문: CMP 공정에서 스크래치를 줄이는 방법에는 어떤 것이 있는가?
- 주장: 표면 기능화된 고분자 하이브리드 입자를 사용하면 기존 연마제 대비 마찰 계수를 낮추고 표면 스크래치를 줄일 수 있다.
- 인용한 초록:
  - [5] Process optimization and consumable development for Chemical Mechanical Planarization (CMP) processes: Chemical Mechanical Planarization (CMP) is one of the most critical processing steps that enables fabrication of multilevel interconnects. The success of CMP process is limited by the implementation of an optimized process and reduction of process generated defects along with post CMP surface characteristics such as dishing and erosion. This thesis…
- **채점 판정: supported** (뒷받침 논문 [5]) 참고 논문[5] 초록에 표면 기능화된 폴리머 입자가 낮은 마찰 계수와 기존 대비 훨씬 적은 표면 스크래치를 유도한다고 명시되어 있다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: Other factors such as gas flow problems, precursor supply efficiency, or specific process condition mismatches are not confirmed in the provided papers.
- 인용한 초록:
  - (인용 없음)
- **채점 판정: unsupported** (뒷받침 논문 []) No citation was provided for this claim, and none of the referenced abstracts mention gas flow issues, precursor supply efficiency, or specific process condition mismatches.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q26
- 질문: HfO2 게이트 절연막의 누설전류는 전계 영역별로 어떤 전도 메커니즘이 지배하는가?
- 주장: Pt/HfO2/Si 구조: 터널링 보조 풀-프렌켈(Tunneling-assisted Poole-Frenkel, TAPF) 메커니즘이 제안되었으며, 이는 전계 의존성이 풀-프렌켈 전도와 유사하나 활성화 에너지는 쇼트키 장벽 높이(Schottky barrier height)와 관련이 있습니다
- 인용한 초록:
  - [5] Tunneling-assisted Poole-Frenkel conduction mechanism in HfO2 thin films: Tunneling-assisted Poole-Frenkel (TAPF) mechanism, which represents electron tunneling from a metal electrode to traps in a nearby insulator layer followed by detrapping of the electrons from the traps by virtue of a lowered potential well due to an applied electric field, is suggested in this study to precisely describe the electrical conduction b…
- **채점 판정: supported** (뒷받침 논문 [5]) Reference [5] proposes the TAPF mechanism for Pt/HfO2/Si, noting similar field dependence to PF but activation energy tied to the Schottky barrier height.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q08
- 질문: GaAs 위에 ALD로 만든 초박막 Al2O3의 누설전류와 항복전계는 어느 수준인가?
- 주장: 또한, 막 두께가 1 nm에 가까워질수록 항복전계가 최대 30 MV/cm까지 크게 향상되는 것이 관찰되었습니다.
- 인용한 초록:
  - [1] Leakage current and breakdown electric-field studies on ultrathin atomic-layer-deposited Al2O3 on GaAs: Atomic-layer deposition (ALD) provides a unique opportunity to integrate high-quality gate dielectrics on III-V compound semiconductors. We report detailed leakage current and breakdown electric-field characteristics of ultrathin Al2O3 dielectrics on GaAs grown by ALD. The leakage current in ultrathin Al2O3 on GaAs is comparable to or even lower th…
- **채점 판정: supported** (뒷받침 논문 [1]) Reference [1] observes a significant enhancement of breakdown electric field up to 30 MV/cm as the film thickness approaches 1 nm.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: Sufficient precursor pulse time is required to achieve saturation in growth-per-cycle (GPC); insufficient pulse time can prevent GPC saturation.
- 인용한 초록:
  - [1] Scaling to Sub-1 nm Equivalent Oxide Thickness with Hafnium Oxide Deposited by Atomic Layer Deposition: The implementation of gate dielectrics in sub- devices requires optimization of nanometer-thin layers, deposited, e.g., by atomic layer deposition (ALD). In this work, we optimize ALD conditions such as precursor pulse time and deposition temperature for layers with physical thicknesses below . Additionally, we investigate intermediate treatments i…
- **채점 판정: supported** (뒷받침 논문 [1]) Reference [1] indicates that specific pulse times must be applied to achieve saturation in GPC and Cl content.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q16
- 질문: CMP 후 세정(post-CMP cleaning)이 중요한 이유는 무엇인가?
- 주장: With device miniaturization, new materials and processes introduce new cleaning issues, making understanding essential to select appropriate cleaning methods for a given material.
- 인용한 초록:
  - [1] Review—Post-Chemical Mechanical Planarization Cleaning Technology: Chemical mechanical planarization (CMP), a commonly employed process for attaining local and global planarization in integrated circuits fabrication, leaves contaminants and defects on the surface polished. Due to the miniaturization of devices, new materials/ processes for the fabrication of IC circuits are considered, introducing new post-CMP iss…
- **채점 판정: supported** (뒷받침 논문 [1]) The abstract mentions that miniaturization leads to new post-CMP issues and that understanding the cleaning process is critical to choose an appropriate method for the given material.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q08
- 질문: GaAs 위에 ALD로 만든 초박막 Al2O3의 누설전류와 항복전계는 어느 수준인가?
- 주장: GaAs 위에 원자층 증착(Atomic-layer deposition, ALD)으로 형성한 초박막 Al2O3의 누설전류는 최첨단 Si 기반 SiO2와 비슷하거나 더 낮은 수준입니다.
- 인용한 초록:
  - [1] Leakage current and breakdown electric-field studies on ultrathin atomic-layer-deposited Al2O3 on GaAs: Atomic-layer deposition (ALD) provides a unique opportunity to integrate high-quality gate dielectrics on III-V compound semiconductors. We report detailed leakage current and breakdown electric-field characteristics of ultrathin Al2O3 dielectrics on GaAs grown by ALD. The leakage current in ultrathin Al2O3 on GaAs is comparable to or even lower th…
- **채점 판정: supported** (뒷받침 논문 [1]) Reference [1] states the leakage current in ultrathin Al2O3 on GaAs is comparable to or even lower than that of state-of-the-art SiO2 on Si.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F09
- 질문: 박막 XRD에서 피크가 안 보이면 비정질이라고 봐도 돼?
- 주장: X-ray 회절(XRD)은 결정질 재료의 장거리 질서(long-range order)와 비결정질 재료의 단거리 질서(short-range order)를 식별하는 데 사용됩니다.
- 인용한 초록:
  - [2] Experimental methods in chemical engineering: X‐ray diffraction spectroscopy— XRD: Abstract X‐ray diffraction (XRD) analysis identifies the long‐range order (ie, the structure) of crystalline materials and the short‐range order of non‐crystalline materials. From this information we deduce lattice constants and phases, average grain size, degree of crystallinity, and crystal defects. Advanced XRD provides information about strain,…
- **채점 판정: supported** (뒷받침 논문 [2]) Reference [2] states that XRD identifies the long-range order of crystalline materials and the short-range order of non-crystalline materials.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q17
- 질문: 불균형한 웨이퍼맵 데이터로 CNN 결함 분류기를 학습할 때 어떻게 대응하고 성능은 어느 정도인가?
- 주장: 학습 전략: 지배적인 'None' 클래스의 수를 제어하거나, 모델에 균형 함수(balance function)를 적용하여 성능을 개선합니다
- 인용한 초록:
  - [2] CBAM-enhanced lightweight CNN for wafer map defect classification: Automated interpretation of wafer maps is central to manufacturing quality monitoring. Identifying rare defects with less detailed wafer maps is a challenging task. Moreover, class imbalance, heavyweight backbones, and limited model transparency are constraints for the real-world deployment of defective wafer identification. However, a nine-class w…
  - [4] A Deep convolutional neural network with residual blocks for wafer map defect pattern recognition: Abstract Different deep convolution neural network (DCNN) models have been proposed for wafer map pattern identification and classification tasks in previous studies. However, factors such as input image resolution effect on the classification performance of the proposed models and class imbalance in the training set after splitting the data into t…
- **채점 판정: supported** (뒷받침 논문 [2, 4]) [2]에서는 지배적인 None 클래스의 수를 제어하는 controlled reduction을 언급하고, [4]에서는 균형 함수를 적용한 모델이 성능을 개선할 수 있다고 언급하고 있습니다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q09
- 질문: ZrO2/Al2O3/ZrO2 MIM 커패시터에서 Al2O3를 삽입하는 이유와 주된 누설 전도 메커니즘은?
- 주장: 해당 구조의 주된 유전체 전도 메커니즘은 쇼트키 방출로 제시되었습니다.
- 인용한 초록:
  - [1] High density metal-insulator-metal capacitor based on ZrO2∕Al2O3∕ZrO2 laminate dielectric: The metal-insulator-metal (MIM) capacitor for analog and rf applications has been developed with ZrO2∕Al2O3∕ZrO2 laminate as the dielectric. The high capacitance density of 21.54fF∕μm2 can be achieved due to the tetragonal ZrO2 which makes the higher dielectric constant of 38.7. This MIM capacitor also demonstrates the quadratic voltage coefficient…
- **채점 판정: supported** (뒷받침 논문 [1]) 초록에 쇼트키 방출이 주요 유전체 전도 메커니즘으로 제시되었다고 명시되어 있다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q17
- 질문: 불균형한 웨이퍼맵 데이터로 CNN 결함 분류기를 학습할 때 어떻게 대응하고 성능은 어느 정도인가?
- 주장: Opt-ResDCNN 모델은 입력 해상도에 따라 90.28%에서 99.90% 사이의 정확도를 보였습니다
- 인용한 초록:
  - [4] A Deep convolutional neural network with residual blocks for wafer map defect pattern recognition: Abstract Different deep convolution neural network (DCNN) models have been proposed for wafer map pattern identification and classification tasks in previous studies. However, factors such as input image resolution effect on the classification performance of the proposed models and class imbalance in the training set after splitting the data into t…
- **채점 판정: supported** (뒷받침 논문 [4]) [4]의 초록에서는 네 가지 해상도에서의 정확도가 각각 99.90%, 99.86%, 90.28%, 98.88%로 보고되어 90.28%~99.90% 범위를 보여줍니다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F05
- 질문: gate stack에서 계면에 SiO2 층이 있으면 좋은 거야, 나쁜 거야?
- 주장: 게이트 스택(gate stack)에서 계면 산화막(interfacial layer, IL)인 SiO2의 존재는 장단점이 모두 존재합니다.
- 인용한 초록:
  - (인용 없음)
- **채점 판정: unsupported** (뒷받침 논문 []) The answer provides no citation for this general statement, and while the cited references discuss both advantages and disadvantages, the claim itself lacks a direct supporting citation.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다
