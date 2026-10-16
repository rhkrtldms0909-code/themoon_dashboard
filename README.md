# 더문 멤버십 대시보드

팬딩 더문 멤버십의 월별 가입·이탈·활성 멤버 추이를 보여주는 정적 사이트입니다. GitHub Pages로 배포합니다.

- `index.html` — 대시보드 페이지
- `data.json` — 집계 숫자 (닉네임·연락처 등 개인 정보 없음)
- `scripts/build_data.py` — 팬딩 엑셀 두 개로 `data.json`을 다시 만드는 스크립트

## 매달 갱신

```bash
pip install pandas openpyxl
python scripts/build_data.py 멤버십가입자목록_YYYY-MM-DD.xlsx 멤버십이탈자목록_YYYY-MM-DD.xlsx YYYY-MM-DD
```

새로 생긴 `data.json`만 저장소에 올리면 사이트가 바뀝니다. 엑셀 원본은 개인 정보가 있으니 저장소에 올리지 마세요.

## 집계 기준

- 신규 가입: 최초 가입 월. 이탈자는 가입일이 없어 `이탈일 − 마지막 회차 × 30일`로 가입 월을 추정합니다.
- 월말 활성: 그 달 말까지 가입했고 아직 이탈하지 않은 인원.
- 플랜 묶음: 3Package(5만·6만원) / 프리미엄 Package(12만·15만·18만원, 얼리버드 포함) / 3+프리미엄(16만·18만·21만원) / 기타.
