# 빌드 방법

번역 대본(`text/`)과 글꼴 파일은 저장소에 없으므로, 아래는 같은 자료를 갖춘 경우의 절차입니다.

## 준비
- Python 3.11 이상, `pip install pillow numpy scipy keystone-engine zstandard`
- 원본 `GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan).bin` (README의 해시와 일치)을 저장소 상위 폴더에 둡니다.
- 디스크에서 `DATA.FAD`, `SLPM_872.86` 을 꺼내 `orig/` 에 둡니다(`tools/iso.py`).
- 글꼴: `fonts/Galmuri11.ttf`, `fonts/Galmuri9.ttf`, 상위 폴더에 `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf`, `SeoulHangangEB.ttf`

## 순서
1. 원문 추출: `python tools/extract_text.py` → `text/ja.json`
2. 번역: `text/ko_a.tsv`, `text/ko_b.tsv`, `text/ko_c.tsv` (`블록<TAB>번호<TAB>한국어`, 줄바꿈은 `/`)
3. 그림 글자 사양: `text/gfx_spec.py`(상자·번역어·글꼴), 타이틀 로고 팔레트 `text/logo_pal.json`
4. 빌드: `python build.py` → 상위 폴더에 `GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan) [KR].bin` (로그는 `build.log`)
5. 차분 파일: `xdelta3 -e -0 -S none -s "GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan).bin" "GeGeGe no Kitarou - Gyakushuu! Youma Daikessen (Japan) [KR].bin" Kitarou_Youma_Daikessen_KO_v1.0.xdelta`
