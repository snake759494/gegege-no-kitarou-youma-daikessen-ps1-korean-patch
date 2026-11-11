# 게게게의 기타로 역습! 요마대혈전 (PS1) 비공식 한글패치

PS1 일본판 **ゲゲゲの鬼太郎 逆襲！妖魔大血戦 (게게게의 기타로 역습! 요마대혈전, SLPM-87286)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.bin`/`.cue`** (Redump 형식, 트랙 1개)를 준비합니다. (CHD·PBP·ECM 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan).bin'`
2. xdeltaUI 같은 도구로 원본 `.bin` 에 `Kitarou_Youma_Daikessen_KO_v1.0.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 BIN, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan).bin" Kitarou_Youma_Daikessen_KO_v1.0.xdelta "GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Korean).bin"`
3. 원본 `.cue` 를 복사해 이름을 바꾸고, 안의 `FILE "..."` 줄을 새 `.bin` 파일명으로 고칩니다.
4. 만들어진 `.cue` 를 DuckStation 등 PS1 에뮬레이터나 ODE 장치에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 BIN 크기 | 136,686,480 바이트 |
| 원본 BIN MD5 | `b52cd0642c87150c2df41fff33945e0e` |
| 원본 BIN SHA-256 | `de7fb1e28b031304f464d959e7edd2cc0ee32dc3e7aa0e5b193756f9224398b4` |
| xdelta SHA-256 | `0a229af9d686ec0446e7af29284dcf1e97b6419eb932ee5561eb972ba7502007` |
| 결과 BIN 크기 | 136,686,480 바이트 |
| 결과 BIN SHA-256 | `d3aca0c7c3a37e184786defdbdfbeb292b9a3fd8f54cb03a3a7d23d8601199ea` |

## 주의
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 글꼴 배치가 달라 글자가 깨집니다. 메모리 카드 세이브는 그대로 쓸 수 있습니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 360KB).

## 한글화 내용
- 대사·이름표·지명 516개 문자열(24개 블록) 전수 직접 번역
- 게임 글꼴(12×12)에 한글 추가, 글자 출력 루틴을 고쳐 반각 띄어쓰기 지원(글자 593자)
- 그림 글자 — 타이틀 컬러 로고(「게게게의 기타로 / 역습! 요마대혈전」)와 흰색 로고, 「스타트 버튼을 누르거라」, 타이틀·설정 메뉴, 미즈키 시게루 탄생 80주년 도장, 보스 이름 로고 16종, 일시정지 「잠시 쉬자꾸나!」, 동료 아이콘, 거점 메뉴(우체통·외출·기록·놀이 시간), 편지 보낸 사람, 지명판, 거점 배경의 「기타로의 집」, 튜토리얼 안내, 요괴도감 표지·이름·부위 이름, 엔딩 크레딧
- 그림 글자는 게임의 스프라이트 표에서 실제로 화면에 보이는 사각형을 읽어 그 안에 맞춰 그림
- 글꼴: 본문 갈무리11, 작은 그림 글자 갈무리9·11, 로고·메뉴·보스 이름 나눔스퀘어 네오, 거점 배경 지명 서울한강체

## 그대로 둔 것
- 음성, 영상, KONAMI 로고, 「Computer Entertainment Japan」 등 영문 표기, 메모리 카드 관리 화면에 보이는 세이브 제목

## 검증 범위
DuckStation에서 도장·타이틀 로고·스타트 문구·타이틀/설정 메뉴, 서장 대사·튜토리얼·일시정지·보스 이름, 메모리 카드 세이브로 불러온 거점 메뉴와 기록(세이브) 화면을 확인했습니다. 모든 대사 블록을 전수 검사해 번역이 빠진 문자열이 없는 것을 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
