<!-- English summary for GitHub discoverability -->
**Korean fan-translation patch for _Tengai Makyou II: Manji Maru_ (天外魔境II 卍MARU, Nintendo DS, game code ATMJ).** Tools, translation data, and font for building the patch — no ROM included.

# 천외마경II 卍MARU 한국어 패치 (Tengai Makyou II: Manji Maru — Korean Patch)

> 닌텐도 DS용 RPG **천외마경II 卍MARU**(일본판, 게임코드 `ATMJ`, 128 MiB)의 비공식 한국어 팬 번역 패치 소스/도구 저장소입니다.
> 본문 대사 약 97% 한글화 + 메뉴 그래픽 전체 + 시스템/전투/저장 텍스트.

- 코드/도구 라이선스: **MIT**
- 폰트: **Galmuri11** (SIL Open Font License 1.1)
- 비공식·비영리 팬 번역 — **이 저장소에는 게임 롬이 일절 포함되지 않습니다.**

---

## 무엇인가요

원작 © Red Company(レッド) / Hudson Soft / Sting. 이 저장소는 깨끗한 일본판 ROM에 적용해 게임을 한글로 즐길 수 있게 하는 **패치와 빌드 도구**만 담고 있습니다. 일반 사용자는 `dist/`의 xdelta 패치를 적용하면 되고, 개발자는 `patch/`의 소스에서 직접 빌드할 수 있습니다.

## 완성도 / 상태

- **본문 대사 약 97% 한글화** — 전 스토리·엔딩·전투·시스템 UI·사운드 테스트 등.
- **메뉴 이미지 전체** — 메인/필드/하단 라벨 메뉴, 전투 명령 16개 아이콘, 시작 선택 화면(起=처음 / 転=계속).
- **ARM9·오버레이의 시스템/전투/저장 텍스트** 한글화.
- 한글 폰트는 **Galmuri11**을 게임의 한자 글리프 슬롯에 그려 넣어 구현(KS X 1001 완성형 2,350자).
- 지명 배너는 프레임 폭이 글자 수에 맞춰 자동 조절됩니다.

> **미포함**: 서브로케이션 세부 지명(`chimei.scs`)은 별도의 커스텀 글리프가 필요해 이번 패치에서 제외했습니다. 게임 진행·전투·메뉴에는 영향이 없습니다.

## 주요 특징

| 영역 | 내용 |
| --- | --- |
| 대사 | `.scs` 대사 컨테이너 전체를 번역문으로 재조립. 화자/초상·줄바꿈·페이지 구분 등 제어코드 보존. |
| 폰트 | Galmuri11 비트맵을 16×16 글리프로 렌더링해 게임 한자 폰트(CObj) 슬롯에 무손실 주입. 한글은 한자 SJIS 코드 재매핑 트릭으로 출력. |
| 메뉴 그래픽 | 메인/필드/전투/시작 화면을 한글 PNG로 직접 교체(추출→편집→삽입 키트 포함). |
| 시스템 텍스트 | ARM9 바이너리·오버레이의 메뉴/전투/저장/아이템/주문 문자열을 바이트 길이 보존 치환. |
| 지명 용어사전 | 지명을 **한자독음(1한자=1한글음절)**으로 통일(187개 표제어). 배너 폭 초과 방지 + 표기 일관성. |

---

## 패치 적용법 (일반 사용자)

준비물: **깨끗한 천외마경II 卍MARU 일본판(ATMJ) 롬 파일**과 xdelta 패처.

`dist/` 폴더의 `.xdelta` 패치를 깨끗한 원본 롬에 적용합니다. 이 패치는 **2차 압축 없이(no secondary compression)** 만들어 PC 패처와 안드로이드 **UniPatcher** 양쪽에서 그대로 동작합니다.

### PC (xdelta3 / GUI 패처)

xdelta3([공식 배포](https://github.com/jmacd/xdelta)) 명령줄:

```
xdelta3 -d -s 원본_ATMJ.nds "dist/Tengai Makyou II - Manji Maru (Korean)_20260629.xdelta" 출력_KR.nds
```

GUI 패처(예: delta patcher, MultiPatch)라면 원본 롬과 `.xdelta` 파일을 지정하고 Apply를 누르면 됩니다.

### 안드로이드 (UniPatcher)

1. 원본 ATMJ 롬과 `dist/`의 `.xdelta` 파일을 기기에 복사합니다.
2. UniPatcher에서 패치 파일(`.xdelta`)을 고른 뒤 원본 롬을 지정해 적용합니다.

> 이 패치는 UniPatcher가 디코드하지 못하는 2차 압축(DJW/LZMA)을 사용하지 않으므로 바로 적용됩니다.

### 적용 후

결과 롬 크기가 **134,217,728 바이트(128 MiB)** 인지 확인한 뒤 에뮬레이터(멜론DS / DeSmuME)나 플래시카트/실기에 올립니다.

> 패치는 반드시 **깨끗한 원본 일본판 롬**에 적용하세요. 이미 패치된 롬에 다시 적용하면 정상 동작하지 않습니다.

---

## 소스에서 빌드 (개발자)

`patch/`의 소스로 직접 ROM을 빌드할 수 있습니다.

### 준비물

- **Python 3.8 이상**
- 파이썬 패키지 **numpy, Pillow, ndspy**

```
pip install numpy pillow ndspy
```

- 천외마경II 卍MARU **(일본판, ATMJ) 롬 파일** *(저장소에 포함되지 않음)*

### Windows

- **방법 1 (가장 쉬움)**: `patch/patch_windows.bat` 위로 롬 파일을 마우스로 끌어다 놓기 → 같은 폴더에 `입력이름_KR.nds` 생성.
- **방법 2**: 명령 프롬프트에서

  ```
  python patch/patch.py 입력롬.nds 출력롬.nds
  ```

### Mac / Linux

```
chmod +x patch/patch_mac_linux.sh        # 최초 1회
./patch/patch_mac_linux.sh 입력롬.nds       # → 입력이름_KR.nds 로 저장
# 또는
python3 patch/patch.py 입력롬.nds 출력롬.nds
```

`patch.py`는 대사·폰트·시스템 텍스트 패치를 적용한 뒤 `menu/png/`의 한글 메뉴 이미지를 삽입합니다. 정상 출력 크기는 **134,217,728 바이트**입니다.

> 가능하면 **매번 깨끗한 입력 롬**에 빌드하세요. 같은 출력 파일에 반복 적용하면 파일이 불필요하게 커질 수 있습니다(동작에는 무해). 이미 한글이 들어간 롬을 입력하면 대사 단계에서 "원문 불일치" 경고가 다수 나올 수 있는데, 이는 기존 한글이 보존된다는 뜻이라 정상입니다.

### 메뉴 이미지 다시 그리기

메뉴 그래픽은 글꼴로 자동 렌더링하지 않고 **PNG 이미지를 직접 삽입**하는 방식입니다. 기본 제공된 `patch/menu/png/`에 한글 메뉴가 이미 들어 있어 그대로 빌드하면 적용됩니다. 직접 편집하려면:

```
cd patch/menu
python menu_extract.py 원본롬.nds png/      # 1) 원본 메뉴 → 인덱스 PNG 추출
#   png/ 안의 PNG를 한글로 편집 (캔버스 크기·팔레트 색 유지)
python menu_insert.py 입력롬.nds png/ 출력롬.nds   # 3) 수정 PNG 삽입 (메뉴만)
```

자세한 규칙은 [`patch/menu/PATCH_DATA.md`](patch/menu/PATCH_DATA.md)를 참고하세요. (편집 시 캔버스 크기는 절대 바꾸지 말고, 원본 팔레트 색만 사용하세요.)

### 지명 배너 폭 조절

지명 배너 테두리는 가장 넓은 행의 글자 수에 맞춰 자동으로 늘어납니다. 폭을 미세 조정하려면 `patch/banner_tool.py`로 행 텍스트에 전각 공백(U+3000)을 패딩합니다.

```
python patch/banner_tool.py list                 # 모든 지명 배너 + 현재 프레임 폭
python patch/banner_tool.py list 아키바            # 이름으로 검색
python patch/banner_tool.py pad <인덱스> <목표너비>  # 본문 행 좌우 균등 패딩
```

수정 후 다시 `patch.py`로 빌드하면 반영됩니다.

---

## 저장소 구성

```
.
├── dist/                 배포용 xdelta 패치 (일반 사용자용)
└── patch/                패치 패키지 (코드 + 번역데이터 + 폰트)
    ├── patch.py          통합 빌드 러너 (이걸 실행)
    ├── patch_windows.bat Windows 드래그앤드롭 실행
    ├── patch_mac_linux.sh Mac/Linux 실행
    ├── banner_tool.py    지명 배너 프레임 폭 조절 도구
    ├── LICENSE.txt       Galmuri11 폰트 라이선스 (SIL OFL 1.1)
    ├── dialogue/         대사 + 폰트 + 시스템 텍스트 패치
    │   ├── build_ko.py           최상위 빌드 오케스트레이터
    │   ├── scs_repack.py         .scs 포인터 테이블 리패커
    │   ├── scs_segment.py        엔트리 본문 ↔ 세그먼트 변환
    │   ├── scs_text.py           페이지/줄/제어 시퀀스 빌더 + 글자 인코딩
    │   ├── tengai_cobj_font.py   CObj 전각 폰트 decode/encode
    │   ├── galmuri_bdf.py        Galmuri11 BDF 렌더러
    │   ├── font_mapping.py       SJIS↔슬롯↔한글 매핑
    │   ├── arm9_text.py          ARM9/오버레이 SJIS 문자열 치환
    │   ├── merge_unify.py        지명 통일 결과 → translation.json 병합
    │   ├── merge_unify_arm9.py   지명 통일 결과 → arm9_translation.json 병합
    │   ├── translation.json      대사 번역 데이터
    │   ├── arm9_translation.json ARM9 텍스트 번역 데이터
    │   ├── 지명사전.json / .txt   187개 지명 한자독음 용어사전
    │   ├── ks2350.txt            KS X 1001 완성형 2,350자
    │   └── Galmuri11.bdf         한글 폰트
    └── menu/              메뉴 이미지 추출/삽입 키트
        ├── menu_extract.py  원본 메뉴 → 인덱스 PNG 추출
        ├── menu_insert.py   수정 PNG → 롬 삽입
        ├── patch_all.py     png/ 일괄 삽입 (patch.py가 호출)
        ├── tools.py         FAT/FNT/LZ10 공용 라이브러리
        ├── cmp.py           다단계 CMP 압축 코덱
        ├── png/             삽입할 한글 메뉴 PNG ← 이걸 수정
        └── PATCH_DATA.md    메뉴 바이너리 포맷 기술 사양
```

기술 세부는 [`ARCHITECTURE.md`](ARCHITECTURE.md)를 참고하세요.

---

## 지명 한자독음 정책

지명을 그대로 음차하면 한글 음절 수가 늘어 배너 프레임 폭을 넘기는 경우가 많습니다. 이를 막기 위해 지명을 **한자독음(1한자 = 1한글 음절)**으로 통일했습니다. 예를 들어 `峠`(고개)는 2음절 대신 **재**(1음절)로, `村`→**촌**, `神社`→**신사**처럼 옮깁니다. 가타카나 지명은 음차하고, 일반명사 16개(高山·神社·外国·洞窟 등)는 지명이 아니므로 통일 대상에서 제외했습니다. 187개 표제어는 `patch/dialogue/지명사전.json`/`.txt`에 정리되어 있으며, 이를 기준으로 대사·ARM9 번역 전반의 지명 표기를 정본으로 통일했습니다.

---

## 라이선스

- **도구/코드**: MIT License.
- **Galmuri11 폰트**: SIL Open Font License 1.1 — © Lee Minseo (quiple). 라이선스 전문은 `patch/LICENSE.txt` 참고.
- **게임 텍스트**: 저작권물의 2차적 저작물에 해당합니다. 비영리 팬 번역 목적이며, **게임 롬·게임 원본 그래픽은 저장소에 포함하지 않습니다.**

## 크레딧

- 번역 / 롬해킹: **snake7594**
- 폰트: **Galmuri** — quiple (Lee Minseo)
- 의존성: Python 3.8+, numpy, Pillow, ndspy

## 면책

이 프로젝트는 Red Company / Hudson Soft / Sting 및 권리자와 무관한 **비공식 팬 번역**이며, 어떠한 영리 목적도 없습니다. 패치는 사용자가 합법적으로 소유한 원본 롬에 적용하는 용도로만 제공됩니다. 게임 롬은 이 저장소에 포함되어 있지 않으며 배포하지 않습니다.