# 잭 & 덱스터: 구세계의 유산 — 한글화 (OpenGOAL)

PS2 『Jak and Daxter: The Precursor Legacy』(잭 1편)를 PC 포트 [OpenGOAL](https://github.com/open-goal/jak-project)에서 한국어로 즐기기 위한 비공식 팬 한글화 프로젝트입니다.

![표지](cover_ko.png)

> 번역 전체(2,158항목) 완료·검수 승인. 현황은 [docs/translation_status.md](docs/translation_status.md)를 보세요.

## 무엇을 하나

- **한글 표시**: 1편 폰트에는 한글이 없어서, 폰트 텍스처를 확장하고 새 코드페이지(리드 바이트 2·4–9·11·12·14·15 + 글리프 바이트)를 엔진에 추가했습니다. 최대 2,035 음절.
- **서체**: 메뉴는 배민 주아체, 자막은 Pretendard SemiBold (둘 다 OFL).
- **번역 범위**: 메뉴·힌트 텍스트, OpenGOAL 추가 메뉴, 컷신·힌트 자막, 엔딩 크레딧 제목·역할명 (총 2,158 항목). 음성은 영어 원본 그대로.
- **번역하지 않은 것**: 텍스처로 그려진 글자(타이틀 로고, 진행 메뉴의 "AUTO SAVE OFF" 등), 크레딧의 인명·회사명.
- **언어**: OpenGOAL 의 예약 언어 ID 17(korean)로 텍스트·자막 언어에 추가.

## 필요한 것

- 본인 소유의 **Jak and Daxter: The Precursor Legacy NTSC-U (SCUS-97124, Black Label) ISO**. 게임 데이터는 이 저장소에 포함되지 않습니다.
- Linux: clang, cmake, ninja, nasm, python3 (+ Pillow, pytest), `libssl-dev` 등 [OpenGOAL 빌드 요구 사항](https://github.com/open-goal/jak-project#building-and-running-the-game)
- Windows: 아래 [Windows 설치](#windows-설치) 참고

## 간편 설치 (미리 빌드한 패키지)

빌드 도구 없이 설치하는 방법입니다. 패키지에는 게임 데이터가 없고, 본인 ISO 로 설치할 때 한글 폰트를 합성합니다.

1. 릴리스 페이지에서 `jak1-korean-<버전>-windows.zip` 을 받아 원하는 폴더에 풉니다.
2. ISO 파일을 `install.bat` 에 끌어다 놓습니다 (추출·빌드에 몇 분 걸림).
3. `play.bat` 으로 실행하고, 게임 옵션에서 **텍스트 언어**·**자막 언어**를 **한국어**로 바꿉니다.

설정과 세이브는 패키지 폴더 안에 저장됩니다 (`--portable`). 자세한 안내는 패키지의 `README.txt` 를 보세요.

## 설치 (Linux)

1. 이 저장소를 받습니다.
   ```bash
   git clone https://github.com/stPark-dev/Jak_Daxter_The_Precursor_Legacy_Korean.git
   cd Jak_Daxter_The_Precursor_Legacy_Korean
   ```
2. OpenGOAL 을 받아 한글 패치를 적용하고 빌드한 뒤, 본인 ISO 를 추출합니다 (처음 한 번, 수십 분 걸림).
   ```bash
   tools/setup_opengoal.sh /path/to/jak1.iso
   ```
3. 한글 폰트를 만들고 번역을 넣어 게임을 빌드합니다.
   ```bash
   tools/build_kr.sh release
   ```
   (`dev` 는 작업용으로 미번역 줄을 영어 원문으로 채웁니다. `release` 는 모든 줄이 검수 승인일 때만 성공합니다.)
4. 실행합니다.
   ```bash
   jak-project/build/Release/bin/game/gk -- -boot -fakeiso
   ```
5. 게임에서 START → 옵션 → 게임 옵션으로 가서 **텍스트 언어**와 **자막 언어**를 **한국어**로 바꿉니다.
   "음성 언어"는 영어 그대로 두세요 (음성은 영어만 있습니다).

### 문제 해결

- `setup_opengoal.sh` 는 OpenGOAL `b6c8430` 에 패치를 적용합니다. 이미 `jak-project/` 에 다른 수정이 있으면 패치가 실패하니 지우고 다시 실행하세요.
- 확인한 ISO 는 NTSC-U Black Label (SCUS-97124) 뿐입니다. 다른 판(Greatest Hits, PAL, 일본판)은 확인하지 않았습니다.

## Windows 설치

Windows 10 에서 설치부터 한글 표시까지 확인했습니다 (2026-10-16, VS 2022 Build Tools 17.14 + LLVM 23.1.3).

1. PowerShell 에서 빌드 도구를 설치합니다. 관리자 권한(UAC) 창이 뜨면 허용하세요.
   ```powershell
   winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   winget install --id Git.Git -e
   winget install --id LLVM.LLVM -e
   winget install --id Kitware.CMake -e
   winget install --id Ninja-build.Ninja -e
   winget install --id NASM.NASM -e
   winget install --id Python.Python.3.11 -e
   python -m pip install pillow pytest
   ```
   설치 후에는 새 터미널을 여세요 (PATH 갱신).
2. 저장소를 받습니다.
   ```bat
   git clone https://github.com/stPark-dev/Jak_Daxter_The_Precursor_Legacy_Korean.git
   cd Jak_Daxter_The_Precursor_Legacy_Korean
   ```
3. OpenGOAL 을 받아 한글 패치를 적용하고 빌드한 뒤, 본인 ISO 를 추출합니다 (처음 한 번, 16코어 기준 약 40분).
   ```bat
   tools\kr.bat setup C:\Games\jak1.iso
   ```
4. 한글 폰트를 만들고 번역을 넣어 게임을 빌드합니다.
   ```bat
   tools\kr.bat build release
   ```
5. 실행합니다.
   ```bat
   tools\kr.bat run
   ```
   (직접 실행하려면 `jak-project\out\build\Release\bin\gk.exe -- -boot -fakeiso`)
6. 게임에서 START → 옵션 → 게임 옵션 → **텍스트 언어**·**자막 언어**를 **한국어**로 바꿉니다.

`tools\kr.bat` 는 Visual Studio C++ 환경(`vcvars64`)을 불러오고, winget 이 PATH 에 넣지 않는 LLVM·NASM 경로를 더한 뒤
Git Bash 로 Linux 와 같은 스크립트(`setup_opengoal.sh`, `build_kr.sh`)를 실행합니다.
Git Bash 의 `link` 명령이 MSVC 링커를 가리지 않도록 MSVC 경로를 앞에 둡니다.
이 저장소와 OpenGOAL 은 줄 끝 변환 없이(LF) 받아야 패치가 적용됩니다 (`.gitattributes`, `core.autocrlf=false` 로 처리).

## 배포 패키지 만들기

`build release` 뒤에 실행합니다. 정적 링크 바이너리를 따로 빌드하고(`out/build/Release-static`), `dist/` 에 zip 을 만듭니다.

```bat
tools\kr.bat package 1.0.0
```

(Linux: `tools/package_kr.sh 1.0.0` → `tar.gz`, 미검증.) 패키지에 ISO 에서 나온 파일이 섞이면 실패합니다.

## 저장소 구성

| 경로 | 내용 |
|---|---|
| `patches/opengoal-kr.patch` | OpenGOAL `b6c8430` 기준 엔진 수정 (폰트 코드페이지, 한국어 텍스트·자막 컴파일, 언어 17 등록, 텍스처 오버레이, 테스트) |
| `tools/package_kr.sh`, `tools/dist/` | 배포 패키지 생성 스크립트와 패키지에 들어가는 설치·실행 스크립트 |
| `tools/kr_font/` | 한글 폰트 텍스처·코드표 생성기 (한글 글자만 그린 오버레이를 만들고, 추출 때 원본 폰트 위에 합성) |
| `tools/translation/` | 번역 워크스페이스 도구 (검사·내보내기·읽기 속도 점검) |
| `translation/` | 번역 원문·번역문·검수 상태 |
| `docs/` | 결정 기록, 조사, PoC, 용어집, 진행 현황 |
| `fonts/` | 배민 주아체, Pretendard SemiBold 와 각 OFL 라이선스 |

## 테스트

```bash
(cd tools && python3 -m pytest -q kr_font text translation)   # 도구 테스트
jak-project/build/Release/bin/goalc-test                      # OpenGOAL 회귀 + 한국어 인코딩 테스트
(cd tools && python3 -m pytest -q test_build_output.py)       # 빌드 결과물 검사 (build_kr.sh 이후)
```

## 라이선스·고지

- 『Jak and Daxter』 및 관련 상표·캐릭터·원문 텍스트의 권리는 Sony Interactive Entertainment / Naughty Dog 에 있습니다. 이 프로젝트는 비공식 팬 작업이며 어떤 회사와도 관련이 없습니다.
- 용어집의 한국어 표기는 이 패치의 자체 결정이며 공식 한국어 명칭이 아닙니다 ([docs/glossary.md](docs/glossary.md)).
- 서체: 배민 주아체(© The Jua Project Authors), Pretendard(© Kil Hyung-jin) — SIL Open Font License 1.1.
- OpenGOAL 은 ISC 라이선스입니다.
