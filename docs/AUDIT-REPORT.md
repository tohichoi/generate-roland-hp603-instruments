# ATD 편입 감사 보고서 — generate-roland-hp603-instruments

- 감사관: Elena (S.P.I.R.E. 수석 품질·보안 감사관)
- 감사일: 2026-09-21
- 대상: `/home/x/Workspace/generate-roland-hp603-instruments`
- 감사 기준선: 작업 트리 (HEAD = `528e261` = `origin/main`)
- 편입 프레임: `Adopted Project` (선례: `sheet-music-extractor/docs/PROJECT-PROMOTION.md` §4)
- **최종 판정: NEEDS_IMPROVEMENT — 적발 20건 (HIGH 5 / MEDIUM 6 / LOW 9)**

감사 원칙: 본 프로젝트의 값어치는 코드 품질이 아니라 **MIDI 프로토콜의 정밀한 분석**에 있으므로,
프로토콜 서술의 사실 여부를 최우선으로 검증했다. 코드 스타일 지적은 백로그로만 남긴다.

---

## 0. 감사 방법 및 재현 명령

원본 데이터와 산출물을 **직접 집계**해 문서의 모든 수치를 대조했다. 문서를 근거로 문서를 검증하지 않았다.

```bash
# Roland 전수 집계 (318행 / 40 bank / MSB·LSB 집합 / bank별 PC)
python3 -c "..." "hp603 instruments.txt"
# Yamaha 전수 집계 (511행 / 53 bank)
python3 -c "..." data/yamaha-clp685-data.txt
# 산출물 재생성 대조
python3 generate_cakewalk_ins.py > /tmp/r.ins                    # exit 0, 바이트 동일
/tmp/hp603venv/bin/python generate_cakewalk_yamaha_ins.py > /tmp/y.ins   # exit 0, 바이트 동일
/tmp/hp603venv/bin/python make_toml.py                           # exit 0, TOML 동일
```

집계 스크립트는 저장소 외부(`/tmp`)에서만 실행했고, 본문 파일은 수정하지 않았다.
아래 모든 `파일:행` 근거는 **작업 트리 기준**이며, HEAD 기준이 필요한 항목은 명시했다.

---

## 1. 최우선 감사: 프로토콜 서술 사실 검증

### 1-1. 검증 결과 요약표

| # | 문서 주장 (PROJECT-PROMOTION.md) | 실측 | 판정 |
| :--- | :--- | :--- | :--- |
| P-1 | Roland 318음색 / 40 bank (`:80`) | 318음색행 / 고유 bank 40 | **일치** |
| P-2 | 네이티브 MSB `0·1·2·4·8·16·24·32·47` (`:81`) | 정확히 이 9개, 예외 없음 | **일치** |
| P-3 | 네이티브 LSB `64~71` (`:81`), "예외 없이 LSB 64~71" (`:108`) | LSB 0 예외 **3건** | **불일치** |
| P-4 | 네이티브 규모 53음색 / **32 bank** (`:82`) | 53음색 / **29 bank** | **bank 수 불일치** |
| P-5 | GM2 = MSB 121 / LSB 0~9 = 256음색 (`:103`) | 121+LSB0~9 = 256행 | **일치** |
| P-6 | Drums = MSB 120 = 9건 (`:102`) | 120+LSB0 = 9행 | **일치** |
| P-7 | Yamaha 511음색 / 53 bank (`:80`) | 511행 / 고유 bank 53 | **일치** |
| P-8 | Preset = MSB 108 / LSB `0~7, 100` = 31건 9 bank (`:81`, `:122`) | 일치 | **일치** |
| P-9 | XG = MSB 0 = 438건, LSB 43종 (`:83`, `:125`) | 438행 / LSB 43종 / bank 43 | **일치** |
| P-10 | SFX = MSB 64 = 42건 (`:84`, `:126`) | 42행 / bank 1 | **일치** |
| P-11 | Preset PC가 GM 프로그램 번호 체계 (`:146`) | 계열 수준 일치, prog 3 슬롯만 부정확 | **부분 일치** |
| P-12 | README `CFX Grand 108 0 1` → bank 13824 (`README:80-82`) | 128×108+0 = 13824 | **일치** |
| P-13 | GM2 On 시스엑스 `F0 7E 7F 09 03 F7` 구성 설명 (`:65-68`) | GM2 System On 규격과 일치 | **일치** |
| P-14 | "두 벤더 주소 체계는 호환되지 않는다" (`:150-163`) | 데이터로 뒷받침·**오히려 강화** | **일치** |
| P-15 | `PROMOTION-SPEC.toml` metrics | 3/4 일치, "891행" 근거 불일치 | **부분 일치** |

### 1-2. 개별 검증 상세

**[검증 통과] P-1 Roland 318음색 / 40 bank — 정확.**
`hp603 instruments.txt` = 326행 = 그룹 헤더 8행(`Piano, E.Piano, Organ, Strings, Upright,
Classical, Drums, GM2`) + 음색행 318행. 고유 `(MSB,LSB)` 쌍 = 40, 고유 `(MSB,LSB,PC)` 3중항 = 318
(중복 0). 8+318=326 이므로 문서의 "318행"은 음색 데이터 행 수로 정확하다.

**[검증 통과] P-2 Roland 네이티브 MSB 집합 — 예외 없음.**
MSB 120·121을 제외한 전체 MSB는 정확히 `{0,1,2,4,8,16,24,32,47}` 9종이다. 문서 `:81`의 집합과
완전히 일치하며 누락·추가 0건이다.

**[적발 #1 / HIGH] P-3 "네이티브 음색은 예외 없이 LSB 64~71" — 반증됨.**
문서 `:108`은 "Roland의 네이티브 음색은 예외 없이 LSB 64~71에 있습니다"라고 단정하지만,
실측 예외가 3건 있다.

| 파일:행 | 음색 | MSB | LSB | PC |
| :--- | :--- | :--- | :--- | :--- |
| `hp603 instruments.txt:38` | Violin | 0 | **0** | 40 |
| `hp603 instruments.txt:41` | Cello | 0 | **0** | 42 |
| `hp603 instruments.txt:43` | Pizzicato Str | 0 | **0** | 45 |

더욱이 이는 **문서 내부 모순**이다. 같은 문서 `:92`의 상세 열거는 MSB 0의 네이티브 bank을
`LSB=[0, 64, 65, ..., 71]`로 **LSB 0을 포함해** 9개로 세고, `:101`의 "--- 이상 네이티브 ---"
구분선은 그 아래에 온다. 즉 열거표는 이 3건을 네이티브로 계상하면서 산문은 예외가 없다고
단정한다. (`:108`의 후속 문장 "LSB 0~63은 표준 확장(GM2)에 내준 것"도 부정확하다. GM2는
`MSB=121, LSB=0~9`이고, 여기서 문제된 `MSB=0, LSB=0`은 GM Level 1 bank이다.)

**[적발 #2 / HIGH] P-4 "네이티브 규모 53음색 / 32 bank" — bank 수 오류.**
`:82`의 표는 32 bank이라 하지만 실측은 **29 bank**이다. 문서 `:92-100`의 상세 열거를 그대로
합산하면 `9+3+3+1+6+3+1+2+1 = 29`로, **동일 문서의 표와 열거가 서로 어긋난다.**
교차 확인: 전체 40 bank − MSB 120(1) − MSB 121(10) = 29. 음색 53건은 정확하다
(`25+7+3+1+7+6+1+2+1 = 53`).

**[검증 통과] P-5·P-6 · P-7~P-10 — 정확.**
GM2 bank 10개(MSB 121, LSB 0~9)에 256행, Drums 1개(MSB 120, LSB 0)에 9행.
Yamaha는 511행 / 고유 bank 53, Preset 9 bank(LSB `0~7,100`) 31행, MSB 0 = 438행 / LSB 43종,
MSB 64 = 42행. 문서 `:80-84`의 모든 수치와 일치한다.
`:148`이 예시로 든 `CuttingNoise, StringSlap, FluteKeyClick, Shower, Thunder` 5건 모두
`data/yamaha-clp685-data.txt:532-537`에 실재한다.

**[적발 #3 / LOW] P-11 Preset PC의 GM 체계 — 계열 수준은 맞고 3번 슬롯 서술이 부정확.**
`data/yamaha-clp685-data.txt`의 MSB 108 블록에서 확인한 실제 배치는 GM 프로그램 계열과
잘 맞는다: prog 1·2 그랜드(`CFX Grand`, `Bright Grand`), prog 4 `HonkyTonk Pf`(GM 4 = Honky-tonk),
prog 5·6 EP(GM 5·6 = Electric Piano 1·2), prog 17 `Jazz Organ 1`(GM 17 = Drawbar Organ),
prog 20 오르간(GM 17~24 오르간 계열), prog 49·50 `Strings`/`Slow Strings`(GM 49·50 = String
Ensemble 1·2), prog 53 `Choir`(GM 53 = Choir Aahs). 문서 `:146`의 "GM 표준의 프로그램 번호
배치와 일치합니다"는 이 범위에서 **성립**한다.
다만 "prog 1~3은 그랜드 피아노"는 부정확하다. GM의 prog 3은 **Electric Grand Piano**이며,
Yamaha 데이터의 prog 3은 `Rock Grand`(음향 그랜드)이다. 슬롯 3 한 건에서 GM과 어긋난다.

**[검증 통과 / 결론 강화] P-14 "두 주소 체계는 호환되지 않는다" — 데이터로 뒷받침되며, 문서가
주장한 것보다 더 강하게 성립한다.**

| 대조 | 값 |
| :--- | :--- |
| bank id 교집합 | **9건** (`0, 64, 65, 66, 67, 68, 69, 70, 71`) |
| 고유 `(bank, PC)` 교집합 | **5건** — `(0,40) (0,42) (0,45) (64,89) (66,19)` |
| 그 5건의 실제 음색 | 아래 표 |

| bank, PC | Roland HP603 | Yamaha CLP-685 |
| :--- | :--- | :--- |
| 0, 40 | Violin | SynthBass2 |
| 0, 42 | Cello | Viola |
| 0, 45 | Pizzicato Str | TremoloStrings |
| 64, 89 | Soft Pad | Fantasy |
| 66, 19 | ChurchOrgan1 | FastRotary |

bank 번호 9건이 숫자로 겹치고, 그중 5건은 **PC까지 같아도 서로 다른 악기**를 낸다. 예컨대
bank 0은 Roland에서 `Orchestra C`(Violin/Cello/Pizzicato Str)이고 Yamaha에서 `XG Voices/Bank#0`
(`GrandPiano`, `BrightPiano`, …)이다. 문서 `:161`의 "bank 번호를 넘겨줄 공통 표기가 존재하지
않습니다"는 실측으로 확정된다. **이 프로젝트의 핵심 논지는 타당하다.**

**[검증 통과] P-13 GM2 On 시스엑스 — 설명 정확.**
`F0`(SysEx 시작) `7E`(Universal Non-Real Time) `7F`(대상 기기 전체) `09`(GM System On)
`03`(GM2) `F7`(종료) 구성은 GM2 System On 규격과 일치한다. `generate_cakewalk_ins.py` 계열이
아닌 `find_roland_gm_inst.py:24`와 `test_program_change.py:31` 양쪽에 동일 바이트가 있다.

**[적발 #4 / LOW] P-15 `PROMOTION-SPEC.toml` metrics — 3/4 일치, 1건 근거 불일치.**

| metrics | SPEC 값 | 실측 | 판정 |
| :--- | :--- | :--- | :--- |
| 지원 기종 (`:63`) | Roland 318/40 · Yamaha 511/53 | 동일 | 일치 |
| 역분석 규모 (`:67`) | 829 주소 | 318+511 = 829 | 일치 |
| 벤더 대조 (`:73`) | Roland MSB 120·121 / Yamaha MSB 0·64·108 | 동일 | 일치 |
| 코드 규모 (`:77`) | 498행 (정리 후) | 실측 498행 | 일치 |
| 역분석 규모 subtext (`:68`) | "제조사 PDF 데이터 리스트 **891행** 수작업 전사" | 829(문서 `:187`)와 불일치 | **근거 불일치** |

`891 = 318(음색행) + 573(파일 전문)`으로, 서로 다른 단위를 더한 값이다. 같은 문서 `:187`은
"Roland 318행, Yamaha 511행"으로 829를 말한다. 891의 출처는 확인 불가다.
주목할 점은 **SPEC이 MD보다 정확하다**는 것이다. SPEC `:77`은 498행으로 실측과 맞고,
MD는 555행이라고 쓴다(적발 #5).

---

## 2. 서술과 구현의 불일치 (파일:행 근거)

**[적발 #5 / HIGH] 코드 규모 555행 — 실측 498행.**

| 파일 | 문서 주장 (`:268`) | 실측 (`wc -l`) | 판정 |
| :--- | ---: | ---: | :--- |
| `generate_cakewalk_ins.py` | 114 | 114 | 일치 |
| `generate_cakewalk_yamaha_ins.py` | **164** | **107** | **불일치 (−57)** |
| `find_instruments.py` | 76 | 76 | 일치 |
| `find_roland_gm_inst.py` | 89 | 89 | 일치 |
| `test_program_change.py` | 63 | 63 | 일치 |
| `make_toml.py` | 49 | 49 | 일치 |
| **계** | **555** | **498** | **불일치 (−57)** |

불일치는 Yamaha 생성기 한 곳에서만 발생한다. `164`는 **HEAD 시점 값**이다
(`git show HEAD:generate_cakewalk_yamaha_ins.py | wc -l` = 164). 편입 정리에서 죽은 코드
(미호출 `get_bank_name` + 리터럴 43항목, 미호출 최상위 `get_banks`)가 제거되어 107행이
되었는데, 문서의 행수표는 Roland 쪽은 **정리 후 값**(114)을, Yamaha 쪽은 **정리 전 값**(164)을
쓰고 있다. 그 결과 `:20`, `:273`, `:337`의 "555행"이 모두 실측과 어긋난다.
동일 저장소의 `docs/PROMOTION-SPEC.toml:77`은 498행으로 정확하므로 **MD와 SPEC이 서로 모순**이다.

**[적발 #6 / MEDIUM] README의 `.toml` 커밋 주장 — 거짓.**
`README.md:62`는 "`.toml` 은 커밋되어 있으므로, 생성기만 다시 돌릴 때는 `make_toml.py` 를
건너뛰어도 됩니다"라고 안내한다. 그러나 `data/yamaha-clp685-data.toml`은 **untracked**다
(`git status --short` → `?? data/yamaha-clp685-data.toml`, `git check-ignore` = 미해당).
`.gitignore:2`의 주석 "data/yamaha-clp685-data.toml 은 생성기와 find_instruments.py 가 읽는
입력이므로 커밋한다"는 **의도**이고, 실제 상태는 그 반대다. 새 체크아웃에서는
`generate_cakewalk_yamaha_ins.py`가 `FileNotFoundError`로 즉시 실패한다.
(`docs/VERIFICATION-REPORT.md:313-325`가 동일 리스크를 이미 기록했다.)

**[적발 #7 / MEDIUM] `.gitignore` 부재 주장 — 실측과 반대.**
문서 `:327`은 "`LICENSE`와 `.gitignore`가 없습니다"라고 쓴다. `LICENSE`는 실제로 없다(적발 #18).
그러나 `.gitignore`는 **존재한다**(untracked, 8행). 문서가 저장소 위생 결함으로 지목한 항목 중
하나가 이미 해소된 상태이며, §7-1의 작업 표 어디에도 `.gitignore` 생성이 기재되어 있지 않아
누가 언제 만들었는지 문서상 추적되지 않는다.

**[적발 #8 / HIGH] "배포된 `.ins`는 CRLF" 전제가 반전됨 — 줄바꿈 수정이 저장소 수준에서 무효.**

문서 `:309`는 "배포된 `.ins`는 CRLF(Cakewalk는 Windows 애플리케이션)인데 생성기는 줄바꿈을
지정하지 않아, Linux에서 재생성하면 450행 전체가 diff로 잡혔습니다"라고 쓴다. 실측은 반대다.

| 대상 | CRLF | 단독 LF |
| :--- | ---: | ---: |
| HEAD 커밋 blob `Roland HP603.ins` | **0** | **450** |
| 작업 트리 `Roland HP603.ins` | 450 | 0 |
| `Yamaha CLP-685.ins` (untracked) | 689 | 0 |

즉 **커밋된(배포되는) 산출물은 LF-only**이고, CRLF는 이번 수정으로 새로 생긴 것이다.
게다가 이 저장소는 `core.autocrlf=input`이므로 git이 커밋 시 CRLF를 LF로 되돌린다.
실제로 `git diff`는 경고를 낸다:

```
warning: in the working copy of 'Roland HP603.ins', CRLF will be replaced by LF
the next time Git touches it
```

따라서 `sys.stdout.reconfigure(newline='\r\n')`(`generate_cakewalk_ins.py:7`,
`generate_cakewalk_yamaha_ins.py:8`)는 **작업 트리에서만 유효**하고, 커밋되면 다시 LF가 된다.
Cakewalk(Windows) 사용자가 GitHub에서 받는 파일은 여전히 LF이며, 문서가 "고정했다"고 선언한
문제는 해소되지 않는다. 수정 자체의 의도는 타당하나(Windows 앱 상호운용), 서술의 전제("배포본이
CRLF")가 사실과 다르고 효과도 저장소 이력에 남지 않는다. `.gitattributes`(`*.ins text eol=crlf`)가
없는 것이 근본 원인이다.

**[적발 #9 / LOW] §7-3의 `Bank/` 서술이 현재형이며, 실제 잔존 불일치는 다른 곳이다.**
문서 `:321`은 "README는 bank 이름을 `Bank#13824`로 쓰라고 안내하지만 코드는 `Bank/13824`(슬래시)를
출력합니다"라고 현재형으로 쓴다. **HEAD 시점에는 참**이다 — HEAD의 `Instrument.bank_name`은
`f'Bank/{self.bank_id}'`였다(확인). 그러나 현재 코드는 `f'Bank#{self.bank_id}'`
(`generate_cakewalk_yamaha_ins.py:24`)이고, 저장소 어디에도 `Bank/` 리터럴이 없다.
정작 **남아 있는 불일치는 지목되지 않았다**: README `:145`는 section을 `[Bank#13824]`로
안내하지만(같은 취지로 `:133`, `:137`, `:140`), 실제 생성기는 카테고리 접두사를 붙여
`[Preset Voices/Bank#13824]`를 출력한다(`Yamaha CLP-685.ins:8` 및 `Patch[13824]=Preset
Voices/Bank#13824`). README를 그대로 따라 하면 section 이름이 맞지 않는다.

**[적발 #10 / LOW] §7-2 중복 키 서술이 "3곳"이라면서 결과는 1곳만 기술.**
`:300-307`은 "같은 번호가 두 번 들어간 자리가 3곳"이라 하고 예시로 `15492`만 제시한다.
실측 중복 키는 `320`, `15492`, `15494` 3건으로 **"3곳"은 정확**하다(HEAD 소스 확인).
GM/Effect 결과 서술(`GM A~D`에서 끊김, `15492~15497`이 `Effect A,B,D,E,F,G`)도 HEAD 산출물과
일치한다. 다만 `320`의 중복(`Piano H` → `Forte Piano A` 덮어쓰기)과 그 결과는 서술되지 않았다.
"3곳"이라는 수치와 제시된 예시의 범위가 어긋난다.

**[적발 #11 / LOW] §3-3 "표준에 내준 MSB" 행이 Yamaha의 사적 규격을 표준으로 분류.**
`:156`의 표는 Yamaha의 `0`(XG)과 `64`(SFX)를 "표준에 내준 MSB"로 적는다. XG는 **Yamaha 자사
규격**이고 MSB 64 SFX도 Yamaha 사적 영역이므로, "표준에 내준"이라는 행 제목과 맞지 않는다.
같은 문서 `:129`는 MSB 108에 대해 "GM/GS/XG 어느 표준에도 정의되어 있지 않습니다"라 하면서
XG를 프레임상 표준처럼 병기해 **내부 프레이밍이 엇갈린다.** 논지(호환 불가)에는 영향이 없다.

**[적발 #12 / LOW] 데이터 자산 행수의 단위 혼용.**
`:275`는 "데이터 자산은 Roland 318행 + Yamaha 573행"이라 한다. 318은 음색 데이터 행 수이고
573은 **파일 전체 줄 수**(음색행 511 + 주석 18 + 공백 21 + 헤더 23)로, 단위가 다르다.
`:187`은 같은 대상을 "Roland 318행, Yamaha 511행"이라 적어 문서 내부에서 단위가 바뀐다.
이는 적발 #4(SPEC의 "891행")와 같은 원인의 혼용이다.

---

## 3. 시크릿 / PII / 제3자 저작물

**[검증 통과] 시크릿·PII — 0건.**
`.git`, `reference/`를 제외한 전체 텍스트(소스 6종, `*.md`, `*.toml`, `*.txt`, `*.ins`,
`docs/assets/_thumb_build/thumbnail.html`, `requirements.txt`)를 스캔했다. 비밀번호, PIN,
API 키/토큰(`AKIA`, `ghp_`, `sk-`, `xox*`, `BEGIN ... PRIVATE KEY`), 전화번호 패턴,
개인 이메일 주소는 **검출되지 않았다.** 저장소에 등장하는 인명은 `.ins` 헤더의 저자 본인
`Mike Choi`뿐이며, 저장소 소유자(`github.com/tohichoi`)의 공개 저작자 표기로 PII 노출이 아니다.
평문 민감 정보가 0건이므로 role spec의 무조건 `FAIL` 조건에는 해당하지 않는다.

**[적발 #13 / MEDIUM] `reference/` PDF 8건 구성이 문서 서술과 다르고, Yamaha 측 출처가 없다.**
`:329`는 "PDF 8건은 모두 제3자 저작물(Roland MIDI 구현 문서, **Yamaha 데이터 리스트**,
Cakewalk 언어 가이드)입니다"라고 쓴다. `pdfinfo`로 8건 전수 확인한 실제 구성은 **Roland 7건 +
Cakewalk 1건**이며 **Yamaha 문서는 한 건도 없다.**

| 파일 | 저작자 (pdfinfo) |
| :--- | :--- |
| `Midi_Implementatie_Roland_LX-7.pdf` | Roland Corporation |
| `INFOCUS01_MIDI.pdf` | Roland Corporation US |
| `Roland_gm2_sounds.pdf` | (Roland, InDesign CS4) |
| `Selecting_SRX_Sounds_0707.pdf` | ©2005 (Roland) |
| `Selecting_Ints_and_SR-JV80s.pdf` | ©2004 Roland Corporation U.S. |
| `Selecting_Fantom-G_and_ARX-Series_Sounds_Via_MIDI.pdf` | (Roland, InDesign CS3) |
| `roland_full_tone_list.pdf` | (Roland, InDesign CS4) |
| `Cakewalk Application Language Programming Guide.pdf` | Ton Valkenburgh |

파급 효과가 실질적이다. 문서 `:85`는 Yamaha 데이터 출처를 "CLP-685/695GP Data List (Yamaha)"로
적지만 그 PDF가 저장소에 없으므로, **Yamaha 511행 전사의 1차 자료가 저장소 외부에 있어 검증
불가**하다(`data/yamaha-clp685-data.txt`가 유일한 흔적이다). Roland 측(318행, LX-7 PDF)은
1차 자료가 저장소 안에 있어 대조 가능하다 — 비대칭이다.

재배포 판정: 커밋된 8건은 모두 제3자 저작물이며, 공개 저장소(`github.com/tohichoi/...`)에
원문을 두는 것은 각 저작권자의 재배포 허가 범위 밖일 수 있다. 문서 `:329`가 이미 리스크를
기록했고, 본 감사는 그 판단에 동의한다. 조치 방향은 (a) `reference/`를 이력에서 제거하고
출처 URL만 `README:208-215`에 남기거나, (b) 배포 허가가 확인된 문서만 남기는 것이다.
Yamaha 데이터 리스트는 부재하므로 (a)의 근거가 더 강하다.

---

## 4. 실행 가능성 검증

**[검증 통과] `generate_cakewalk_ins.py` — 재현 및 멱등 확인.**
표준 라이브러리만 사용(`collections`, `sys`). `python3 generate_cakewalk_ins.py > /tmp/r.ins`
실행 결과 exit 0, stderr 0바이트, 기존 `Roland HP603.ins`와 **바이트 동일**.
`_BANK_NAME_PAIRS` 중복 assert와 미등록 bank assert가 있어 조용한 실패가 차단된다.

**[검증 통과] `generate_cakewalk_yamaha_ins.py`·`make_toml.py` — 재현 확인.**
`/tmp/hp603venv/bin/python`로 실행, exit 0, 기존 `Yamaha CLP-685.ins`와 **바이트 동일**.
`make_toml.py`도 exit 0이며 생성된 `.toml`이 기존 파일과 **바이트 동일**하다(결정적 변환).

**[적발 #14 / MEDIUM] `find_instruments.py` — 현재 데이터에서 즉시 실패.**
`find_instruments.py:16-21`은 `data.items()`의 값이 **음색 리스트**라고 가정한다:

```python
for category, instruments in data.items():
    for inst in instruments:        # 실제로는 그룹 이름(str)
        row = {'Category': category}
        row.update(inst)            # str을 dict로 update
```

그러나 실제 TOML 구조는 `{category: {group: [inst, ...]}}` 2단계
(`Preset Voices → Piano → [...]`, `XG Voices → PIANO → [...]`)이다. 재현 결과:

```
ValueError: dictionary update sequence element #0 has length 1; 2 is required
```

즉 `find_instruments.py`는 현재 입력으로 **동작하지 않는다.** `README.md:43`은 이 스크립트의
의존성(`streamlit`, `toml`, `pandas`)만 안내하고 정상 동작을 전제하며, 문서 `:259`·`:269`는
이를 "Streamlit 검색 앱"으로 소개한다. `get_categories()`(`:27-32`)는 호출 지점이 없는 죽은
함수이고, `:44`의 주석 처리된 Roland 옵션과 `:53`의 `selected_categories = [0]*len(df_list)`도
미완성 상태다. (streamlit 미설치 환경이라 UI 전체 구동은 시도하지 않았고, 실패하는 데이터
경로만 직접 재현했다.)

**[적발 #15 / MEDIUM] `find_roland_gm_inst.py` — CC 메시지 구성이 잘못되어 bank을 고를 수 없다.**
문서 `:216`은 "`find_roland_gm_inst.py`는 같은 일을 `mido`로 하며"라고 서술한다(= `test_program_change.py`와
동등). 그러나 `find_roland_gm_inst.py:29-37`은

```python
pcmsg.append(Message('control_change', control=int(val.pop())))   # control = PC
pcmsg.append(Message('control_change', control=int(val.pop())))   # control = LSB
pcmsg.append(Message('program_change', program=int(val.pop())))   # program = MSB
```

로, 입력 `[MSB, LSB, PC]`를 pop해 **CC#PC=0, CC#LSB=0, PC=MSB**를 보낸다. 컨트롤러 번호
`0`과 `32`가 상수로 들어가지 않는다. 실제 mido로 재현한 결과:

```
입력 '0 68 0' (CC#0=0, CC#32=68, PC=0) →
    control_change control=0  value=0     # 우연히 일치
    control_change control=68 value=0     # 오류: control=32 value=68 이어야 함
    program_change program=0              # 우연히 일치
```

MSB·PC가 0일 때만 우연히 맞는다. `test_program_change.py:6-11`의 예시 `EP BELLE 8 68 5`를
넣으면 `CC#5=0, CC#68=0, PC=8`이 되어 전혀 다른 음색이 선택된다.
즉 문서가 서술한 "실기 응답 확인" 경로 중 mido 쪽 도구는 **기능하지 않는다.**
(`test_program_change.py:42-47`의 바이트 구성은 정확하며, 문서 `:206-211`의 스니펫과 일치한다.)
프로토콜 분석 자체는 PDF 전사에서 나온 것이므로 이 결함이 분석 결과를 무효화하지는 않는다.
다만 §4-2의 동등성 서술은 사실이 아니다.

**[백로그 / LOW] 코드 스타일 (판정에 미반영).**
`test_program_change.py:25`의 `midiout.open_port(1)`은 포트 인덱스 하드코딩이라 포트가 1개뿐인
환경에서 `IndexError`가 난다. `:49`의 주석 "middle C"가 실제 note 67(G)과 불일치.
`find_roland_gm_inst.py:31`의 `idx=0`은 미사용. 함수/파일 길이는 role spec 한도(함수 50줄,
파일 300줄) 이내이며 ruff 위반 요소는 발견되지 않았다.

---

## 5. 미추적 잔재 파일 4건 판정

4건 모두 `git status`에서 `??`(untracked)이며, README·`PROJECT-PROMOTION.md`·`PROMOTION-SPEC.toml`
어디에도 언급이 없다. 확보한 근거에 따른 정체 판정은 다음과 같다.

| # | 파일 | 크기 | 정체 판정 |
| :--- | :--- | ---: | :--- |
| 1 | `Roland HP603 - friendly names.ins` | 1224행 | **폐기된 탐색 산출물.** `.Patch Names` section 299개 / `Patch[]` 298개인데 음색 엔트리는 318건 — 즉 음색당 bank이 1개꼴로 흩어져 있다. `Patch[2502]`(MSB 19), `Patch[6211]`(MSB 48), `Patch[8771]`(MSB 68), `Patch[11456]`(MSB 89) 등 **최종 데이터에 없는 MSB**를 포함한다. HP603 부분집합이 아니라 더 넓은 Roland tone list에서 만든 초기 시도로 보이며, 최종 `Roland HP603.ins`(40 bank)로 대체되었다. `Bank#NNNN` 자리표시자가 다수라 bank 이름 부여 이전 단계다. |
| 2 | `Roland HP603.ins.txt` | 450행 | **최종 산출물의 이전 드래프트.** 최종본과 section 이름만 다르고 내용·행수·음색 엔트리(318)가 같다. 차이는 이름 부여 이전의 `[Bank#68]` 형태가 `[Piano A]`로 바뀐 것뿐이다. |
| 3 | `Roland HP603.ins (1).txt` | 450행 | **#2와 바이트 동일**(`cmp` 일치). 브라우저 재다운로드로 생긴 사본(`(1)` 접미사)이다. |
| 4 | `cakewalk community posting.txt` | 95행 | **공개 포럼 게시글 원고.** `README.md`의 `Motivation`(7-15행)·`Installation` 일부·`How to`·`Simplifying Cakewalk .ins file structure`·`Caveats`·`References` 절이 이 파일에서 그대로 옮겨졌다. 즉 README의 모태 문서다. |

**[적발 #16 / LOW] 잔재 4건 처리 미결.**
#2·#3은 `Roland HP603.ins`와 중복이고 #1은 대체된 탐색물이므로 삭제 후보이며, #4는 README의
출처로 이력 보존 가치가 있다. 네 건 모두 `.gitignore` 대상이 아니어서 향후 커밋에 딸려 들어갈
위험이 있다. 문서 §7-4가 이들을 언급하지 않아 편입 산출물 목록이 불완전하다.

---

## 6. 저장소 위생

**[적발 #17 / HIGH] 편입 산출물 전체가 미커밋 — 새 체크아웃에서 재현 불가.**
`HEAD` = `origin/main` = `528e261`이며, 이번 ATD 편입의 결과물은 **전부 작업 트리에만** 있다.

```
 M README.md
 M "Roland HP603.ins"
 M generate_cakewalk_ins.py
 M generate_cakewalk_yamaha_ins.py
?? .gitignore
?? "Yamaha CLP-685.ins"
?? data/yamaha-clp685-data.toml
?? docs/                 (PROJECT-PROMOTION.md, PROMOTION-SPEC.toml, VERIFICATION-REPORT.md, assets/)
?? "hp603 instruments.txt"
```

`HEAD`의 tracked 파일 목록에는 `hp603 instruments.txt`와 `data/yamaha-clp685-data.toml`이
**없다**(`git ls-tree -r HEAD --name-only` 확인). 결과적으로 HEAD 기준으로는

- `generate_cakewalk_ins.py` → `FileNotFoundError: hp603 instruments.txt` (직접 실행 확인)
- `generate_cakewalk_yamaha_ins.py` → `FileNotFoundError: data/yamaha-clp685-data.toml`

로 **두 생성기가 모두 실행되지 않는다.** 이는 문서 `:317`이 "실행 불가 상태"로 지목하고
`§7-1`에서 Kai가 해소했다고 기록한 결함이 정확히 그대로 재현되는 상태다. 해소는 작업 트리
안에서만 이루어졌고 저장소 이력에는 반영되지 않았다.
(같은 사실을 `docs/VERIFICATION-REPORT.md:313-325`가 리스크로 기록하고 있다.)

**[적발 #18 / MEDIUM] `LICENSE` 부재 — 문서 서술은 정확, 상태는 미해소.**
저장소 루트에 `LICENSE`가 없다(확인). `README.md`는 "Feel free to change whatever you need"
(`:191`)라 적을 뿐 재사용 조건을 규정하지 않는다. 공개 저장소이므로 라이선스 부재는 재사용
조건 불명확이라는 문서 `:327`의 지적이 타당하다. 미해소 결함으로 남긴다.

**[검증 통과] `requirements.txt` — 문서 `:327`의 서술이 모두 정확.**
UTF-16 little-endian **BOM 있음**(`ff fe 74 00 6f 00 ...` 확인), CRLF. pip가 처리하나 UTF-8
가정 도구는 읽지 못한다. 내용은 큐레이션 목록이 아니라 환경 덤프(버전 고정 41건 + 무버전
`tomli`, `rich` = **43개**)이며, `test_program_change.py`가 쓰는 `python-rtmidi`는 **누락**
이다. 세 가지 서술 모두 실측과 일치한다.
다만 `README.md:36-47`의 스크립트별 의존성 표는 `python-rtmidi`를 명시하므로 README 자체는
정확하고, 문제는 `requirements.txt` 파일 쪽이다.

**[적발 #19 / LOW] `.gitignore`가 추적되지 않는다.**
적발 #7과 같은 사실의 다른 면이다. `.gitignore:2-3`은 `data/*.json`을 무시하고
`.toml`은 커밋하라고 명시하지만, `.gitignore` 자체가 untracked이므로 이 규칙은 저장소에
적용되지 않는다(실제로 `data/yamaha-clp685-data.json`은 로컬에서만 무시된다).
문서 `:327`은 이것이 **없다**고 서술해 상황을 반대로 기술한다.

**[적발 #20 / LOW] §6-1 개발 시기 서술 중 저장소로 확인되지 않는 부분.**
`:258`은 Roland 단계를 "2019.10.24 ~ 10.25", Yamaha 확장을 "2025.10 ~ 12"로 적는다.
저장소에서 확인되는 커밋 날짜는 `2022-08-29`×2, `2025-12-23`×2, `2025-12-26`이며
**2019년 커밋은 없다.** 2019년의 유일한 근거는 `.ins` 헤더의 "Mike Choi, Oct 2019"다.
"10.24 ~ 10.25"의 정밀 날짜와 "2025.10" 시작 시점은 저장소에서 **확인 불가**다.
참고로 `§7-1`의 "로컬이 3커밋 뒤처져 있었다"는 서술은 정합적이다 — 2022년 스냅샷
(`5464666`)에서 `528e261`까지 정확히 3커밋이다.

---

## 7. 판정 및 적발 건수

### 7-1. 항목별 판정

| 감사 영역 | 판정 | 근거 |
| :--- | :--- | :--- |
| 프로토콜 서술 사실 검증 | **NEEDS_IMPROVEMENT** | 15개 주장 중 10 일치 / 3 불일치(#1·#2·#4) / 1 부분(#3) / 1 결론 강화(P-14). 핵심 논지는 확정, 파생 수치에 오류 |
| 서술-구현 불일치 | **NEEDS_IMPROVEMENT** | #5~#12 (HIGH 2 / MEDIUM 2 / LOW 4) |
| 시크릿·PII | **PASS** | 0건. 무조건 FAIL 조건 미해당 |
| 제3자 저작물 재배포 | **NEEDS_IMPROVEMENT** | #13. 서술 불일치 + Yamaha 1차 자료 부재 |
| 실행 가능성 | **NEEDS_IMPROVEMENT** | 생성기 3종 재현 PASS, `find_instruments.py`(#14)·`find_roland_gm_inst.py`(#15) 기능 불능 |
| 미추적 잔재 4건 | **NEEDS_IMPROVEMENT** | #16. 4건 정체 판정 완료, 처리 미결 |
| 저장소 위생 | **NEEDS_IMPROVEMENT** | #17~#20. `requirements.txt` 서술만 정확 |
| 데이터 정합성 (참고) | **PASS** | `docs/VERIFICATION-REPORT.md`의 전수 대조를 독립 재현 — Roland 318/318, Yamaha 511/511 누락·중복·추가 0. 생성기 출력 바이트 동일 재현 |

### 7-2. 적발 건수

| 등급 | 건수 | 번호 |
| :--- | ---: | :--- |
| **HIGH** | 5 | #1 (LSB 예외), #2 (네이티브 32 bank), #5 (코드 555행), #8 (줄바꿈 전제 반전), #17 (편입 미커밋) |
| **MEDIUM** | 6 | #6 (`.toml` 커밋 주장), #7 (`.gitignore` 부재 주장), #13 (PDF 구성·Yamaha 출처), #14 (`find_instruments.py`), #15 (`find_roland_gm_inst.py`), #18 (`LICENSE`) |
| **LOW** | 9 | #3 (prog 3), #4 (SPEC 891행), #9 (`Bank/` 서술·카테고리 접두사), #10 (중복키 예시 범위), #11 (§3-3 표 분류), #12 (행수 단위 혼용), #16 (잔재 4건), #19 (`.gitignore` 미추적), #20 (개발 시기) |
| **계** | **20** | |

### 7-3. 최종 판정

> ## **NEEDS_IMPROVEMENT**

**`FAIL`이 아닌 이유**: role spec이 `FAIL`로 규정한 두 조건에 해당하지 않는다.
(1) 평문 민감 정보가 0건이다. (2) 아키텍처 원칙 위반이 없다 — 생성기 3종은 바이트 동일
재현되고, 데이터 정합성은 누락·중복·추가 0이다. 그리고 이 프로젝트의 핵심 논지
("두 벤더의 주소 체계는 호환되지 않는다")는 실측으로 **확정**되었으며, 같은 문서의
주요 수치(Roland 318/40, Yamaha 511/53, GM2 256, XG 438, SFX 42, 시스엑스, bank 산술)는
**전부 정확**하다. 오류는 파생·요약 수치와 서술의 시제·전제에 국한된다.

**`PASS`가 아닌 이유**: 적발 20건 중 5건이 HIGH이며, 그중 #1·#2·#5·#8은 **문서가 자기
자신과 모순**되거나 **실측과 반대되는 전제를 사실로 단정**한다. 특히 #17 때문에 편입 결과가
저장소 이력에 없어 **새 체크아웃에서 파이프라인이 재현되지 않는다** — ATD 편입의 목적
자체가 달성되지 않은 상태다.

### 7-4. 필수 개선 항목 (우선순위 순)

1. **#17 편입 커밋**: `hp603 instruments.txt`, `data/yamaha-clp685-data.toml`, `.gitignore`,
   `Yamaha CLP-685.ins`, `docs/`, 정리된 4개 소스/산출물을 커밋한다. 이 조치 없이는
   §1의 재현성이 저장소 이력 수준에서 성립하지 않는다. 미추적 잔재 4건(#16)은 함께 정리한다.
2. **#2 수정**: `PROJECT-PROMOTION.md:82`의 "32 bank"를 **29 bank**으로 정정한다.
3. **#1 수정**: `:108`의 "예외 없이 LSB 64~71"을 **"LSB 0(3건: Violin·Cello·Pizzicato Str)을
   제외하면 LSB 64~71"**로 정정하고, 해당 3건이 `MSB=0, LSB=0`(GM Level 1 bank)임을 명시한다.
4. **#5 수정**: `:20`, `:268`, `:273`, `:337`의 555행을 **498행**으로, Yamaha 생성기 행수를
   **107**로 정정한다(`PROMOTION-SPEC.toml:77`과 일치시킨다).
5. **#8 수정**: `:309`의 전제를 **"커밋된 산출물은 LF-only였다"**로 바로잡고, `core.autocrlf=input`
   환경에서는 생성기의 CRLF 고정이 커밋 시 무효화됨을 기술한다. 실효를 원하면
   `.gitattributes`에 `*.ins text eol=crlf`를 추가해야 한다.
6. **#6·#7·#19 수정**: `README.md:62`의 "커밋되어 있으므로"를 실제 상태에 맞추거나(권장)
   `.toml`을 커밋해 주장을 참으로 만든다. `PROJECT-PROMOTION.md:327`의 "`.gitignore`가 없습니다"를
   현재 상태에 맞게 정정한다.
7. **#14·#15 수정**: `find_instruments.py`의 `make_dataframe`을 2단계 구조
   (`for category, groups in data.items(): for group, insts in groups.items():`)로 고치고,
   `find_roland_gm_inst.py`의 `get_cc_msg`를 `control=0, value=msb` / `control=32, value=lsb` /
   `program=pc`로 고친다. 또는 두 스크립트를 미지원으로 명시한다.
8. **#13 정정 및 판단**: `:329`의 PDF 구성을 실측대로(Roland 7 + Cakewalk 1) 고친다.
   `reference/`의 재배포 리스크와 Yamaha 1차 자료 부재를 함께 판단해, 출처 URL만 남기는
   방향을 권고한다.
9. **#18**: `LICENSE`를 추가한다(개인 도구 성격을 고려하면 MIT 등 관대한 라이선스가 무리 없다).

---

## 8. 확인 불가 항목

추측을 배제하기 위해, 근거를 확보하지 못한 항목을 명시한다.

1. `PROMOTION-SPEC.toml:68`의 "891행" 전사 분량의 출처 — 문서 `:187`의 829와 불일치하며,
   산정 근거를 저장소에서 확인할 수 없다.
2. `PROJECT-PROMOTION.md:258`의 "2019.10.24 ~ 10.25" 및 "2025.10" — 2019년 커밋이 없고
   (최초 2022-08-29), Yamaha 관련 커밋은 2025-12-23/26뿐이다. `.ins` 헤더의 "Oct 2019"만 확인된다.
3. Yamaha 511행 전사의 1차 자료인 CLP-685/695GP Data List 원문 — `reference/`에 없어
   전사 정확성을 원문 대조로 검증할 수 없다. (단 `docs/VERIFICATION-REPORT.md`의 전수 대조는
   전사본과 산출물 사이의 정합성만을 증명한다.)
4. `Roland HP603 - friendly names.ins`가 어떤 원본 데이터에서 생성되었는지 — 파일 자체만으로는
   최종 40 bank에 없는 MSB(19, 48, 68, 89 등)의 출처를 특정할 수 없다. 상위 tone list로 추정되나
   근거 파일이 저장소에 없다.
5. GM2 On 시스엑스 송신 후 실기 `MSB=121` bank이 실제로 채워지는지 — 실기 하드웨어가 없어
   규격 문서 수준까지만 확인했다.
6. `data/yamaha-clp685-data.txt`의 주석 4번째 줄(`#   Bank LSB`)에 대응하는 헤더가 본문에
   존재하는지 — Yamaha 산출물의 정합성에는 영향이 없으나 데이터 파일 자체의 서술 완결성은
   확인하지 않았다.
