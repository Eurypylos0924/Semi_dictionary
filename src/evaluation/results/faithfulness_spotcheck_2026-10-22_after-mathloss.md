# 채점 검수용 표본 (2026-10-22)

채점 LLM의 판정이 맞는지 사람이 확인하기 위한 무작위 표본(seed 0)이다.

### max_judge / F13
- 질문: CMP 후 세정을 대충 하면 수율에 어떤 영향이 있어?
- 주장: 세정을 '대충' 했을 때 발생하는 구체적인 수율 저하 수치나 공정상의 정량적 변화는 논문에서 확인되지 않음
- 인용한 초록:
  - (인용 없음)
- **채점 판정: supported** (뒷받침 논문 [1, 2, 3]) 제공된 논문 초록([1],[2],[3]) 어디에도 부적절한 세정 시 구체적인 수율 저하 수치나 정량적 변화에 대한 언급이 없음.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q21
- 질문: 반도체 제조의 수율 분석에는 어떤 기법들이 쓰이는가?
- 주장: 베이지안 분석(Bayesian analysis)을 통해 공정 워크플로우 내 수율 손실의 주요 원인을 식별하며, 노드 폴딩(folding) 및 클러스터링(clustering)을 통해 분석의 복잡성을 줄인다.
- 인용한 초록:
  - [4] A Method for Reducing Noise and Complexity in Yield Analysis for Manufacturing Process Workflows: In this paper, we present an approach to analyze a process workflow for the fabrication of semiconductor integrated circuits in order to identify the source(s) of yield loss. Specifically, we address computational challenges using Bayesian analysis to isolate key process steps affecting the global yield loss of a given workflow. Bayesian inference …
- **채점 판정: supported** (뒷받침 논문 [4]) 논문 4 초록에서 Bayesian analysis로 주요 공정 단계 식별, folding과 clustering으로 분석 단순화를 설명함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q10
- 질문: XRD로 결정성 재료에서 어떤 구조 관련 물성을 구할 수 있는가?
- 주장: 열팽창 계수(thermal expansion coefficient)를 구할 수 있다.
- 인용한 초록:
  - [5] X-ray Diffraction Techniques for Mineral Characterization: A Review for Engineers of the Fundamentals, Applications, and Research Directions: For many decades, X-ray diffraction (XRD) has been used for material characterization. With the recent development in material science understanding and technology, various new materials are being developed, which requires upgrading the existing analytical techniques such that intricate problems can be solved. Although, XRD is a well-established no…
- **채점 판정: supported** (뒷받침 논문 [5]) 논문 5 초록에 열팽창 계수가 XRD 패턴으로 얻을 수 있는 정보로 명시되어 있다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: 인시츄 분광 타원계측법(in situ spectroscopic ellipsometry)을 통해 사이클 수에 따른 두께 변화와 핵생성 거동을 직접 모니터링하여 분석할 수 있습니다
- 인용한 초록:
  - [4] In situspectroscopic ellipsometry as a versatile tool for studying atomic layer deposition: In this paper recent work on the application of in situ spectroscopic ellipsometry (SE) during thin film synthesis by atomic layer deposition (ALD) is reviewed. In particular, the versatility of this all-optical diagnostic is demonstrated by results obtained on Al 2 O 3 , HfO 2 , Er 2 O 3 , TiO 2 , Ta 2 O 5 , TiN and TaN x films with thicknesses ra…
- **채점 판정: supported** (뒷받침 논문 [4]) 논문 4는 ALD 사이클 사이에 SE 데이터를 획득하여 사이클 수에 따른 두께 변화를 모니터링함으로써 사이클당 성장률, 포화 곡선, 다양한 기판에서의 핵생성 거동 및 반단위 사이클 중 표면 변화를 탐구할 수 있다고 명시함
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q15
- 질문: Cu CMP에서 과산화수소(H2O2)와 BTA는 각각 제거율에 어떤 역할을 하는가?
- 주장: Cu CMP 공정에서 과산화수소(hydrogen peroxide)는 산화제(oxidant)로서 구리(Cu)의 용해를 촉진하는 역할을 합니다.
- 인용한 초록:
  - [1] Chemical Mechanical Planarization of Copper: Role of Oxidants and Inhibitors: Investigations were carried out to understand the effect of hydrogen peroxide as an oxidant and benzotriazole (BTA) as an inhibitor on the chemical mechanical planarization (CMP) of copper. Cu-CMP was studied using electrochemistry and removal rate measurements in solutions containing the oxidizer and the inhibitor. In the presence of 0.1 M glycine…
- **채점 판정: supported** (뒷받침 논문 [1]) 초록 [1]은 과산화수소를 산화제로, BTA를 억제제로 명시하고 있으며 과산화수소 존재 시 Cu 용해가 증가한다고 기술함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q23
- 질문: Scherrer 식으로 XRD 피크의 FWHM에서 결정립 크기를 계산하는 방법은?
- 주장: L: 결정립 크기(nano-crystallite size)
- 인용한 초록:
  - [4] Modified Scherrer Equation to Estimate More Accurately Nano-Crystallite Size Using XRD: Scherrer Equation, L=Kλ/β.cosθ, was developed in 1918, to calculate the nano crystallite size (L) by XRD radiation of wavelength λ (nm) from measuring full width at half maximum of peaks (β) in radian located at any 2θ in the pattern. Shape factor of K can be 0.62 - 2.08 and is usually taken as about 0.89. But, if all of the peaks of a pattern are …
- **채점 판정: supported** (뒷받침 논문 [4]) 초록 [4]에 'nano crystallite size (L)'로 정의되어 있음
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q16
- 질문: CMP 후 세정(post-CMP cleaning)이 중요한 이유는 무엇인가?
- 주장: CMP 공정은 집적 회로 제조 시 국부적 및 전체적인 평탄화를 달성하기 위해 사용된다.
- 인용한 초록:
  - [1] Review—Post-Chemical Mechanical Planarization Cleaning Technology: Chemical mechanical planarization (CMP), a commonly employed process for attaining local and global planarization in integrated circuits fabrication, leaves contaminants and defects on the surface polished. Due to the miniaturization of devices, new materials/ processes for the fabrication of IC circuits are considered, introducing new post-CMP iss…
- **채점 판정: supported** (뒷받침 논문 [1]) 논문 1 초록에 'CMP는 집적 회로 제조에서 국부적 및 전체적인 평탄화를 달성하기 위해 흔히 사용되는 공정'이라고 명시되어 있음.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q23
- 질문: Scherrer 식으로 XRD 피크의 FWHM에서 결정립 크기를 계산하는 방법은?
- 주장: 선형 흡수 계수(linear absorption coefficients)가 2117.3 cm⁻¹ 미만인 결정의 경우, 최대 600 nm 크기까지 유효하며, 2θ > 60°인 피크를 사용하면 최대 1 µm까지 적용 범위를 넓힐 수 있습니다.
- 인용한 초록:
  - [2] The Scherrer equation and the dynamical theory of X-ray diffraction: The Scherrer equation is a widely used tool to determine the crystallite size of polycrystalline samples. However, it is not clear if one can apply it to large crystallite sizes because its derivation is based on the kinematical theory of X-ray diffraction. For large and perfect crystals, it is more appropriate to use the dynamical theory of X-ray …
- **채점 판정: supported** (뒷받침 논문 [2]) 초록 [2]에서 linear absorption coefficients below 2117.3 cm(-1)일 때 600 nm까지 유효, 2θ > 60° 피크 사용 시 1 µm까지 확장 가능하다고 명시함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / F06
- 질문: I-V 곡선에서 고전계 구간의 기울기가 바뀌는데, 이건 어떤 전도 메커니즘이야?
- 주장: Hf 실리케이트(Hf silicate) 박막에서도 풀-프렌켈 전도가 나타납니다.
- 인용한 초록:
  - [5] An asymmetry of conduction mechanisms and charge trapping in thin high-k HfxTiySizO films: The electrical behavior of high-permittivity (high-k) hafnium titanium silicate (HfxTiySizO) layers with different Hf:Ti ratios in the films is investigated. The films were deposited by metal-organic chemical-vapor deposition using a mixture of two single-source precursors for the deposition of Hf silicate and Ti silicate. The attention is focused …
- **채점 판정: supported** (뒷받침 논문 [5]) 초록 [5]에서 'Poole-Frenkel conduction in pure Hf silicates'라고 명시함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: ALD 공정에서 GPC는 전구체 펄스 시간과 증착 온도, 중간 처리 과정 등에 의해 결정되며
- 인용한 초록:
  - [1] Scaling to Sub-1 nm Equivalent Oxide Thickness with Hafnium Oxide Deposited by Atomic Layer Deposition: The implementation of gate dielectrics in sub- devices requires optimization of nanometer-thin layers, deposited, e.g., by atomic layer deposition (ALD). In this work, we optimize ALD conditions such as precursor pulse time and deposition temperature for layers with physical thicknesses below . Additionally, we investigate intermediate treatments i…
- **채점 판정: supported** (뒷받침 논문 [1]) 논문 1은 전구체 펄스 시간과 증착 온도를 최적화 조건으로 다루고, 중간 처리가 GPC에 영향을 미침을 명시함
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### baseline / Q22
- 질문: 반도체 제조에서 생성형 AI 가상 비서가 필요한 이유는 무엇인가?
- 주장: 전통적인 제조 시스템은 인적 오류에 취약하다.
- 인용한 초록:
  - [1] Generative AI for Intelligent Manufacturing Virtual Assistants in the Semiconductor Industry: As semiconductor manufacturing complexity escalates, the intricacy of corresponding manufacturing systems intensifies. These extensive systems necessitate diverse engineering expertise for effective operation and analysis. For instance, yield engineers analyze yield systems, process engineers interpret FDC parameters, and equipment engineers monito…
- **채점 판정: supported** (뒷받침 논문 [1]) 초록에 'They are susceptible to human error'라고 명시됨.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F11
- 질문: dishing이랑 erosion은 뭐가 다르고, 각각 뭘 조절해서 줄여?
- 주장: 제공된 논문에서 dishing과 erosion의 정의적 차이에 대해서는 구체적으로 설명하고 있지 않다.
- 인용한 초록:
  - (인용 없음)
- **채점 판정: supported** (뒷받침 논문 []) 참고 논문 1~5 초록 어디에도 dishing과 erosion의 정의적 차이를 설명한 내용이 없다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다
