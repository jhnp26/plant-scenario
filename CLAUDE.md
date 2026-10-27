# 발전소 사고 시나리오 — 프로젝트 안내 (Claude Code용)

전기과 고졸 공기업 입사 예정자(한수원·발전사·한전 등)와 친구들이 쓰는 시나리오형 학습 웹앱.
사이트: https://jhnp26.github.io/plant-scenario/ (GitHub Pages, main 브랜치 루트 → push하면 1~2분 뒤 반영)
사용자는 한국어로 답을 받길 원하고 토큰 절약을 선호함. 단순 암기보다 "상황 → 판단 → 이유" 학습을 좋아함.

## 파일
- `index.html` — 앱 전체(HTML+CSS+JS 한 파일, 빌드 없음). 로드 시 `data.json`을 동기 XHR로 읽어 `window.__DATA`에 넣음.
  - **data.json을 고치면 index.html 안의 `data.json?v=...` 숫자를 올려야** 캐시 없이 반영됨.
- `data.json` — `{scenarios:[], terms:{}, news:[]}`
- `config.js` — Supabase URL·anon key(공개용, 안전). 수정 불필요.
- `manifest.webmanifest`, `icon.svg` — PWA(홈 화면 추가).
- `supabase.sql` — 초기 스키마 참고용(실제 DB에는 이후 마이그레이션이 더 있음).
- `tools/validate.py` — 데이터 검사. `tools/test.py` — 브라우저로 200개 시나리오 자동 풀이 테스트.

## 데이터 구조
시나리오 `{id, lv, date, title, sub, intro, chain, steps[], tg?}`
- `lv`: 입문|이론|기본|계통|사례|심화. `tg`: nuc|thermal|grid|etc|gen (없으면 본문으로 원자력/공통 자동 판별).
- step: `{type?: mc|ox|multi|order, q, o[], a, ans?, e, w?, l[]}`
  - mc: `a`=정답 인덱스(현재 전부 0 — 화면에서 섞어서 보여줌). `w`=보기별 '왜 틀렸나' 배열(o와 같은 길이, 정답 칸은 "") — 틀렸을 때 고른 보기의 이유를 보여줌. 새 mc 문항에도 넣을 것. 오답 보기 길이가 정답보다 눈에 띄게 짧으면 안 됨(정답 길이 티 방지).
  - ox: `o=["O 맞다","X 틀리다"]`. multi: `ans`=정답 인덱스 배열. order: `o`가 올바른 순서.
  - `e` 해설, `l` 관련 용어 키(terms에 반드시 존재).
용어 `terms[key] = {c 분류, k 키, t 이름, s 한줄뜻, d 자세히, f 현장, l 관련}`
뉴스 `{id,date,title,sum,why,src:{name,url},case?,q?}` — 출처 URL 필수, 사실만.

## 백엔드 (Supabase, 프로젝트 id `waakqddnbjsjerczodug`, 서울 리전)
- 아이디/비번 로그인은 자체 RPC: `app_signup, app_login, app_load, app_save, app_logout, app_ranking` (bcrypt, 토큰은 localStorage `khnp-token`).
- 테이블: `app_users, app_sessions, app_progress, content_items(kind scn|term|news, data jsonb, 공개 읽기)`.
  - content_items에 넣은 시나리오/용어/뉴스는 사이트가 로드할 때 합쳐짐(배포 없이 콘텐츠 추가 가능).
- 랭킹 점수 = 끝낸 시나리오×10 + 맞힌 문제 + 공부한 날×5. `pref.hide`면 랭킹에서 숨김.
- 실사용자 있음(예: jsi0114 = 이 프로젝트 주인). **실DB에 테스트 계정 만들지 말 것.**

## 작업 규칙
1. 수정 후 `python3 tools/validate.py` → `python3 tools/test.py` 통과 확인 후 commit/push.
2. 사실 확인: 사고 사례·수치·뉴스는 검색해서 확인. 계통도는 "공개자료 기반 대표 구조"임을 유지.
3. 모바일(390px) 우선. 가로 스크롤 금지.
4. Claude 아티팩트 버전(claude.ai/artifact/S8JjFVd8gKr6dNCZLvBh14)은 예전 사본이고, 이제 이 사이트가 본판.

## 품질 개선 할 일 (2026-10-27 점검 결과)
- [x] 해설 보강: 934문항 중 258개가 60자 미만. "정답 이유 + 원리 + 현장 연결" 2~3문장으로.
- [x] 오답 해설: mc 문항에 `w`(보기별 왜 틀렸는지 짧은 설명 배열) 추가 → 틀렸을 때 고른 보기의 이유를 보여주기.
- [x] 시나리오 목록: 200개가 한 줄로 길게 나열됨 → 검색창, 단계별 접기, 완료 표시.
- [x] `tg` 태그가 23개에만 있음 → 전 시나리오에 명시.
- [x] 화면 하단 "기준: 국내 APR1400…" 문구가 모든 화면에 반복 → 홈/계통도에만.
- [x] 홈 화면이 길다 → 오늘 할 일·다음 시나리오 위주로 압축, 첫 안내 카드는 첫 시나리오 후 숨김.
- [x] 콘텐츠 보강: 화력 5·송변전 5·기타 공기업 2 시나리오, 용어 12개, 계통도 '수전설비·비상발전기'(rcv) 추가. 화력·송변전·기타는 아직 공통/원전보다 적으니 계속 보강하면 좋음.
- [ ] 관리자 기능(선택): 랭킹 개발자 뱃지, 공지, 부적절 아이디 숨김.
- [ ] 매일 자동 추가 예약작업은 현재 꺼져 있음. 다시 하면 content_items에 넣는 방식 권장.
