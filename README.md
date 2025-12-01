# AutoSub-AI 🎬

**AutoSub-AI**는 영상 파일에서 자동으로 오디오를 추출하고, Whisper AI로 음성을 인식(STT)한 뒤, Google Gemini (LLM)를 사용하여 자연스러운 한국어 자막(SRT)을 생성하는 도구입니다.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-orange)

## ✨ 주요 기능

- **자동 자막 생성**: 영상 파일을 드래그 앤 드롭하면 자동으로 자막을 생성합니다.
- **고성능 STT**: `faster-whisper`를 사용하여 빠르고 정확한 음성 인식을 제공합니다.
- **AI 자막 교정**: Google Gemini를 활용하여 오타 수정, 문맥 교정, 자연스러운 의역을 수행합니다.
- **GUI 인터페이스**: Streamlit 기반의 직관적인 웹 인터페이스를 제공합니다.
- **시스템 트레이 지원**: 백그라운드에서 실행되며 트레이 아이콘을 통해 제어할 수 있습니다.
- **휴대용 실행**: 설치가 필요 없는 Portable EXE 형태로 배포됩니다.

## 🚀 설치 및 실행

### 일반 사용자 (Windows)

1. [Releases](https://github.com/HectorSin/AutoSub-AI/releases) 페이지에서 최신 `AutoSub-AI.exe` 파일을 다운로드합니다.
2. 다운로드한 파일을 실행합니다. (첫 실행 시 모델 다운로드로 인해 시간이 소요될 수 있습니다.)
3. 시스템 트레이에 아이콘이 나타나고, 브라우저가 자동으로 열립니다.
4. **설정** 사이드바에서 **Gemini API Key**를 입력하고 저장합니다.
5. 영상 파일을 업로드하고 **자막 생성 시작** 버튼을 클릭합니다.

### 개발자 (소스 코드 실행)

**요구 사항**
- Python 3.10 이상
- FFmpeg (시스템 PATH에 등록되어 있거나 `tools/` 폴더에 배치)
- Google Gemini API Key

**설치**

```bash
# 저장소 클론
git clone https://github.com/HectorSin/AutoSub-AI.git
cd AutoSub-AI

# 가상환경 생성 (권장)
conda create -n autosub python=3.10
conda activate autosub

# 의존성 설치
pip install -r requirements.txt
```

**실행**

```bash
python src/gui_launcher.py
```

**패키징**

```bash
python -m PyInstaller autosub.spec --clean --noconfirm
```

**에러해결**

```bash
taskkill /F /IM AutoSub-AI.exe
```

## 🛠️ 기술 스택

- **Core**: Python
- **GUI**: Streamlit
- **STT**: Faster-Whisper (OpenAI Whisper)
- **LLM**: Google Gemini (via `google-generativeai`)
- **Packaging**: PyInstaller
- **System Integration**: Pystray, Keyring

## 📝 사용 방법

1. **API Key 설정**: 왼쪽 사이드바에서 Gemini API Key를 입력하고 '저장'을 누릅니다. (최초 1회)
2. **모델 선택**: Whisper 모델 크기(base, small, medium, large-v3)를 선택합니다. GPU가 있다면 `cuda`, 없다면 `cpu`를 선택합니다.
3. **파일 업로드**: 메인 화면에 영상 파일(mp4, mkv, avi 등)을 드래그합니다.
4. **생성 시작**: 버튼을 누르면 오디오 추출 -> STT -> LLM 교정 -> SRT 생성 과정이 자동으로 진행됩니다.
5. **다운로드**: 완료되면 생성된 자막을 미리보고 다운로드할 수 있습니다.

## ❓ 트러블슈팅

### CUDA 관련 오류 (Could not locate cudnn_ops64_9.dll)
NVIDIA GPU를 사용하는 경우, 필요한 라이브러리가 누락되었을 수 있습니다. 다음 명령어로 설치해주세요:
```bash
pip install nvidia-cudnn-cu12 nvidia-cublas-cu12
```

### 백신 오탐 (Virus Detected)
PyInstaller로 패키징된 실행 파일은 서명되지 않아 백신이 오탐할 수 있습니다. 예외 처리를 하거나 소스 코드를 직접 실행해주세요.

## 🤝 기여하기

기여는 언제나 환영합니다! 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고해주세요.

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
