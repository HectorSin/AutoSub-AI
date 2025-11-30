# AutoSub-AI 개발 계획서 (PLAN.md)

> 기술 명세서(TECHSPECH_PLAN.md)를 기반으로 한 체크리스트 형식 개발 계획

## 📌 프로젝트 정보
- **프로젝트명**: AutoSub-AI
- **버전**: 0.1.0
- **목표**: 영상 파일 → STT + LLM → 자연스러운 한국어 자막(SRT) 자동 생성
- **배포 형태**: Portable EXE (GUI 기반 로컬 웹 앱)

---

## Phase 1: 프로젝트 초기 설정 및 기반 구축

### 1.1 프로젝트 환경 설정
- [x] 프로젝트 디렉토리 구조 생성
  - [x] `/assets` (아이콘 파일)
  - [x] `/src/core` (핵심 로직)
  - [x] `/src/gui` (Streamlit UI)
  - [x] `/src/prompts` (프롬프트 리소스)
  - [x] `/src/utils` (유틸리티)
  - [x] `/tools` (FFmpeg 바이너리)
  - [x] `/models` (Whisper 모델 저장소)
  - [x] `/logs` (로그 저장소)
- [x] 가상환경 생성 및 활성화 (conda)
- [x] `requirements.txt` 작성
  - [x] faster-whisper>=1.0.0
  - [x] anthropic>=0.40.0
  - [x] pydantic>=2.0.0
  - [x] silero-vad>=5.0.0
  - [x] structlog>=24.0.0
  - [x] typer>=0.9.0
  - [x] tqdm>=4.66.0
  - [x] pyyaml>=6.0.0
  - [x] python-dotenv>=1.0.0
  - [x] ffmpeg-python>=0.2.0
  - [x] streamlit>=1.28.0
  - [x] pyinstaller>=6.0.0
  - [x] keyring>=24.0.0
  - [x] pystray>=0.19.0
  - [x] pillow>=10.0.0
  - [x] psutil>=5.9.0
- [x] 의존성 패키지 설치

### 1.2 설정 파일 작성
- [x] `config.yaml` 작성 (기본 설정)
  - [x] app 정보 (name, version)
  - [x] input 설정 (지원 포맷, 최대 파일 크기)
  - [x] output 설정 (경로, 네이밍 규칙)
  - [x] processing 설정 (chunk_size, overlap, workers)
  - [x] stt 설정 (model, device, language)
  - [x] llm 설정 (provider, model_name, prompt_path)
  - [x] logging 설정 (level, dir, format)
- [x] `.env.example` 작성 (API Key 참고용)
- [x] `.gitignore` 작성
  - [x] .env, /temp/, /output/, /models/, /logs/
  - [x] __pycache__, *.pyc, /dist/, /build/

### 1.3 프롬프트 및 리소스 준비
- [x] `src/prompts/correction.txt` 작성 (LLM 교정 프롬프트)
- [x] `src/prompts/glossary.json` 작성 (보존/대체 단어 사전)
- [x] `assets/app.ico` 준비 (애플리케이션 아이콘)
- [x] `assets/tray_icon.png` 준비 (시스템 트레이 아이콘)
- [x] FFmpeg 바이너리 다운로드 및 `tools/ffmpeg.exe` 배치

---

## Phase 2: 핵심 로직 구현 (Core)

### 2.1 오디오 처리 (audio_processor.py)
- [ ] FFmpeg 경로 감지 로직 구현
  - [ ] `sys._MEIPASS` 활용 (PyInstaller 환경)
  - [ ] 로컬 개발 환경 경로 지원
- [ ] 영상에서 오디오 추출 기능 구현
  - [ ] 지원 포맷 검증 (mp4, mkv, avi, mov, webm)
  - [ ] ffmpeg-python을 사용한 오디오 추출
- [ ] 오디오 파일 검증 및 에러 핸들링
- [ ] 임시 파일 관리 (`./temp/` 폴더)

### 2.2 STT 엔진 (stt_engine.py)
- [ ] Faster-Whisper 모델 초기화
  - [ ] 모델 경로 설정 (`./models/`)
  - [ ] 디바이스 자동 감지 로직 (CPU/GPU)
- [ ] 모델 다운로드 로직 구현
  - [ ] 첫 실행 시 자동 다운로드 옵션
  - [ ] `tqdm` 프로그레스 바 UI
  - [ ] 다운로드 실패 시 에러 핸들링
- [ ] VAD (Voice Activity Detection) 통합
  - [ ] silero-vad를 사용한 음성 구간 감지
  - [ ] 청크 단위 처리 (300초, 5초 오버랩)
- [ ] 타임스탬프 정확도 보장
  - [ ] 세그먼트별 start/end 시간 추출
  - [ ] SRT 형식 타임스탬프 변환 (00:00:00,000)

### 2.3 LLM 엔진 (llm_engine.py)
- [ ] Claude API 연동
  - [ ] anthropic SDK 사용
  - [ ] API Key 환경 변수 또는 keyring 연동
- [ ] 프롬프트 로딩 및 처리
  - [ ] `correction.txt` 파일 읽기
  - [ ] `glossary.json` 파일 파싱
- [ ] 배치 교정 로직 구현
  - [ ] JSON 배열 형식 입력/출력
  - [ ] 세그먼트 개수 및 타임스탬프 무결성 검증
  - [ ] Code-Switching 교정 ("Ready 됬어" → "준비 됐어")
- [ ] 에러 핸들링 및 재시도 로직
  - [ ] API 호출 실패 시 재시도
  - [ ] Rate limit 처리

### 2.4 유틸리티 (utils/)
- [ ] `resource_resolver.py` 작성
  - [ ] `sys._MEIPASS` 기반 리소스 경로 해석
  - [ ] 개발 모드와 배포 모드 경로 자동 전환
- [ ] `port_finder.py` 작성
  - [ ] `find_free_port(start=8501, end=8510)` 구현
  - [ ] 포트 충돌 방지
- [ ] `logger.py` 작성
  - [ ] structlog 설정 (JSON 형식)
  - [ ] 파일 로그 및 콘솔 로그 분리

### 2.5 SRT 파일 생성
- [ ] SRT 포맷 생성 함수 구현
  - [ ] 세그먼트 번호, 타임스탬프, 텍스트 형식화
  - [ ] UTF-8 인코딩 저장
- [ ] 출력 파일명 생성 로직
  - [ ] `{source_name}_{timestamp}.srt` 패턴
  - [ ] 중복 방지

---

## Phase 3: GUI 개발 (Streamlit)

### 3.1 Streamlit 앱 기본 구조 (app.py)
- [ ] 페이지 설정 및 레이아웃
  - [ ] 페이지 타이틀: "AutoSub-AI"
  - [ ] 아이콘 및 레이아웃 설정
- [ ] 사이드바 구성
  - [ ] API Key 입력 필드 (keyring 연동)
  - [ ] 모델 설정 옵션 (device, model 선택)
  - [ ] 출력 경로 설정
  - [ ] 고급 설정 (chunk_size, workers 등)
- [ ] 메인 화면 구성
  - [ ] 파일 업로드 컴포넌트 (drag & drop)
  - [ ] 진행 상태 표시 (프로그레스 바)
  - [ ] 결과 미리보기 텍스트 영역
  - [ ] 다운로드 버튼

### 3.2 파일 업로드 및 검증
- [ ] 지원 포맷 검증 (mp4, mkv, avi, mov, webm)
- [ ] 파일 크기 제한 확인 (4GB)
- [ ] 업로드된 파일 임시 저장
- [ ] 에러 메시지 표시 (Streamlit toast/error)

### 3.3 처리 진행 상태 UI
- [ ] 실시간 진행률 표시
  - [ ] 오디오 추출 단계
  - [ ] STT 처리 단계 (세그먼트별)
  - [ ] LLM 교정 단계
  - [ ] SRT 파일 생성 단계
- [ ] 로그 메시지 스트리밍 (Streamlit expander)
- [ ] 중단 기능 구현 (작업 취소 버튼)

### 3.4 API Key 관리 UI
- [ ] keyring을 통한 API Key 저장/로드
- [ ] Fallback: `~/.autosub/.credentials` 파일 사용
- [ ] 유효성 검증 (테스트 API 호출)
- [ ] 보안 경고 메시지 표시

### 3.5 결과 화면 및 다운로드
- [ ] 생성된 자막 미리보기 (텍스트 영역)
- [ ] SRT 파일 다운로드 버튼
- [ ] 출력 폴더 열기 버튼 (OS 탐색기 연동)
- [ ] 성공 메시지 및 통계 표시 (처리 시간, 세그먼트 수)

### 3.6 Streamlit 테마 설정
- [ ] `.streamlit/config.toml` 작성
  - [ ] 다크 모드 설정
  - [ ] 브랜드 컬러 설정
  - [ ] 폰트 설정

---

## Phase 4: GUI 런처 및 시스템 통합

### 4.1 GUI 런처 (gui_launcher.py)
- [ ] Python 버전 체크 (3.10 이상)
- [ ] 리소스 경로 해석
  - [ ] `sys._MEIPASS` 로직 구현
  - [ ] FFmpeg, config, prompts 경로 자동 감지
- [ ] 동적 포트 할당
  - [ ] `find_free_port()` 호출
  - [ ] 포트 충돌 시 대체 포트 탐색
- [ ] Streamlit 서버 백그라운드 실행
  - [ ] `subprocess.Popen`으로 서버 구동
  - [ ] `--server.port`, `--server.headless` 옵션 적용
- [ ] 브라우저 자동 실행
  - [ ] `webbrowser.open(f"http://localhost:{port}")`
  - [ ] 서버 준비 완료 대기 로직 (health check)

### 4.2 시스템 트레이 아이콘 (pystray)
- [ ] 트레이 아이콘 생성
  - [ ] `assets/tray_icon.png` 로드
  - [ ] 아이콘 우클릭 메뉴 구성
- [ ] 메뉴 항목 기능 구현
  - [ ] "브라우저 열기" → 새 탭으로 localhost 열기
  - [ ] "로그 폴더 열기" → OS 탐색기로 `/logs/` 폴더 열기
  - [ ] "종료(Quit)" → 안전한 종료 프로세스 실행
- [ ] 트레이 아이콘 백그라운드 스레드 실행

### 4.3 프로세스 관리 및 종료 시나리오
- [ ] 자식 프로세스 추적 (psutil)
  - [ ] Streamlit 서버 프로세스 PID 관리
- [ ] 안전한 종료 로직
  - [ ] 작업 진행 중 경고 다이얼로그
  - [ ] 프로세스 Kill 및 임시 파일 정리
  - [ ] `/temp/` 폴더 자동 삭제
- [ ] 비정상 종료 시 복구 로직
  - [ ] 다음 실행 시 Orphaned Temp 폴더 감지
  - [ ] `error.log` 파일 생성 (crash dump)
- [ ] 브라우저 탭 닫기 시 대응
  - [ ] 서버는 백그라운드 유지
  - [ ] 트레이 아이콘으로 재접속 가능

### 4.4 첫 실행 시 초기화
- [ ] Whisper 모델 다운로드 체크
  - [ ] `./models/` 폴더 존재 확인
  - [ ] 없으면 다운로드 UI 표시
- [ ] API Key 입력 유도
  - [ ] keyring에서 체크
  - [ ] 없으면 사이드바 알림
- [ ] 설정 파일 생성
  - [ ] `custom_config.yaml` 생성 (사용자 설정)

---

## Phase 5: 패키징 및 배포

### 5.1 PyInstaller 설정 파일 (autosub.spec)
- [ ] `autosub.spec` 파일 작성
  - [ ] Entry Point: `gui_launcher.py`
  - [ ] `--add-binary`: `tools/ffmpeg.exe`
  - [ ] `--add-data`: config, prompts, gui 폴더
  - [ ] `hiddenimports` 명시 (streamlit, faster_whisper, keyring 등)
  - [ ] `console=False` (GUI 모드, 터미널 숨김)
  - [ ] `icon='assets/app.ico'`
- [ ] Streamlit Hook 파일 작성
  - [ ] `./hooks/hook-streamlit.py`
  - [ ] 누락되는 내부 모듈 명시

### 5.2 빌드 테스트
- [ ] 로컬 빌드 실행
  - [ ] `pyinstaller autosub.spec`
  - [ ] `/dist/AutoSub-AI.exe` 생성 확인
- [ ] UPX 압축 적용
  - [ ] `upx=True` 옵션 활성화
  - [ ] 파일 크기 최적화
- [ ] 빌드 크기 점검
  - [ ] Whisper 모델 제외 시 약 200MB 목표
  - [ ] 불필요한 의존성 제거

### 5.3 실행 파일 검증
- [ ] Windows Sandbox 환경에서 테스트
  - [ ] 깨끗한 Windows 10/11에서 실행
  - [ ] Python 미설치 환경 검증
- [ ] 첫 실행 시나리오 테스트
  - [ ] 모델 다운로드 정상 작동
  - [ ] API Key 입력 및 저장
  - [ ] 전체 파이프라인 실행
- [ ] 백신 오탐 테스트
  - [ ] Windows Defender 검사
  - [ ] VirusTotal 스캔

### 5.4 Splash Screen 추가 (옵션)
- [ ] `pyi-splash` 설정
  - [ ] 로딩 화면 이미지 준비
  - [ ] 압축 해제 중 표시
- [ ] 첫 실행 지연 사용자 경험 개선

### 5.5 Code Signing (옵션)
- [ ] Code Signing 인증서 취득 (필요 시)
- [ ] EXE 파일 서명
- [ ] 백신 오탐 확률 감소

---

## Phase 6: 테스트 및 품질 보증

### 6.1 Unit 테스트 (pytest)
- [ ] 테스트 환경 설정
  - [ ] `pytest`, `pytest-cov` 설치
  - [ ] `/tests/` 디렉토리 생성
- [ ] Core 로직 테스트
  - [ ] 타임스탬프 변환 함수
  - [ ] JSON 파싱 및 검증
  - [ ] SRT 포맷 생성
- [ ] 테스트 커버리지 80% 이상 목표

### 6.2 Integration 테스트
- [ ] 전체 파이프라인 테스트
  - [ ] 샘플 영상 → 오디오 추출 → STT → LLM → SRT
  - [ ] 타임스탬프 무결성 검증
  - [ ] 세그먼트 개수 일치 확인
- [ ] 에러 시나리오 테스트
  - [ ] 잘못된 포맷 입력
  - [ ] API 호출 실패
  - [ ] 디스크 용량 부족

### 6.3 GUI 테스트
- [ ] 수동 테스트 체크리스트
  - [ ] 파일 업로드/드래그 앤 드롭
  - [ ] 진행률 표시 정확성
  - [ ] 다운로드 버튼 동작
  - [ ] 설정 저장/로드
- [ ] Playwright 자동화 테스트 (옵션)
  - [ ] Streamlit 컴포넌트 동작 검증

### 6.4 호환성 테스트
- [ ] Windows 10 (21H2 이상)
- [ ] Windows 11
- [ ] VM 환경에서 테스트

### 6.5 성능 테스트
- [ ] 대용량 파일 처리 (2~4GB)
- [ ] 긴 영상 처리 (1시간 이상)
- [ ] 메모리 사용량 모니터링
- [ ] CPU/GPU 자원 활용 최적화

---

## Phase 7: 문서화 및 배포 준비

### 7.1 README.md 작성
- [ ] 프로젝트 소개
- [ ] 주요 기능 설명
- [ ] 설치 및 실행 가이드
  - [ ] 일반 사용자용
  - [ ] 개발자용
- [ ] 스크린샷/GIF 추가
- [ ] 라이선스 명시 (MIT)

### 7.2 사용자 가이드 문서
- [ ] 첫 실행 가이드
  - [ ] 모델 다운로드 안내
  - [ ] API Key 발급 및 입력 방법
- [ ] 트러블슈팅 섹션
  - [ ] 백신 오탐 해결 방법
  - [ ] 포트 충돌 해결
  - [ ] 일반적인 에러 메시지 설명

### 7.3 개발자 문서
- [ ] 아키텍처 다이어그램
- [ ] 주요 모듈 설명
- [ ] 빌드 가이드
  - [ ] 환경 설정
  - [ ] PyInstaller 빌드 명령어
- [ ] 기여 가이드 (CONTRIBUTING.md)

### 7.4 릴리스 준비
- [ ] 버전 정보 업데이트 (0.1.0)
- [ ] CHANGELOG.md 작성
- [ ] GitHub Release 생성
  - [ ] EXE 파일 업로드
  - [ ] 릴리스 노트 작성
- [ ] 배포 파일 체크섬 생성 (SHA256)

---

## Phase 8: 유지보수 및 개선

### 8.1 버그 수정
- [ ] GitHub Issues 모니터링
- [ ] 사용자 피드백 수집
- [ ] 핫픽스 배포 프로세스 수립

### 8.2 기능 개선
- [ ] 다국어 지원 (영어, 일본어 등)
- [ ] 다양한 LLM 엔진 지원 (GPT, Gemini)
- [ ] 배치 처리 (여러 파일 동시 처리)
- [ ] 자막 스타일 커스터마이징

### 8.3 성능 최적화
- [ ] 병렬 처리 개선
- [ ] 모델 경량화 옵션 (small, medium)
- [ ] 캐싱 전략 적용

---

## 🎯 마일스톤

- **M1 (Week 1-2)**: Phase 1-2 완료 (환경 설정 + Core 로직)
- **M2 (Week 3-4)**: Phase 3 완료 (GUI 개발)
- **M3 (Week 5)**: Phase 4-5 완료 (런처 + 패키징)
- **M4 (Week 6)**: Phase 6-7 완료 (테스트 + 문서화)
- **M5 (Week 7+)**: Phase 8 (유지보수 및 개선)

---

## 📊 진행 상황 추적

**전체 진행률**: 0%

- Phase 1: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 2: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 3: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 4: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 5: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 6: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 7: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
- Phase 8: ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%
