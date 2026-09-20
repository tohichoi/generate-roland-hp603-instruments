# ATD 편입 검증 보고서 — generate-roland-hp603-instruments

- 검증자: Noah (S.P.I.R.E. 수석 QA 아키텍트 / 테스트 최적화관)
- 검증일: 2026-09-21
- 대상: `/home/x/Workspace/generate-roland-hp603-instruments`
- 최종 판정: **PASS**

## 0. 검증 환경 및 방법

| 항목 | 값 |
|---|---|
| Roland 생성기 실행기 | `python3` (표준 라이브러리만 사용) |
| Yamaha 생성기 실행기 | `/tmp/hp603venv/bin/python` (격리 venv, toml/tomli/rich 설치) |
| 시스템 파이썬 오염 | 없음 — Yamaha 관련 실행은 전부 `/tmp/hp603venv` 로만 수행 |
| 검증 하네스 | `/tmp/verify_hp603.py` (원본 파서 + `.ins` 파서 + 전수 집합 대조) |
| 회귀 테스트 위치 | `/tmp/regress` (프로젝트 격리 복사본) — 저장소 소스 무수정 |
| 소스 무결성 | 검증 전후 `md5sum` 동일 (아래 §6) |
| 생성 산출물 | 커밋하지 않음. 모든 재생성 결과는 `/tmp` 로만 출력 |

대조에 사용한 핵심 항등식은 생성기와 동일한 `bank = msb*128 + lsb` 이며, 모든 MSB/LSB 가
7-bit(0..127) 범위임을 확인했다 (Roland msb 0–121 / lsb 0–71, Yamaha msb 0–108 / lsb 0–101).
따라서 `msb*128+lsb` 는 (msb,lsb) 쌍에 대한 전단사이므로 **bank id 충돌은 구조적으로 불가능**하다.

---

## 1. 파이프라인 재현성 — PASS

### 실행 명령

```
cd /home/x/Workspace/generate-roland-hp603-instruments
python3 generate_cakewalk_ins.py                > /tmp/r1.ins   # 재현성용
python3 generate_cakewalk_ins.py                > /tmp/r2.ins   # 멱등성용
/tmp/hp603venv/bin/python generate_cakewalk_yamaha_ins.py > /tmp/y1.ins
/tmp/hp603venv/bin/python generate_cakewalk_yamaha_ins.py > /tmp/y2.ins
```

4회 실행 모두 `exit code 0`, stderr 0 바이트.

### 결과

| 비교 | 명령 | 결과 | md5 |
|---|---|---|---|
| Roland: 재생성 vs 커밋 산출물 | `cmp /tmp/r1.ins "Roland HP603.ins"` | **완전 일치** | `e8157ae740ba5025fb85aa7f4cbfa729` (양쪽 동일) |
| Roland: 멱등성 (1회차 vs 2회차) | `cmp /tmp/r1.ins /tmp/r2.ins` | **완전 일치** | `e8157ae7…` |
| Yamaha: 재생성 vs 커밋 산출물 | `cmp /tmp/y1.ins "Yamaha CLP-685.ins"` | **완전 일치** | `548c3fd8288a863aa16f165fa031427d` (양쪽 동일) |
| Yamaha: 멱등성 (1회차 vs 2회차) | `cmp /tmp/y1.ins /tmp/y2.ins` | **완전 일치** | `548c3fd8…` |

`cmp` 는 바이트 단위 비교이며 4건 모두 차이 0. Python dict 의 삽입 순서 보존 특성상
출력 순서가 결정적이므로 멱등성은 실행 시점과 무관하게 성립한다.

### 줄바꿈 (CRLF 고정) 검증

| 파일 | 총 LF | CRLF | 단독 LF | 단독 CR | CRLF 종료 |
|---|---|---|---|---|---|
| `/tmp/r1.ins` (Roland) | 450 | 450 | **0** | 0 | 예 |
| `/tmp/y1.ins` (Yamaha) | 689 | 689 | **0** | 0 | 예 |

`sys.stdout.reconfigure(newline='\r\n')` 가 두 생성기 모두에서 실제로 동작하며, LF 가
섞인 줄은 0건이다. 정규식 `(?<!\r)\n` 으로 스캔한 결과 매칭 0건.

---

## 2. 전수 주소 대조 — PASS (누락 0 / 중복 0 / 추가 0)

원본 데이터에서 직접 파싱한 튜플 집합과 산출물에서 파싱한 집합을 다중집합(Counter)으로
비교했다. 누락 = `원본 − 산출물`, 추가 = `산출물 − 원본`.

### 2.1 Roland HP603

**원본 `hp603 instruments.txt` 행 구성 (총 326행)**

```
group_headers=8, instrument_rows=318, total=326
```

즉 "326행"은 파일 전체 줄 수이며, 실제 음색 데이터는 318행이다. 그룹 헤더 8건은
`Piano, E.Piano, Organ, Strings, Upright, Classical, Drums, GM2`.

**주소 파싱 필드 순서**: `group, index, name…, MSB, LSB, PC` (마지막 3토큰 = MSB/LSB/PC,
이름은 가변 길이). 생성기 소스의 `cval=list(map(int, tokens[-3:]))` 와 일치.

| 지표 | 원본 | 산출물 | 판정 |
|---|---|---|---|
| 총 음색 수 | 318 | 318 | 일치 |
| bank 수 | 40 | 40 (`.Patch Names` 섹션) | 일치 |
| bank id 집합 | 40개 | 40개 | **원본에만 0 / 산출물에만 0** |
| `Patch[bank]=이름` 정의 수 | — | 40 | 일치 |
| (bank, PC, name) 3중항 | 318 | 318 | **누락 0 / 추가 0** |
| 원본 자체 중복 3중항 | 0 | — | 중복 없음 |
| bank 내 PC 중복 (원본) | 0 | — | 중복 없음 |
| bank 내 PC 중복 (산출물) | — | 0 | 중복 없음 |
| bank 내 이름 집합 불일치 | — | — | **0건** |
| 매칭 실패한 섹션 | — | — | **0건** |

추가로, 모든 bank 에 대해 **원본 이름 집합 == 산출물 이름 집합**을 개별 확인했고
불일치 0건이다 (단순 개수 일치가 아니라 동일 bank 의 동일 PC 가 동일 이름으로 매핑됨).

### 2.2 Yamaha CLP-685

**원본 `data/yamaha-clp685-data.txt` 행 구성 (총 573행)**

```
blank=21, comment=18, header=23, data=511, total=573
```

즉 "573행"은 파일 전체 줄 수이며, 실제 음색 데이터는 511행이다.

**주소 파싱 필드 순서**: `name…, MSB, LSB, PC` (PC 가 마지막).
`make_toml.py` 가 `prog→lsb→msb` 순으로 `pop()` 하여 앞에 insert 하는 것과 일치하며,
`data/yamaha-clp685-data.toml` 의 실제 필드도 `name / msb / lsb / prog` 순으로 확인했다
(예: `GrandPiano` → `msb=0, lsb=0, prog=1`).

> 주의: 최초 검증 시 이 필드 순서를 `prog,lsb,msb` 로 잘못 가정하여 511건 전량 불일치로
> 오보고했다. 파서를 수정한 뒤 재실행하여 아래 결과를 얻었다. **산출물의 결함이 아니라
> 검증 하네스의 결함이었다.**

| 지표 | 원본 | 산출물 | 판정 |
|---|---|---|---|
| 총 음색 수 | 511 | 511 | 일치 |
| 카테고리 수 | 2 (`Preset Voices`, `XG Voices`) | 2 | 일치 |
| (category, bank) 쌍 수 | 53 | 53 (`.Patch Names` 섹션) | 일치 |
| 전역 고유 bank id 수 | 53 | 53 | 카테고리 간 중복 없음 |
| `Patch[bank]=이름` 정의 수 | — | 53 | 일치 |
| (category, bank, PC, name) 4중항 | 511 | 511 | **누락 0 / 추가 0** |
| 카테고리별 bank id 집합 | Preset 9 / XG 44 | Preset 9 / XG 44 | 둘 다 OK |
| bank 섹션 내 PC 중복 (원본) | 0 | — | 중복 없음 |
| bank 섹션 내 PC 중복 (산출물) | — | 0 | 중복 없음 |

카테고리별 bank 분포: `Preset Voices` 9개 은행(13824–13924 대역), `XG Voices` 44개 은행
(0–8192 대역).

---

## 3. bank 이름 체계 정합성 — PASS

### 3.1 섹션 이름 고유성

Cakewalk 는 `.Patch Names` 의 섹션 이름이 전역 고유해야 한다.

| 파일 | 섹션 수 | 고유 섹션 수 | 중복 |
|---|---|---|---|
| `Roland HP603.ins` | 40 | 40 | **0** |
| `Yamaha CLP-685.ins` | 53 | 53 | **0** |

`grep '^\[' <file> | sort | uniq -d` 결과 양쪽 모두 빈 출력. 검증 하네스의 파서에도
섹션 중복 시 즉시 assertion 이 걸리도록 넣었으며 발동하지 않았다.

### 3.2 `Patch[N]` 의 N 과 섹션 bank 번호 일치

| 파일 | `Patch[N]` 개수 | 고유 N | N != 실제 bank id | 참조 섹션 미존재 | 빈 섹션 |
|---|---|---|---|---|---|
| `Roland HP603.ins` | 40 | 40 | **0** | **0** | 0 |
| `Yamaha CLP-685.ins` | 53 | 53 | **0** | **0** | 0 |

Yamaha 의 `Patch[N]` 값은 `Category/Bank#N` 형태이므로 `N == Bank#N` 을 정규식으로
전수 검사했고 불일치 0건이다. Roland 의 `Patch[N]` 값은 `.Patch Names` 섹션 이름과
문자열 동일하며, 모든 값이 실존하는 섹션을 가리킨다.

두 산출물 모두 `Patch[N]` 의 N 은 `msb*128+lsb` 로 계산된 bank select 번호이고, 값은
그 bank 에 대응하는 패치 이름 목록의 이름이다. Cakewalk `.ins` 규격상 올바른 의미다.

### 3.3 정의 수 == 섹션 수

| 파일 | `.Instrument Definitions` 의 `Patch[` 줄 수 | `.Patch Names` 섹션 수 | 판정 |
|---|---|---|---|
| `Roland HP603.ins` | 40 | 40 | **일치** |
| `Yamaha CLP-685.ins` | 53 | 53 | **일치** |

### 3.4 관찰 사항 (결함 아님, 향후 참고)

Yamaha 는 카테고리마다 `[Yamaha CLP-685 - <Category>]` 정의 블록이 분리되어 있고, 현재
카테고리 간 bank id 가 겹치지 않아 `Patch[]` 키가 전역 고유하다. 향후 카테고리를 추가할
때 bank id 가 겹치면 각 블록 안에서 키가 반복되므로, Cakewalk 의 블록 스코프 규칙을
재확인할 필요가 있다. 현재 산출물에는 해당 없음.

---

## 4. 회귀 검증 (assert 발동 확인) — PASS

저장소 소스를 직접 수정하지 않기 위해 프로젝트를 `/tmp/regress` 로 복사한 뒤 그 안에서만
변형했다. 복사본은 먼저 무변형 실행하여 `/tmp/r1.ins` 와 바이트 동일함을 확인했다
(베이스라인 정합성 확보).

### 4.1 중복 bank id → `duplicate bank id` assert

`_BANK_NAME_PAIRS` 의 `(68, 'Piano A'),` 바로 뒤에 `(68, 'Piano A DUP'),` 를 주입.

```
$ python3 /tmp/regress/gen_dup.py
exit_code=1
AssertionError: duplicate bank id in _BANK_NAME_PAIRS
stdout bytes = 0
```

**발동 확인.** exit 1, stdout 0 바이트 → 불완전한 `.ins` 가 부분 출력되지 않고 즉시
중단된다. 트레이스백은 `assert len(BANK_NAMES)==len(_BANK_NAME_PAIRS)` 줄을 정확히 지목.

### 4.2 미등록 bank → `unnamed banks` assert

`(15497, 'Effect E'),` 등록을 제거 (해당 bank id 는 실제 데이터에 존재).

```
$ python3 /tmp/regress/gen_unnamed.py
exit_code=1
AssertionError: unnamed banks: [15497]
stdout bytes = 0
```

추가로 `(15496, 'Effect D'),` 도 제거하여 2건 미등록 상태를 만들자
`AssertionError: unnamed banks: [15496, 15497]` 로 **미등록 bank 전체를 정렬된 리스트로
보고**함을 확인했다.

**발동 확인.** 두 케이스 모두 exit 1 / stdout 0 바이트.

### 4.3 원복

변형은 `/tmp/regress` 복사본에서만 수행했다. 검증 후 저장소의 두 생성기 md5 를 재확인한
결과 검증 전과 동일하다 (§6). 원복 조치 불필요.

---

## 5. 정리 산출물 무손실 검증 — PASS

### 5.1 제거된 코드의 실체 (`generate_cakewalk_yamaha_ins.py`, HEAD → 작업본)

`git diff HEAD -- generate_cakewalk_yamaha_ins.py` = **7 insertions / 64 deletions**.

| 제거 대상 | 위치 (HEAD) | 실체 |
|---|---|---|
| bank 이름 dict | `get_bank_name()` 내부 | **리터럴 43항목 / 고유 키 40개**. 중복 키 3건: `320`, `15492`, `15494` |
| `get_bank_name(banks, bankid)` | 6행 | 호출 지점 **0건** |
| 최상위 `get_banks(inst_name, data)` | 60행 | 호출 지점 **0건**. 게다가 본문이 미정의 이름 `inst_info` 를 참조 → 호출 시 `NameError` 확정 |

"40건"은 고유 키 기준으로 정확하다. 리터럴은 43줄이지만 dict 특성상 뒤 값이 앞 값을
덮어써 40개만 살아남았다.

### 5.2 죽은 코드였음의 증명

- `get_bank_name` — HEAD 파일 전체에서 등장 위치는 **정의부 1곳뿐**, 호출 0건.
- 최상위 `get_banks` — HEAD 파일에서 `get_banks` 문자열은 4곳에 등장하나, 3곳
  (115·151·161행)은 전부 `InstrumentCategory.get_banks` **메서드**이며, 60행의 최상위
  함수는 호출되지 않는다. 메서드 버전은 작업본에도 그대로 존치되어 94·104행에서 2회
  호출된다.
- 제거된 dict 의 bank id 40개는 전부 **Roland 좌표계** 값이다. Yamaha 좌표계
  (`msb*128+lsb`, 0–13924)와는 의미가 다르므로 애초에 적용 대상이 아니었다.

### 5.3 제거 후 산출물 불변 확인

HEAD 버전 생성기를 현재 TOML 입력으로 실행 (`rc=0`) 후 작업본 산출물과 비교:

```
diff <(HEAD 출력) <(현재 출력)  →  총 216줄 (106 <줄 + 106 >줄 + 헤더 4줄)
```

216줄 전량이 다음 두 원인으로만 설명된다.

1. **헤더 주석 4줄** — `Roland HP603 / Mike Choi, Oct 2019` → `Yamaha CLP-685 / Mike Choi`.
   Yamaha 로 복사된 뒤 방치된 잘못된 헤더의 정정.
2. **`Bank/` → `Bank#` 개명 212줄** — HEAD 출력에 `Bank/` 106건, 현재 출력에 `Bank#` 106건.
   `[Category/Bank/13824]` 는 구분자 `/` 와 충돌하므로 `Bank#` 로 바꾼 의도적 변경.
   106건 × diff 2줄 = 212줄.

**죽은 코드 제거로 인한 출력 변화는 0줄이다.** 즉 제거 대상은 실제로 죽은 코드였음이
산출물 수준에서 입증되었다.

### 5.4 부수 발견 — Roland 산출물의 실제 데이터 버그 1건이 수정됨

편입 과정에서 `_BANK_NAME_PAIRS` + assert 구조로 바뀌면서, **구 버전의 shadowing 버그가
Roland 산출물에서 교정**되었다. 커밋된 구 `Roland HP603.ins` 와 신규 산출물의
`Patch[]` 줄을 비교:

```
< Patch[15492]=Effect A        > Patch[15492]=GM E
< Patch[15493]=Effect B        > Patch[15493]=Effect A
< Patch[15494]=Effect D        > Patch[15494]=Effect B
< Patch[15495]=Effect E        > Patch[15495]=Effect C
< Patch[15496]=Effect F        > Patch[15496]=Effect D
< Patch[15497]=Effect G        > Patch[15497]=Effect E
```

구 `generate_cakewalk_ins.py` 의 `names={…}` 에도 동일한 중복 키(43항목/40고유,
`320`·`15492`·`15494`)가 있었고, 그 결과 원래 이름이던 `15492='GM E'` 와
`15494='Effect C'` 가 소실된 채 뒤쪽이 한 칸씩 밀려 있었다. 신규 구조는 이를 복원하고
나머지를 재번호했다. **은행 수는 40 → 40 으로 불변이며, 은행이 사라지거나 늘어난 것이
아니라 이름 6건이 정정된 것이다.** 신규 소스의 주석이 지목한 바로 그 손실이다.

---

## 6. 무결성 확인

```
$ md5sum -c /tmp/gen_hash_before.txt
generate_cakewalk_ins.py: OK
generate_cakewalk_yamaha_ins.py: OK
```

| 파일 | 검증 전 md5 | 검증 후 md5 |
|---|---|---|
| `generate_cakewalk_ins.py` | `140daebe7b95aa816fd0841d4ff1eea8` | 동일 |
| `generate_cakewalk_yamaha_ins.py` | `26ca26c50dbc2843e2071289bef1d1ba` | 동일 |

소스 코드 무수정. 생성 산출물(`/tmp/r*.ins`, `/tmp/y*.ins`)은 저장소 외부에만 존재하며
커밋하지 않았다. `Roland HP603.ins` / `Yamaha CLP-685.ins` 의 mtime 도 검증 중 변하지
않았다 (읽기만 수행).

---

## 7. ATD 편입 리스크 (검증 항목 외, 참고)

검증 항목은 아니지만 편입 완결성에 영향을 주는 사실을 기록한다.

`git status` 기준으로 생성기 입력이 아직 추적되지 않은 상태다.

- `hp603 instruments.txt` (Roland 생성기 입력) — **untracked**
- `data/yamaha-clp685-data.toml` (Yamaha 생성기 입력) — **untracked**
  (`.gitignore` 주석은 "생성기와 find_instruments.py 가 읽는 입력이므로 커밋한다"고
  명시하고 있어 의도와 실제 상태가 어긋난다)
- 커밋된 원본은 `data/yamaha-clp685-data.txt` 뿐이다.

실증: HEAD 버전 Yamaha 생성기를 **깨끗한 체크아웃에서** 실행하면
`FileNotFoundError: data/yamaha-clp685-data.toml` 로 즉시 실패한다.

즉 현재 재현성은 작업 트리 상태에 의존한다. 편입 커밋 시 위 두 입력 파일을 반드시
포함해야 §1 의 재현성이 저장소 이력 수준에서도 성립한다.

---

## 8. 항목별 판정 요약

| # | 검증 항목 | 결과 | 근거 |
|---|---|---|---|
| 1 | 파이프라인 재현성 | **PASS** | 바이트 일치 4/4, 멱등 2/2, 단독 LF 0건 |
| 2 | 전수 주소 대조 | **PASS** | Roland 318/318 누락·추가 0, Yamaha 511/511 누락·추가 0 |
| 3 | bank 이름 체계 정합성 | **PASS** | 섹션 고유 40/40·53/53, `Patch[N]` 불일치 0, 정의수==섹션수 |
| 4 | 회귀 검증 | **PASS** | 중복 bank assert 발동, unnamed bank assert 발동, 소스 원복 |
| 5 | 정리 산출물 무손실 | **PASS** | 죽은 코드 3종 호출 0건, 제거로 인한 출력 변화 0줄 |

주소 매핑 오류, 누락, 중복, 추가는 **전 항목 0건**이다.

# 최종 판정: PASS
