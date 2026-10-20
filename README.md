# 261014_1127_woori

**심화_AI기반 지능형 솔루션 개발 과정** 실습 코드 저장소

| 항목 | 내용 |
|------|------|
| 기간 | 2026-10-14 ~ 2026-11-27 |
| 학습 허브 | https://261012-1127-bucheon.vercel.app |
| 실습 환경 | Anaconda + VSCode · Python |

## 수업 시간

수업일: **월 · 화 · 수 · 금**

| 교시 | 시간 |
|------|------|
| 1교시 | 09:20 ~ 10:10 |
| 2교시 | 10:20 ~ 11:10 |
| 3교시 | 11:20 ~ 12:10 |
| 4교시 | 12:20 ~ 13:10 |
| 점심 | 13:10 ~ 14:10 |
| 5교시 | 14:10 ~ 15:00 |
| 6교시 | 15:10 ~ 16:00 |
| 7교시 | 16:10 ~ 17:00 |
| 8교시 | 17:10 ~ 18:00 |

## 커리큘럼

학습 허브에서 주제 순서대로 진행합니다. 앞 주제의 노드를 모두 완료해야 다음 주제가 열립니다.

| # | 주제 | 내용 |
|---|------|------|
| 1 | VSCode | 에디터 설치·설정 |
| 2 | Anaconda | 가상환경 구성 |
| 3 | Python | 변수·자료형·조건문·반복문·함수·클래스 |
| 4 | Data | 데이터 수집·증강·라벨링 |
| 5 | YOLO | 분류·탐지·포즈·세그멘테이션 → 커스텀 학습 |
| 6 | OpenAPI | 공공 API 활용 |
| 7 | Groq API | LLM API 호출 |
| 8 | HuggingFace | 모델 허브 활용 |
| 9 | Transformers | 사전학습 모델 파이프라인 |
| 10 | OCR | 이미지 속 문자 인식 |
| 11 | Streamlit | 웹 데모 만들기 |
| 12 | Gradio | 모델 데모 UI |
| 13 | Claude Web | Claude 로 웹 만들기 |
| 14 | Claude Code | AI 코딩 에이전트 활용 |
| 15 | Team Project | 팀 프로젝트 |

## 폴더 구조

| 폴더 | 날짜 | 내용 |
|------|------|------|
| `261012_python/` | 10/12 | Python 기초 — 자료형·f-string·if·for·zip·함수·try·while·with·class·lambda |
| `261014_1_data/` | 10/14 | 데이터 수집(로컬·스케줄)·증강·라벨링 |
| `261014_2_yolo_basic/` | 10/14 | YOLO 기초 — cls·det·pose·seg·파라미터 |
| `261016_3_yolo_basic/` | 10/16 | YOLO 기초 — HTTP 이미지 추론·putText |
| `261016_4_yolo_advan/` | 10/16 | YOLO 심화 — track·heatmap·alarm·blur·distance |
| `261019_5_yolo_advan/` | 10/19 | YOLO 심화 — region·in_out·SAHI·speed·SAM·FastSAM·export·compare·Streamlit |
| `261019_6_openapi/` | 10/19 | 공공 API(ITS CCTV) + YOLO 연동 |
| `261020_7_groq_api/` | 10/20 | Groq API — 기본 호출·챗봇·페르소나 챗봇·챗봇 레포 구축 과제 |
| `261020_8_hugging/` | 10/20 | HuggingFace — DeepSeek 호출·TTI(텍스트→이미지)·서비스 구축 과제 |
| `261020_8_hugging/demo/` | 10/20 | HF 서비스 경진대회 지침·채점 기준·투표 서버(`vote_server/`) |
| `captured_images/` | — | 캡처 결과 라벨(txt·xml) |
| `labeling/roboflow_label/` | — | Roboflow 라벨 데이터셋(라벨·data.yaml) |

> 이미지·영상·모델 가중치(`.pt`)·데이터셋 압축 파일은 용량 문제로 올리지 않습니다.
> API 키(`.env`·키 텍스트 파일)는 올리지 않습니다. Groq·HuggingFace 실습은 환경변수 `GROQ_API_KEY`·`HF_TOKEN` 을 설정한 뒤 실행하세요.
