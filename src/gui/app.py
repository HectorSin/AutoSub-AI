import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow imports from src
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.resource_resolver import get_resource_path
from src.utils.gpu_setup import add_nvidia_dll_path
from src.core.audio_processor import AudioProcessor
from src.core.stt_engine import STTEngine
from src.core.llm_engine import LLMEngine
from src.core.srt_generator import SRTGenerator
import logging

from src.core.srt_generator import SRTGenerator
import logging
import keyring

logger = logging.getLogger(__name__)

SERVICE_NAME = "AutoSub-AI"
USERNAME = "gemini_api_key"

def load_api_key():
    try:
        return keyring.get_password(SERVICE_NAME, USERNAME)
    except Exception as e:
        logger.error(f"Keyring error: {e}")
        return None

def save_api_key(key):
    try:
        keyring.set_password(SERVICE_NAME, USERNAME, key)
        st.toast("API Key 저장 완료", icon="🔒")
    except Exception as e:
        st.error(f"API Key 저장 실패: {e}")

def main():
    # Setup GPU paths
    add_nvidia_dll_path()

    st.set_page_config(
        page_title="AutoSub-AI",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎬 AutoSub-AI")
    st.markdown("### 영상 파일에서 자막을 자동으로 생성하고 교정합니다.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API Key
        st.markdown("[🔑 Gemini API Key 발급받기](https://aistudio.google.com/app/apikey)")
        saved_key = load_api_key()
        api_key_input = st.text_input("Gemini API Key", value=saved_key if saved_key else "", type="password", help="Google Gemini API Key를 입력하세요.")
        
        if st.button("API Key 저장"):
            if api_key_input:
                save_api_key(api_key_input)
            else:
                st.warning("API Key를 입력하세요.")
        
        # Use the input value for processing
        api_key = api_key_input
        
        # Model Settings
        st.subheader("모델 설정")
        model_size = st.selectbox("Whisper 모델 크기", ["base", "small", "medium", "large-v3"], index=3)
        device = st.selectbox("디바이스", ["auto", "cuda", "cpu"], index=0)
        
        # Output Settings
        st.subheader("출력 설정")
        # Default output dir relative to project root or user home?
        # For portable app, maybe relative to exe or in Documents.
        default_output = str(project_root / "output")
        output_dir = st.text_input("출력 경로", value=default_output)
        
        # Advanced Settings
        with st.expander("고급 설정"):
            chunk_size = st.number_input("청크 크기 (초)", value=300, step=10)
            workers = st.number_input("작업자 수", value=4, min_value=1, max_value=16)

    # Main Content
    uploaded_file = st.file_uploader("영상 파일을 업로드하세요", type=["mp4", "mkv", "avi", "mov", "webm"])
    
    if uploaded_file:
        # Validate size (4GB limit)
        MAX_SIZE_MB = 4096
        if uploaded_file.size > MAX_SIZE_MB * 1024 * 1024:
            st.error(f"파일 크기가 너무 큽니다. (최대 {MAX_SIZE_MB}MB)")
            return

        # Save to temp
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.toast(f"파일 준비 완료: {uploaded_file.name}", icon="✅")
        except Exception as e:
            st.error(f"파일 저장 중 오류 발생: {e}")
            return
        
        if st.button("자막 생성 시작", type="primary"):
            if not api_key:
                st.error("API Key가 필요합니다.")
            else:
                st.success("작업을 시작합니다...")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 1. Audio Extraction
                    status_text.text("🔊 오디오 추출 중...")
                    audio_processor = AudioProcessor(temp_dir="temp")
                    audio_path = audio_processor.extract_audio(str(temp_path))
                    progress_bar.progress(10)
                    
                    # 2. STT
                    status_text.text("📝 STT 변환 중...")
                    stt_engine = STTEngine(model_size=model_size, device=device)
                    
                    def stt_progress(current, total):
                        # Map 10-50%
                        if total > 0:
                            progress = 10 + int((current / total) * 40)
                            progress_bar.progress(min(progress, 50))
                            status_text.text(f"📝 STT 변환 중... ({int(current)}s / {int(total)}s)")
                        
                    segments = stt_engine.transcribe(audio_path, progress_callback=stt_progress)
                    progress_bar.progress(50)
                    
                    # 3. LLM Correction
                    status_text.text("🤖 LLM 교정 중...")
                    llm_engine = LLMEngine(api_key=api_key)
                    
                    def llm_progress(current, total):
                        # Map 50-90%
                        if total > 0:
                            progress = 50 + int((current / total) * 40)
                            progress_bar.progress(min(progress, 90))
                            status_text.text(f"🤖 LLM 교정 중... ({current}/{total} 세그먼트)")
                        
                    corrected_segments = llm_engine.correct_subtitles(segments, progress_callback=llm_progress)
                    progress_bar.progress(90)
                    
                    # 4. SRT Generation
                    status_text.text("💾 SRT 파일 생성 중...")
                    output_path = SRTGenerator.generate_output_filename(str(temp_path), output_dir)
                    SRTGenerator.generate_srt(corrected_segments, output_path)
                    progress_bar.progress(100)
                    
                    status_text.text("✅ 완료!")
                    st.success(f"자막 생성 완료: {output_path}")
                    
                    # Show result
                    with open(output_path, "r", encoding="utf-8") as f:
                        srt_content = f.read()
                    
                    st.subheader("결과 미리보기")
                    st.text_area("자막 내용", value=srt_content, height=300)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="SRT 다운로드",
                                data=f,
                                file_name=Path(output_path).name,
                                mime="text/plain"
                            )
                    with col2:
                        if st.button("출력 폴더 열기"):
                            if sys.platform == "win32":
                                os.startfile(str(Path(output_path).parent))
                            else:
                                st.info(f"출력 폴더: {Path(output_path).parent}")

                except Exception as e:
                    st.error(f"작업 중 오류 발생: {e}")
                    logger.error(f"Processing error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
