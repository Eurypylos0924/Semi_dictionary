# 채점 검수용 표본 (2026-10-26)

채점 LLM의 판정이 맞는지 사람이 확인하기 위한 무작위 표본(seed 0)이다.

### max_judge_nolimit / F12
- 질문: CMP 패드 컨디셔닝은 왜 하고, 안 하면 어떻게 돼?
- 주장: 기존의 컨디셔닝 디스크를 사용할 경우 다이아몬드 분리로 인한 스크래치 발생 및 니켈 용해에 따른 금속 오염 문제가 발생할 수 있습니다.
- 인용한 초록:
  - [1] Physical and Chemical Characteristics of the Ceramic Conditioner in Chemical Mechanical Planarization: Abstract. The purpose of this study was to characterize a new pad conditioning disk in terms of corrosion resistance and CMP performances, such as removal rate, non-uniformity, and contamination of metals and particles on wafers. The new conditioning disk was manufactured using a pattern process on ceramic substrates and a diamond CVD on patterned …
- **채점 판정: supported** (뒷받침 논문 [1]) 논문 1 초록에 'Conventional conditioning disks often encounter problems such as scratches due to the diamond segregation and the metal contamination, which is due to the dissolution of Ni'라고 명시되어 있음.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q26
- 질문: HfO2 게이트 절연막의 누설전류는 전계 영역별로 어떤 전도 메커니즘이 지배하는가?
- 주장: HfO2/TaN 기반 MIM 커패시터에서 고전계 영역의 지배적 전도 메커니즘은 Poole-Frenkel(PF) 방출이다.
- 인용한 초록:
  - [4] High-temperature conduction behaviors of HfO2/TaN-based metal-insulator-metal capacitors: High-temperature (∼90–150 °C) conduction mechanisms of metal-insulator-metal (MIM) capacitors with atomic-layer-deposited HfO2 dielectric are studied. In the low field range, the Schottky emission current is dominant, and the deduced dielectric constant is close to the static one of HfO2. In the high field range, the resulting leakage current compl…
- **채점 판정: supported** (뒷받침 논문 [4]) 논문 4 초록에 'In the high field range, the resulting leakage current complies with the Poole-Frenkel (PF) emission'으로 명시됨.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / Q24
- 질문: XRD 피크의 폭(FWHM)이 넓어지는 원인은 무엇인가?
- 주장: 결정립 크기가 작아질수록 회절 피크의 폭은 증가한다.
- 인용한 초록:
  - [5] Crystallite size and lattice strain of lithiated spinel material for rechargeable battery by X-ray diffraction peak-broadening analysis: High-energy ball milling is performed on Li1.1Mn1.95Fe0.05O4 spinel material, synthesized by sol-gel method for lithium rechargeable battery, at different durations to obtain nanopowders of finite size distributions. The powders are investigated by means of scanning electron microscopy, particle size distribution, and X-ray diffraction (XRD) measur…
- **채점 판정: supported** (뒷받침 논문 [5]) 초록 [5]에서 'XRD results show that the widths of the diffraction peaks increase with the decrease of particle size' 및 'Peak broadening is attributed to contributions of crystallite size'라고 명시함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / Q06
- 질문: 다결정 HfO2와 비정질 HfO2의 결함 상태는 어떻게 다르고, 어떻게 억제할 수 있는가?
- 주장: 하프늄 산화물에 20%의 실리콘을 첨가하여 하프늄 실리케이트를 형성하면 결정화를 방지할 수 있다.
- 인용한 초록:
  - [1] Sub-bandgap defect states in polycrystalline hafnium oxide and their suppression by admixture of silicon: The crystallinity of atomic layer deposition hafnium oxide was found to be thickness dependent, with the thinnest films being amorphous and thick films being at least partially crystalline. Hafnium oxide films fabricated by metalorganic chemical vapor deposition are mostly monoclinic. Formation of hafnium silicate by admixture of 20% Si prevents cr…
- **채점 판정: supported** (뒷받침 논문 [1]) 초록에 'Formation of hafnium silicate by admixture of 20% Si prevents crystallization'이라고 명시되어 있음.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / Q14
- 질문: Cu CMP 중 나노입자 응집은 어떻게 스크래치와 결함을 만드는가?
- 주장: DLA에 의한 결함 생성 확률은 슬러리 재생이나 공정 개선 조치가 없을 경우 약 10~20분 시간 규모에서 크게 증가할 수 있습니다.
- 인용한 초록:
  - [1] Diffusion-Limited Agglomeration and Defect Generation during Chemical Mechanical Planarization: Chemical mechanical planarization ͑CMP͒ of copper involves removal of surface asperities with abrasive particles and polishing processes.This leads to copper-containing nanoparticles extruded into the solution.We model the diffusion-limited agglomeration ͑DLA͒ of such nanoparticles which can rapidly grow to large sizes.These large particles are det…
- **채점 판정: supported** (뒷받침 논문 [1]) Paper 1 states that under realistic conditions the defect generation probability can increase significantly over time scales of ~10 to 20 min from DLA, unless prevented by slurry rejuvenation or process modification measures.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: 표면에 존재하는 유기물이나 용매 잔류물이 핵생성 거동에 큰 영향을 미칩니다.
- 인용한 초록:
  - [5] HfO2 on MoS2 by Atomic Layer Deposition: Adsorption Mechanisms and Thickness Scalability: We report our investigation of the atomic layer deposition (ALD) of HfO2 on the MoS2 surface. In contrast to previous reports of conformal growth on MoS2 flakes, we find that ALD on MoS2 bulk material is not uniform. No covalent bonding between the HfO2 and MoS2 is detected. We highlight that individual precursors do not permanently adsorb on the c…
- **채점 판정: supported** (뒷받침 논문 [5]) 초록 [5]에서 'organic and solvent residues can dramatically change ALD nucleation behavior'라고 명시함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q17
- 질문: 불균형한 웨이퍼맵 데이터로 CNN 결함 분류기를 학습할 때 어떻게 대응하고 성능은 어느 정도인가?
- 주장: CNN 기반 분류: 합성 데이터로 학습한 모델은 98.2%의 테스트 정확도를 기록했습니다.
- 인용한 초록:
  - [5] Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network: Wafer maps provide important information for engineers in identifying root causes of die failures during semiconductor manufacturing processes. We present a method for wafer map defect pattern classification and image retrieval using convolutional neural networks (CNNs). Twenty eight thousand six hundred synthetic wafer maps for 22 defect classes a…
- **채점 판정: supported** (뒷받침 논문 [5]) 초록 5에서 22개 결함 클래스의 합성 웨이퍼 맵으로 학습한 모델이 6600개 테스트 데이터셋에서 98.2% 분류 정확도를 기록했다고 명시함.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / Q19
- 질문: 밀도 기반 군집화로 웨이퍼맵을 분석하면 어떤 불량 패턴을 찾을 수 있는가?
- 주장: 임의의 형태(arbitrarily shaped)를 가진 군집 패턴도 검출이 가능합니다.
- 인용한 초록:
  - [2] A Novel DBSCAN-Based Defect Pattern Detection and Classification Framework for Wafer Bin Map: Defective die on a wafer map tend to cluster in distinguishable patterns, and such defect patterns can provide crucial information to identify equipment problems or process failures in the semiconductor manufacturing. Therefore, it is important to accurately and efficiently classify the defect patterns. In this paper, we propose a novel clustering-…
- **채점 판정: supported** (뒷받침 논문 [2]) 논문 [2] 초록에 'arbitrarily shaped cluster patterns can be detected'라고 직접 언급되어 있음.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge / F03
- 질문: ALD 사이클 수는 같은데 두께가 기대보다 얇게 나와. 뭘 의심해야 해?
- 주장: 증착 공정에서 전구체 펄스 시간이 충분하지 않아 포화(saturation)에 도달하지 못하면 사이클 당 성장률(GPC, growth-per-cycle)이 낮아질 수 있습니다
- 인용한 초록:
  - [1] Scaling to Sub-1 nm Equivalent Oxide Thickness with Hafnium Oxide Deposited by Atomic Layer Deposition: The implementation of gate dielectrics in sub- devices requires optimization of nanometer-thin layers, deposited, e.g., by atomic layer deposition (ALD). In this work, we optimize ALD conditions such as precursor pulse time and deposition temperature for layers with physical thicknesses below . Additionally, we investigate intermediate treatments i…
- **채점 판정: supported** (뒷받침 논문 [1]) 논문 1은 GPC와 Cl 함량의 포화를 달성하기 위해 특정 펄스 시간이 필요하다고 명시하며, 포화 펄스 사용이 서브-EOT 영역에서 게이트 누설 전류를 감소시킴을 보여줌
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / Q17
- 질문: 불균형한 웨이퍼맵 데이터로 CNN 결함 분류기를 학습할 때 어떻게 대응하고 성능은 어느 정도인가?
- 주장: 배치 정규화와 공간 드롭아웃 같은 정규화 기법을 사용하여 분류 성능을 향상시킨다.
- 인용한 초록:
  - [2] A Deep Convolutional Neural Network for Wafer Defect Identification on an Imbalanced Dataset in Semiconductor Manufacturing Processes: Wafer maps contain information about various defect patterns on the wafer surface and automatic classification of these defects plays a vital role to find their root causes. Semiconductor engineers apply various methods for wafer defect classification such as manual visual inspection or machine learning-based algorithms by manually extracting usefu…
- **채점 판정: supported** (뒷받침 논문 [2]) 논문 2 초록에 '배치 정규화와 공간 드롭아웃 같은 최신 정규화 방법을 사용하여 분류 성능을 향상시켰다'고 명시됨.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / Q23
- 질문: Scherrer 식으로 XRD 피크의 FWHM에서 결정립 크기를 계산하는 방법은?
- 주장: 수정된 Scherrer 식(modified Scherrer equation)은 $\ln\beta$를 $\ln(1/\cos\theta)$에 대해 플롯하여 최소 자승법(least squares technique)으로 회귀선의 절편($\ln(K\lambda/L)$)을 구함으로써 단일 결정립 크기 값을 도출한다.
- 인용한 초록:
  - [3] Modified Scherrer Equation to Estimate More Accurately Nano-Crystallite Size Using XRD: Scherrer Equation, L=Kλ/β.cosθ, was developed in 1918, to calculate the nano crystallite size (L) by XRD radiation of wavelength λ (nm) from measuring full width at half maximum of peaks (β) in radian located at any 2θ in the pattern. Shape factor of K can be 0.62 - 2.08 and is usually taken as about 0.89. But, if all of the peaks of a pattern are …
- **채점 판정: supported** (뒷받침 논문 [3]) 초록 [3]에 'Modified Scherrer equation plots lnβ against ln(1/cosθ) and obtains the intercept of a least squares line regression, ln=Kλ/L, from which a single value of L is obtained'라고 명시되어 있다.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다

### max_judge_nolimit / F13
- 질문: CMP 후 세정을 대충 하면 수율에 어떤 영향이 있어?
- 주장: 주어진 소재에 적합한 세정 방법을 선택하기 위해 CMP 후 세정 공정에 대한 이해가 필수적이다.
- 인용한 초록:
  - [1] Review—Post-Chemical Mechanical Planarization Cleaning Technology: Chemical mechanical planarization (CMP), a commonly employed process for attaining local and global planarization in integrated circuits fabrication, leaves contaminants and defects on the surface polished. Due to the miniaturization of devices, new materials/ processes for the fabrication of IC circuits are considered, introducing new post-CMP iss…
- **채점 판정: supported** (뒷받침 논문 [1]) 초록에 'understanding of post-CMP cleaning process is critical to choose an appropriate method for the given material'라고 명시됨.
- 사람 확인: [ ] 판정이 맞다  [ ] 틀리다
