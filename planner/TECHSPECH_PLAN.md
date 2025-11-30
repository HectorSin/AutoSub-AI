# TECHSPEC_PLAN.md

## 1. 프로젝트 개요 (Project Overview)
- **프로젝트명**: AutoSub-AI
- **버전**: 0.1.0 (Semantic Versioning)
- **목표**: 영상 파일을 입력받아 STT(음성 인식)와 LLM(Code-Switching 교정)을 통해 원어민 수준의 자연스러운 한국어 자막(SRT)을 생성한다.
- **타겟 사용자**:
    - **비개발자 콘텐츠 크리에이터**: Python이나 터미널을 모르는 유튜버, 영상 편집자.
    - **일반 사용자**: 설치 과정 없이 .exe 파일 더블 클릭만으로 프로그램을 사용하고 싶은 윈도우 사용자.
- **배포 형태**:
    - **Portable EXE**: 별도 설치 과정 없이 실행 가능한 단일 실행 파일.
    - **GUI 기반**: 웹 브라우저를 통해 직관적으로 조작하는 로컬 웹 앱.
- **핵심 가치**:
    - **Zero Setup**: 파이썬, FFmpeg 설치 불필요 (내장화).
    - **Context-Aware Correction**: "Ready 됬어" -> "준비 됐어" 맥락 의역.
    - **Time-Sync Integrity**: 타임스탬프 오차 없는 정교한 교정.

## 2. 시스템 아키텍처 (System Architecture)

### 2.1. Execution Flow (EXE)
```mermaid
flowchart LR
    User[User (Windows)] -- Double Click --> Launcher[Launcher.exe<br/>(PyInstaller)]
    Launcher -- Background Process --> Streamlit[Local Streamlit Server]
    Launcher -- Auto Open --> Browser[Default Web Browser<br/>localhost:8501]
    
    subgraph "Internal Logic (Embedded)"
        Streamlit --> FFmpeg[FFmpeg Binary]
        Streamlit --> Whisper[STT Engine]
        Streamlit --> LLM[LLM Engine]
    end
```

### 2.2. 기술 스택 및 의존성 (Tech Stack & Dependencies)
**requirements.txt 명세**:
```text
faster-whisper>=1.0.0
anthropic>=0.40.0
pydantic>=2.0.0
silero-vad>=5.0.0
structlog>=24.0.0
typer>=0.9.0
tqdm>=4.66.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
ffmpeg-python>=0.2.0
streamlit>=1.28.0
pyinstaller>=6.0.0
keyring>=24.0.0  # 시스템 자격 증명 저장소
pystray>=0.19.0  # 시스템 트레이 아이콘
pillow>=10.0.0   # 이미지 처리 (트레이 아이콘용)
psutil>=5.9.0    # 프로세스 관리 (종료 시 자식 프로세스 Kill)
```

- **GUI Framework**: Streamlit (브라우저 기반 GUI).
- **Packaging**: PyInstaller (단일 .exe 생성).
- **Launcher**: `gui_launcher.py` (Streamlit 서버 구동, 포트 관리, 트레이 아이콘).
- **Security**: keyring (API Key를 OS 보안 저장소에 암호화하여 저장).

## 3. 데이터 모델 및 설정 (Data Models & Configuration)

### 3.1. 설정 파일 스키마 (config.yaml)
EXE 실행 시 내부 리소스와 사용자 설정(`custom_config.yaml`)을 구분하여 관리.

```yaml
# config.yaml (Default embedded in EXE)
app:
  name: "AutoSub-AI"
  version: "0.1.0"

input:
  supported_formats: ["mp4", "mkv", "avi", "mov", "webm"]
  max_file_size_gb: 4

output:
  dir: "./output" # GUI에서 사용자가 변경 가능
  naming: "{source_name}_{timestamp}.srt"
  formats: ["srt"]

processing:
  chunk_size: 300
  overlap_size: 5
  max_workers: 2 
  temp_dir: "./temp"
  
stt:
  model: "large-v3"
  model_path: "./models"      # 모델 파일 저장 경로
  download_on_first_run: true # true: 첫 실행 시 다운로드, false: 번들 모델 사용
  device: "auto"
  language: "ko"

llm:
  provider: "claude"
  model_name: "claude-3-5-haiku-20241022"
  # EXE 내부 경로(_MEIPASS) 자동 참조
  prompt_path: "./src/prompts/correction.txt"
  glossary_path: "./src/prompts/glossary.json"

logging:
  level: "INFO"
  dir: "./logs"
  json_format: true
```

## 4. 핵심 기능 명세 (Core Logic Specifications)

### 4.1. EXE 구동 및 리소스 관리 (gui_launcher.py)
- **환경 점검**: Python 버전이 3.10 미만일 경우 경고 로그 출력 및 실행 차단 (개발 모드 시).
- **리소스 경로 해석**: `sys._MEIPASS`를 통해 PyInstaller 임시 폴더 내의 에셋 경로(이미지, 설정 파일, FFmpeg)를 올바르게 찾아낸다.
- **동적 포트 할당**: 기본 포트(8501)가 사용 중일 경우 `find_free_port(start=8501, end=8510)` 로직을 통해 가용 포트를 탐색한다.
- **서버/브라우저 연동**:
    1. 백그라운드에서 `streamlit run src/gui/app.py --server.port={port} --server.headless=true` 실행.
    2. `webbrowser.open(f"http://localhost:{port}")` 호출.
- **시스템 트레이 (System Tray)**:
    - `pystray`를 활용하여 트레이 아이콘 생성.
    - **기능**: "브라우저 열기", "로그 폴더 열기", "종료(Quit)".

### 4.2. 내장형 FFmpeg 처리
- **번들링 전략**: `ffmpeg.exe`를 PyInstaller의 `--add-binary` 옵션으로 포함시킨다.
- **경로 참조**: `audio_processor.py`에서 `sys._MEIPASS` 하위의 `tools/ffmpeg.exe` 경로를 감지하여 사용.

### 4.3. Whisper 모델 관리 전략
- **옵션 A (기본): On-Demand Download**
    - EXE 용량을 가볍게 유지(약 200MB).
    - 첫 실행 시 또는 설정 메뉴에서 모델(large-v3, 약 3GB) 다운로드 진행. `tqdm`으로 다운로드 UI 제공.
- **옵션 B: Bundled Model**
    - EXE 용량이 매우 커짐(3GB+). 오프라인 환경 필수 시에만 고려.
    - PyInstaller `datas` 옵션에 모델 폴더 포함.

### 4.4. API Key 보안 및 관리
- **저장 방식**: `keyring` 라이브러리를 사용하여 OS의 자격 증명 관리자(Windows Credential Manager, macOS Keychain)에 저장.
- **Fallback**: Keyring 사용 불가 환경일 경우, 사용자 홈 디렉토리의 `~/.autosub/.credentials` 파일에 난독화하여 저장.
- **GUI 동작**: 앱 시작 시 Keyring을 확인하고, 없으면 설정 사이드바에서 입력 요청.

### 4.5. 에러 핸들링 (EXE 특화)
- **Console Hidden**: EXE 실행 시 콘솔 창(검은 화면)이 뜨지 않도록 설정 (`--noconsole`).
- **Crash Log**: 프로그램 비정상 종료 시, 실행 파일과 같은 위치에 `error.log` 파일 생성. 일반적인 런타임 로그는 `./logs/` 디렉토리에 저장.

### 4.6. 종료 시나리오 (Shutdown Handling)
`psutil`을 활용하여 자식 프로세스까지 깔끔하게 종료하는 것이 핵심.

| 상황 | 동작 |
| --- | --- |
| **트레이 → "종료"** | Launcher 및 Streamlit 자식 프로세스 전체 Kill + `./temp` 폴더 정리 |
| **브라우저 탭 닫기** | 서버는 백그라운드 유지 (트레이 아이콘으로 다시 열기 가능) |
| **작업 진행 중 종료** | 경고 다이얼로그 표시 (Streamlit UI) 후 강제 종료 시 `[INTERRUPTED]` 로그 기록 |
| **비정상 종료/크래시** | 다음 실행 시 Orphaned Temp 폴더 자동 감지 및 삭제 |

## 5. 프로젝트 구조 및 파일 명세 (Project Structure)

### 5.1. 디렉토리 트리
```text
/project_root
├── /assets                  # 아이콘(.ico), 트레이 아이콘(.png)
├── /src
│   ├── /core                # 핵심 비즈니스 로직
│   │   ├── audio_processor.py
│   │   ├── stt_engine.py    # 모델 다운로드 로직 포함
│   │   └── llm_engine.py
│   ├── /gui                 # GUI 코드
│   │   └── app.py           # Streamlit 메인 앱
│   ├── /prompts             # 프롬프트 리소스
│   │   ├── correction.txt
│   │   └── glossary.json
│   └── /utils               # 리소스 경로 리졸버, 포트 탐색기
├── /tools
│   └── ffmpeg.exe           # 번들링용 윈도우 바이너리
├── /models                  # (Optional) 사전 다운로드된 모델
├── /logs                    # 런타임 로그 저장소
├── config.yaml              # 기본 설정
├── .env.example             # 참고용
├── gui_launcher.py          # [Entry Point] 트레이 아이콘 및 서버 구동
├── autosub.spec             # PyInstaller 빌드 설정 파일
├── requirements.txt         # 의존성 목록
└── README.md
```

### 5.2. 주요 파일 예시

**README.md**
```markdown
# AutoSub-AI

비개발자를 위한 AI 기반 자동 한글 자막 생성기 (Windows).

## 주요 기능
- 영상 드래그 앤 드롭으로 SRT 자막 자동 생성
- "Ready 됬어" -> "준비 됐어"와 같은 Code-Switching 자연스러운 교정
- FFmpeg 및 Python 설치 불필요 (단일 EXE)

## 설치 및 실행
1. `AutoSub-AI.exe`를 다운로드하여 실행합니다.
2. 시스템 트레이에 아이콘이 나타나고 웹 브라우저가 자동으로 열립니다.
3. 최초 실행 시 사이드바 설정에서 API Key를 입력하세요.

## 라이선스
MIT License
```

**.env.example**
```ini
# 로컬 개발용 (.env 파일 생성 시 사용)
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**src/prompts/correction.txt**
```text
당신은 한국어 자막 교정 전문가입니다.

## 규칙
1. 입력 JSON 배열의 세그먼트 개수를 절대 변경하지 마세요.
2. start, end 타임스탬프는 수정하지 마세요.
3. 영어-한국어 혼용을 자연스러운 한국어로 의역하세요.
   예: "Ready 됬어" → "준비 됐어"
4. 맞춤법 오류를 교정하세요.
5. glossary의 단어는 그대로 유지하세요.

## 출력
입력과 동일한 JSON 배열 구조로만 응답하세요.
```

**src/prompts/glossary.json**
```json
{
  "preserve": ["YouTube", "API", "ChatGPT", "Claude"],
  "replacements": { "레디": "준비" }
}
```

**.gitignore**
```text
.env
/temp/
/output/
/models/  # 모델 파일은 용량이 크므로 git 제외
/logs/
__pycache__/
*.pyc
/dist/
/build/
*.spec
```

## 6. 배포 및 패키징 전략 (Deployment Strategy)

### 6.1. PyInstaller 빌드 명세 (autosub.spec)
```python
# autosub.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[('tools/ffmpeg.exe', 'tools')],
    datas=[
        ('config.yaml', '.'),
        ('src/prompts/*', 'src/prompts'),
        ('src/gui/*', 'src/gui'),
        # Streamlit config (테마 등)
        ('.streamlit/config.toml', '.streamlit') 
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.runtime.scriptrunner',
        'faster_whisper',
        'anthropic',
        'pystray',
        'PIL',
        'keyring.backends.Windows', # 윈도우용 백엔드 명시
        'psutil'
    ],
    hookspath=['./hooks'],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoSub-AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # GUI 모드 (터미널 숨김)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico'
)
```

### 6.2. 패키징 리스크 및 대안 (Risks & Alternatives)
| 리스크 항목 | 설명 | 대응 전략 |
| --- | --- | --- |
| **번들 크기** | Streamlit + 의존성 포함 시 2~4GB 육박 가능 | Whisper 모델을 제외하고 배포(On-demand Download). UPX 압축 사용. |
| **첫 실행 지연** | 임시 폴더 압축 해제로 30초~1분 소요 가능 | Splash Screen 추가 (pyi-splash)로 사용자 이탈 방지. |
| **백신 오탐** | 서명 없는 EXE를 바이러스로 오진 | 가능한 경우 Code Signing 인증서 적용. 대안으로 예외 처리 가이드 제공. |
| **Hidden Imports** | Streamlit 내부 의존성 누락으로 실행 불가 | `.spec` 파일의 `hiddenimports` 지속적 업데이트 및 hook 파일 작성. |

### 6.3. 대안 배포 방식 (Fallback)
만약 단일 EXE 패키징 실패 시 다음 방식을 고려한다.
- **Portable ZIP**: Python Embeddable Package를 활용하여 설치 없이 압축만 풀면 실행되는 폴더 형태 배포.
- **NSIS Installer**: 단일 EXE 대신 설치 관리자(Installer)를 사용하여 파일을 Program Files에 풀고 바로가기를 생성하는 방식. (백신 오탐 확률 낮음).

## 7. 개발 로드맵 (Development Roadmap)

### Phase 1: Core & CLI (Foundation)
- [ ] FFmpeg, Faster-Whisper, Claude API 연동 핵심 로직 구현.
- [ ] CLI(`main.py`)를 통해 기본 기능 검증.

### Phase 2: GUI Development (User Interface)
- [ ] `src/gui/app.py` 개발: 파일 업로드, 진행률 표시 UI.
- [ ] `gui_launcher.py`: 포트 탐색 및 트레이 아이콘 로직 구현.
- [ ] API Key 보안: keyring 연동 및 설정 UI 구현.

### Phase 3: Packaging & Optimization
- [ ] `autosub.spec` 작성 및 PyInstaller 빌드 테스트.
- [ ] 모델 다운로드 로직: 첫 실행 시 다운로드 UI 구현.
- [ ] Windows Sandbox 환경에서 실행 및 백신 탐지 테스트.

## 8. 설치 및 시작 가이드 (Quick Start)

### 개발자 (Developer)
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. GUI 런처 실행 (소스코드)
python gui_launcher.py
```

### 일반 사용자 (End User)
1. **다운로드**: `AutoSub-AI.exe` 파일을 받습니다.
2. **실행**: 파일을 더블 클릭합니다.
3. **첫 실행 시** Whisper 모델 다운로드로 몇 분 소요될 수 있습니다.
4. **설정**: 사이드바에서 API Key를 입력합니다 (최초 1회).
5. **사용**: 영상 파일을 드래그하여 자막을 생성합니다.
6. **종료**: 시스템 트레이 아이콘 우클릭 → "종료"

## 9. 테스트 전략 (Test Strategy)
| 유형 | 도구 | 대상 |
| --- | --- | --- |
| **Unit** | pytest | Core 로직 (시간 변환, JSON 파싱) |
| **Integration** | pytest | 파이프라인 전체 흐름 |
| **GUI** | 수동 + Playwright | Streamlit 컴포넌트 |
| **Packaging** | Windows Sandbox | EXE 빌드 검증 |
| **Compatibility** | VM | Windows 10/11 호환성 |