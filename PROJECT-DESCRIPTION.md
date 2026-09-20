# 프로젝트 명세서 (MIDI Instrument Definition Generator)

이 문서는 프로젝트 고유 지침의 단일 원천이다. 전사 공통 규범은 `AGENTS.md`(허브 SSOT)를 따르며, 이 문서는 이 저장소에만 해당하는 내용을 담는다.

## 1. Goal & Vision (목표 및 비전)

- 목적: 디지털피아노 음색을 DAW에서 고르려면 bank 번호를 손으로 계산해야 하는 불편을 없앤다.
- 수단: MIDI bank select 프로토콜을 역분석해 제조사별 악기 선택 체계를 Cakewalk `.ins` 악기 정의 파일로 구현한다.
- 대상 기종: Roland HP603 (318음색 / 40 bank), Yamaha CLP-685 (511음색 / 53 bank).
- 이 프로젝트의 값어치는 코드가 아니라 **도메인 지식**이다. 498행의 코드는 얇은 변환 계층이고, 어려운 것은 829개 악기 주소를 알아내는 일이었다.

### 공식 가이드 및 문서

| 문서 | 위치 |
| :--- | :--- |
| 사용법·재생성 절차·참고 문서 링크 | `README.md` |
| ATD 편입 케이스 스터디 (프로토콜 분석 본문) | `docs/PROJECT-PROMOTION.md` |
| ATD 포트폴리오 연동 규격 (SSOT) | `docs/PROMOTION-SPEC.toml` |
| ATD 편입 감사 보고서 (적발 20건) | `docs/AUDIT-REPORT.md` |
| ATD 편입 검증 보고서 (PASS) | `docs/VERIFICATION-REPORT.md` |
| 라이선스 | `LICENSE` (MIT) |

### ATD 편입 프레임

이 프로젝트는 **ATD 편성 하에 개발되지 않았다.** 디렉터(Mike)가 2019년에 시작해 2025년에 확장한 개인 프로젝트이며, ATD는 2026년에 편입하여 분석·감사·문서화만 수행했다. `AGENTS.md` §5-1 의 `Adopted Project` 프레임을 따른다.

## 2. Domain & System Mission (도메인 및 시스템 핵심 미션)

### 도메인 규칙: MIDI Bank Select

음색 선택은 세 바이트로 전송된다.

```
CC#0   Bank Select MSB
CC#32  Bank Select LSB
PC     Program Change

BankNumber = CC#0 * 128 + CC#32      # 14비트, 16,384 bank x 128 program
```

표준이 점유한 영역은 `MSB=120`(드럼)과 `MSB=121`(GM2)뿐이고, 나머지는 제조사 자유 영역이다. **여기서 벤더가 갈린다.**

| | Roland HP603 | Yamaha CLP-685 |
| :--- | :--- | :--- |
| 공용·표준 영역 | `120` 드럼 · `121` GM2 | `0` XG · `64` SFX (Yamaha 사적 규격) |
| 프리셋 MSB | 낮은 값 여럿 (0~47) | `108` 단일 |
| LSB 의미 | 음색 계열 (64~71이 사적 영역) | 변주 깊이 (0~7, 100) |
| PC 의미 | bank 내 목록 순번 | GM 프로그램 계열 |

- Roland 네이티브 50음색은 LSB 64~71에 있고, `bank 0`(MSB 0 / LSB 0)만 GM 표준 bank 로서 prog 40·42·45 세 건을 담는다.
- 두 주소 체계는 **호환되지 않는다.** bank 번호를 넘겨줄 공통 표기가 존재하지 않는다.

### 시스템 요구사항 및 제약

- 출력은 Cakewalk `.ins` 포맷이어야 한다. `.Patch Names` + `.Instrument Definitions` 두 구역으로 구성된다.
- `.ins` 는 CRLF 로 체크아웃되어야 한다(Cakewalk 는 Windows 애플리케이션). `.gitattributes` 가 이를 강제한다.
- bank 이름은 MIDI 문서에서 얻을 수 없다. 실기에서 확인하며 붙인 값이므로 그 사실을 코드 주석에 남긴다.
- 제3자 저작물(제조사 PDF)은 재배포하지 않는다. `reference/` 는 `.gitignore` 로 제외하고, 문서에는 배포처 링크만 남긴다.

### 데이터 자산

| 데이터 | 규모 | 출처 |
| :--- | :--- | :--- |
| `hp603 instruments.txt` | 318건 (326행) | Roland LX-7 MIDI 구현 문서 p.12-14 수작업 전사 |
| `data/yamaha-clp685-data.txt` | 511건 (573행) | Yamaha CLP-685/695GP Data List 수작업 전사 |
| `data/yamaha-clp685-data.toml` | 위 데이터의 변환 결과 | `make_toml.py` 산출물. 생성기와 앱이 읽는 입력이므로 커밋한다 |

**Yamaha 원문은 저장소에 없다.** Roland 전사는 `Midi_Implementatie_Roland_LX-7.pdf` 로 대조할 수 있었으나 Yamaha 쪽은 전사본만 존재한다. 따라서 Yamaha 수치는 전사본 기준 검증이며 제조사 원문과의 일치 여부는 확인 범위 밖이다.

## 3. Workflows & Architecture (핵심 워크플로우 및 체계)

### 데이터 흐름

```
제조사 PDF ──수작업 전사──> 텍스트 데이터 ──┬─> generate_cakewalk_ins.py ───────> Roland HP603.ins
                                          │                                   (450행 / 40 bank)
                                          └─> make_toml.py ─> .toml ─┬─> generate_cakewalk_yamaha_ins.py
                                                                     │   ─> Yamaha CLP-685.ins
                                                                     │      (689행 / 53 bank)
                                                                     └─> find_instruments.py
                                                                         (Streamlit 검색 앱)

실기 검증: test_program_change.py  (python-rtmidi; bank select 3바이트 직접 구성)
           find_roland_gm_inst.py  (mido; GM2 On 시스엑스 F0 7E 7F 09 03 F7 선행)
```

### 컴포넌트

| 파일 | 행수 | 역할 |
| :--- | :--- | :--- |
| `generate_cakewalk_ins.py` | 114 | Roland `.ins` 생성. 표준 라이브러리만 사용 |
| `generate_cakewalk_yamaha_ins.py` | 107 | Yamaha `.ins` 생성. TOML 입력 |
| `find_instruments.py` | 76 | Streamlit 악기 검색 앱 |
| `find_roland_gm_inst.py` | 89 | mido 기반 bank/patch 탐색 (대화형) |
| `test_program_change.py` | 63 | python-rtmidi 기반 실기 검증 (대화형) |
| `make_toml.py` | 49 | 데이터 txt → TOML 변환 |

### 핵심 파싱 규칙

음색 이름에 공백이 있어 앞에서 자르면 경계를 알 수 없다. **뒤에서 3개 토큰을 숫자로 읽는다.**

```python
cval=list(map(int, tokens[-3:]))
tokens[-3:]=[]
inst[group].append([int(tokens[0]), ' '.join(tokens[1:])]+cval)
```

이 규칙 하나로 `Nason flt 8'` 처럼 공백과 특수문자가 섞인 이름도 파싱된다.

### 안전장치

- `generate_cakewalk_ins.py` 의 bank 이름은 쌍 목록(`_BANK_NAME_PAIRS`)으로 정의한다. 딕셔너리 리터럴은 중복 키를 조용히 덮어쓰므로(실제로 `GM E` 가 소실된 원인) 길이 검사로 중복을 검출한다.
- 미등록 bank 는 산출 직전에 검사하여 중단한다.

## 4. Architecture Roadmap (아키텍처 로드맵)

### 완료된 마일스톤

- **2019.10** Roland HP603 지원. 데이터 전사, bank 이름 부여, 실기 검증 도구 제작.
- **2025.12** Yamaha CLP-685 확장. TOML 데이터 계층 도입, Streamlit 검색 앱, Yamaha 생성기.
- **2026.09** ATD 편입. 전수 분석·감사(적발 20건)·검증(PASS)·문서화. 감사 우선순위 항목 전부 해소.

### 개선 백로그

감사 적발 20건의 전체 목록과 근거는 `docs/AUDIT-REPORT.md` 에 있다. 편입 과정에서 해소한 항목은 다음과 같다.

- bank 이름 사전 중복 키 3건 제거 및 GM/Effect 계열 이름 정합화
- 출력 줄바꿈 CRLF 고정 + `.gitattributes` 추가 (커밋 시 LF 로 정규화되어 Windows 사용자가 LF 를 받던 문제)
- `generate_cakewalk_yamaha_ins.py` 의 Roland 잔재(미호출 함수·bank 사전)와 벤더 오표기 정정
- `find_instruments.py` TOML 2단계 구조 대응 (기동 불가 상태였음)
- `find_roland_gm_inst.py` 의 컨트롤 번호·값 혼동 수정 (bank select 가 무동작이었음)
- `hp603 instruments.txt` 와 `data/yamaha-clp685-data.toml` 복원·커밋 (새 체크아웃에서 생성기 실행 불가였음)
- `LICENSE`(MIT) 및 `.gitignore` 추가
- 제3자 PDF 배포 제외 및 문서 링크화
- README 재생성 절차·의존성 표 추가, `CCE2` → `CC32` 오타 정정

남은 항목은 코드 결함이 아니라 검증 불가 또는 문서 정밀도 문제다.

- `reference/` 의 Drums bank(MSB 120) 실기 미검증 — 하드웨어가 있어야 확인 가능
- Yamaha 511건 전사의 제조사 원문 대조 — 원문이 저장소에 없음
- 자동 테스트 0건. Streamlit 을 띄워야 드러나는 오류 계열에 대한 검증 수단이 없음
- `requirements.txt` 가 UTF-16 이라 UTF-8 을 가정하는 일반 도구가 읽지 못한다. 내용도 환경 전체 `pip freeze` 이며 `python-rtmidi` 가 누락되어 있다
