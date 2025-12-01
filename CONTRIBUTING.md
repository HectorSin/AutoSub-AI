# 기여 가이드 (Contributing Guide)

AutoSub-AI 프로젝트에 관심을 가져주셔서 감사합니다! 여러분의 기여는 프로젝트를 더 발전시키는 데 큰 도움이 됩니다.

## 🛠️ 개발 환경 설정

1. **Fork** 이 저장소를 자신의 계정으로 Fork 합니다.
2. **Clone** Fork한 저장소를 로컬에 클론합니다.
   ```bash
   git clone https://github.com/YOUR_USERNAME/AutoSub-AI.git
   cd AutoSub-AI
   ```
3. **가상환경 설정** Python 3.10 이상 환경을 권장합니다.
   ```bash
   conda create -n autosub python=3.10
   conda activate autosub
   pip install -r requirements.txt
   ```
4. **Pre-commit 설정** (선택 사항)
   코드 스타일 일관성을 위해 pre-commit을 사용하는 것이 좋습니다.

## 🧪 테스트

코드를 수정하거나 새로운 기능을 추가한 후에는 반드시 테스트를 수행해주세요.

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_pipeline.py
```

## 📮 Pull Request (PR) 제출

1. 새로운 브랜치를 생성하여 작업합니다. (`git checkout -b feature/amazing-feature`)
2. 변경 사항을 커밋합니다. (`git commit -m 'Add some amazing feature'`)
3. 원격 저장소에 푸시합니다. (`git push origin feature/amazing-feature`)
4. GitHub에서 Pull Request를 생성합니다.
5. PR 내용에는 변경 사항에 대한 명확한 설명과 테스트 결과를 포함해주세요.

## 🐛 버그 신고

버그를 발견하셨다면 GitHub Issues에 다음 정보를 포함하여 제보해주세요:
- 사용 중인 OS 및 버전
- 발생한 에러 메시지 (로그 파일 첨부 권장)
- 재현 방법

## 💡 기능 제안

새로운 기능 아이디어가 있다면 언제든지 Issues에 제안해주세요!
