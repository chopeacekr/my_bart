 # 🐶 Bark TTS Server

> **표현력 넘치는 감정 음성 합성 서버**  
> Suno AI의 Bark 모델을 사용한 다국어 TTS 서버

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)

---

## 📋 목차

- [특징](#-특징)
- [빠른 시작](#-빠른-시작)
- [설치](#-설치)
- [사용법](#-사용법)
- [API 문서](#-api-문서)
- [특수 토큰](#-특수-토큰)
- [화자 프리셋](#-화자-프리셋)
- [성능](#-성능)
- [문제 해결](#-문제-해결)
- [라이선스](#-라이선스)

---

## ✨ 특징

### 🎭 표현력의 왕
- **감정 표현**: [laughs], [sighs], [cries], [gasps]
- **음악 생성**: [music] 토큰으로 노래/배경음악
- **효과음**: [applause], [gasps] 등
- **100+ 화자 프리셋**: 다양한 목소리 선택

### 🌍 다국어 지원
13개 언어 지원:
- 한국어 (KR) 🇰🇷
- 영어 (EN) 🇺🇸
- 일본어 (JP) 🇯🇵
- 중국어 (ZH) 🇨🇳
- 프랑스어 (FR) 🇫🇷
- 독일어 (DE) 🇩🇪
- 스페인어 (ES) 🇪🇸
- 이탈리아어 (IT) 🇮🇹
- 포르투갈어 (PT) 🇵🇹
- 폴란드어 (PL) 🇵🇱
- 터키어 (TR) 🇹🇷
- 러시아어 (RU) 🇷🇺
- 힌디어 (HI) 🇮🇳

### 🚀 FastAPI 기반
- RESTful API
- 자동 문서화 (Swagger UI)
- CORS 지원
- Health check 엔드포인트

---

## ⚡ 빠른 시작

### 1. 설치

```bash
# 저장소 클론 또는 파일 복사
cd my_bark

# 의존성 설치 (uv 사용)
uv sync

# 또는 pip 사용
pip install fastapi uvicorn[standard] torch torchaudio transformers \
    accelerate scipy numpy soundfile python-multipart psutil
```

### 2. 서버 시작

```bash
uv run python server_tts.py

# 또는 직접 실행
python server_tts.py
```

**서버 주소**: http://localhost:8600

### 3. 테스트

```bash
# Health check
curl http://localhost:8600/health

# TTS 생성
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요!" \
  -o output.wav
```

---

## 📦 설치

### 요구사항

- Python 3.10 이상
- 8GB+ RAM (CPU 사용 시)
- 2GB+ 디스크 공간 (모델 캐시)

### 방법 1: uv 사용 (권장)

```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 설정
cd my_bark
uv sync

# 서버 실행
uv run python server_tts.py
```

### 방법 2: venv + pip

```bash
# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install fastapi uvicorn[standard] torch torchaudio transformers \
    accelerate scipy numpy soundfile python-multipart psutil

# 서버 실행
python server_tts.py
```

---

## 🎯 사용법

### Python에서 사용

```python
import requests

# TTS 생성
response = requests.post(
    "http://localhost:8600/synthesize",
    data={
        "text": "안녕하세요! [laughs]",
        "voice_preset": "v2/ko_speaker_0",
        "speed": 1.0
    }
)

# 오디오 저장
with open("output.wav", "wb") as f:
    f.write(response.content)

print("✅ 음성 생성 완료!")
```

### cURL에서 사용

```bash
# 기본 사용
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요!" \
  -o output.wav

# 감정 표현
curl -X POST http://localhost:8600/synthesize \
  -F "text=정말 기뻐요! [laughs]" \
  -o laugh.wav

# 화자 선택
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요" \
  -F "voice_preset=v2/ko_speaker_1" \
  -o voice1.wav

# 속도 조절
curl -X POST http://localhost:8600/synthesize \
  -F "text=빠르게 말합니다" \
  -F "speed=1.5" \
  -o fast.wav
```

### JavaScript에서 사용

```javascript
const formData = new FormData();
formData.append('text', '안녕하세요! [laughs]');
formData.append('voice_preset', 'v2/ko_speaker_0');
formData.append('speed', '1.0');

fetch('http://localhost:8600/synthesize', {
  method: 'POST',
  body: formData
})
.then(response => response.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
});
```

---

## 📚 API 문서

### Swagger UI

서버 실행 후 브라우저에서 접속:
- **Swagger UI**: http://localhost:8600/docs
- **ReDoc**: http://localhost:8600/redoc

### 엔드포인트

#### 1. Health Check

```http
GET /health
```

**응답:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cpu",
  "sample_rate": 24000
}
```

#### 2. TTS 생성

```http
POST /synthesize
```

**파라미터:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `text` | string | ✅ | - | 생성할 텍스트 |
| `voice_preset` | string | ❌ | null | 화자 프리셋 (예: v2/ko_speaker_0) |
| `speed` | float | ❌ | 1.0 | 음성 속도 (0.5 ~ 2.0) |

**응답:**
- Content-Type: `audio/wav`
- 샘플레이트: 24000 Hz
- 채널: 모노

**예시:**

```bash
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요" \
  -F "voice_preset=v2/ko_speaker_0" \
  -F "speed=1.2" \
  -o output.wav
```

---

## 🎭 특수 토큰

Bark는 텍스트에 특수 토큰을 포함하여 비언어적 표현을 생성할 수 있습니다.

### 감정 표현

| 토큰 | 효과 | 예시 |
|------|------|------|
| `[laughs]` | 웃음 😄 | "정말 재밌어요! [laughs]" |
| `[sighs]` | 한숨 😔 | "힘드네요... [sighs]" |
| `[cries]` | 울음 😢 | "너무 슬퍼요 [cries]" |
| `[gasps]` | 헐떡임 😲 | "와! [gasps] 놀라워요!" |

### 효과음

| 토큰 | 효과 | 예시 |
|------|------|------|
| `[music]` | 음악/노래 🎵 | "생일 축하합니다! ♪ [music]" |
| `[applause]` | 박수 👏 | "축하해요! [applause]" |

### 사용 예시

```python
# 감정 표현
texts = [
    "정말 기뻐요! [laughs]",
    "오늘은 힘드네요... [sighs]",
    "너무 슬퍼요 [cries]",
    "와! [gasps] 대단해요!"
]

# 음악/효과음
texts = [
    "생일 축하합니다! ♪ [music]",
    "축하합니다! [applause]"
]

for text in texts:
    response = requests.post(
        "http://localhost:8600/synthesize",
        data={"text": text}
    )
    # 오디오 저장...
```

---

## 👥 화자 프리셋

Bark는 100개 이상의 사전 정의된 화자 프리셋을 제공합니다.

### 한국어 화자

| 프리셋 | 설명 | 특징 |
|--------|------|------|
| `v2/ko_speaker_0` | 한국어 남성 1 | 중저음 |
| `v2/ko_speaker_1` | 한국어 여성 1 | 부드러운 목소리 |
| `v2/ko_speaker_2` | 한국어 남성 2 | 낮은 목소리 |
| `v2/ko_speaker_3` | 한국어 여성 2 | 밝은 목소리 |
| `v2/ko_speaker_4` | 한국어 남성 3 | 차분한 목소리 |
| `v2/ko_speaker_5` | 한국어 여성 3 | 활기찬 목소리 |

### 영어 화자

| 프리셋 | 설명 |
|--------|------|
| `v2/en_speaker_0` | 영어 남성 1 |
| `v2/en_speaker_1` | 영어 여성 1 |
| `v2/en_speaker_2` | 영어 남성 2 |
| `v2/en_speaker_3` | 영어 여성 2 |
| `v2/en_speaker_4` | 영어 남성 3 |
| `v2/en_speaker_5` | 영어 여성 3 |
| `v2/en_speaker_6` | 영어 남성 4 |
| `v2/en_speaker_7` | 영어 여성 4 |
| `v2/en_speaker_8` | 영어 남성 5 |
| `v2/en_speaker_9` | 영어 여성 5 |

### 중국어 화자

| 프리셋 | 설명 |
|--------|------|
| `v2/zh_speaker_0` | 중국어 남성 1 |
| `v2/zh_speaker_1` | 중국어 여성 1 |
| `v2/zh_speaker_2` | 중국어 남성 2 |
| `v2/zh_speaker_3` | 중국어 여성 2 |

### 사용 예시

```bash
# 한국어 남성 목소리
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요" \
  -F "voice_preset=v2/ko_speaker_0" \
  -o male.wav

# 한국어 여성 목소리
curl -X POST http://localhost:8600/synthesize \
  -F "text=안녕하세요" \
  -F "voice_preset=v2/ko_speaker_1" \
  -o female.wav
```

**💡 Tip**: `voice_preset`을 생략하면 자동으로 언어에 맞는 기본 화자가 선택됩니다.

---

## ⚡ 성능

### 처리 속도 (실측)

| 환경 | 모델 | 텍스트 | 처리 시간 | 비고 |
|------|------|--------|-----------|------|
| CPU (i7) | bark-small | "Suno AI의 오픈소스..." | **103초** | 실제 테스트 |
| CPU (i7) | bark-small | 2초 음성 | 2.5초 | 한경희님 보고서 |
| GPU (RTX 3090) | bark | 짧은 문장 | 5-10초 | 예상 |
| GPU (RTX 3090) | bark | 긴 문장 | 10-20초 | 예상 |

### 다른 TTS 모델과 비교

| 모델 | 처리 시간 | 속도 비율 | 특징 |
|------|-----------|-----------|------|
| **MeloTTS** | 1-2초 | 기준 (가장 빠름) | 실시간 처리 |
| **XTTS v2** | 5-10초 | 5-10배 느림 | Voice Cloning |
| **F5-TTS** | 10-20초 | 10-20배 느림 | 최고 품질 |
| **Bark** | **103초** | **50-100배 느림** ⚠️ | 감정 표현 |

### 리소스 요구사항

#### 최소 사양 (bark-small, CPU)
- **CPU**: Intel Core i7 이상 (4코어)
- **RAM**: 8GB
- **저장공간**: 2GB (모델 캐시)
- **처리 속도**: 짧은 텍스트 → 103초

#### 권장 사양 (bark, GPU)
- **GPU**: NVIDIA RTX 3090 (12GB VRAM)
- **CPU**: 8코어 이상
- **RAM**: 16GB
- **저장공간**: 3GB
- **처리 속도**: 짧은 텍스트 → 5-10초

### 사용 권장 사항

#### ✅ Bark가 최적인 경우
- 감정 표현이 중요한 콘텐츠 (오디오북, 스토리텔링)
- 음악/효과음 생성
- 배치 처리 (시간 여유 있는 작업)
- 품질 > 속도인 프로젝트

#### ❌ Bark가 부적합한 경우
- 실시간 대화형 애플리케이션 → **MeloTTS 권장** (1-2초)
- 빠른 응답 챗봇 → **MeloTTS/Google TTS**
- 대량 음성 생성 → **MeloTTS** (50-100배 빠름)
- 시간 제약이 엄격한 작업

### 최적화 팁

#### 1. GPU 사용 (10-20배 빠름!)

```bash
# CUDA 설치 확인
nvidia-smi

# PyTorch GPU 버전 설치
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 2. 모델 선택

```python
# CPU 환경 → bark-small (빠름, 품질 양호)
from transformers import BarkModel
model = BarkModel.from_pretrained("suno/bark-small")

# GPU 환경 → bark (느림, 품질 최고)
model = BarkModel.from_pretrained("suno/bark")
```

#### 3. 배치 처리

```python
# ❌ 긴 텍스트 한 번에 처리 (매우 느림)
long_text = "..." * 100
bark_tts(long_text)  # 10분 이상 소요

# ✅ 문장 단위로 분할 (권장)
sentences = long_text.split('. ')
for sentence in sentences:
    bark_tts(sentence)  # 각 100초, 병렬 가능
```

---

## 🐛 문제 해결

### 1. 서버가 시작되지 않음

**증상:**
```
ModuleNotFoundError: No module named 'transformers'
```

**해결:**
```bash
# 의존성 재설치
pip install --upgrade pip
pip install fastapi uvicorn[standard] torch torchaudio transformers \
    accelerate scipy numpy soundfile python-multipart psutil

# 또는 uv 사용
uv sync
```

### 2. 모델 다운로드 실패

**증상:**
```
HTTPError: 403 Forbidden
```

**해결:**
```bash
# Hugging Face 캐시 삭제
rm -rf ~/.cache/huggingface

# 수동 다운로드
python -c "from transformers import AutoProcessor, BarkModel; \
    AutoProcessor.from_pretrained('suno/bark-small'); \
    BarkModel.from_pretrained('suno/bark-small')"
```

### 3. 메모리 부족

**증상:**
```
RuntimeError: CUDA out of memory
```

**해결:**
```python
# bark-small 사용
model = BarkModel.from_pretrained("suno/bark-small")

# 또는 CPU 모드
device = "cpu"
model = model.to(device)
```

### 4. 처리 속도가 매우 느림 (103초+)

**원인:**
- CPU 사용
- bark (Large) 모델
- 긴 텍스트

**해결:**
```bash
# 1. GPU 사용 (10-20배 빠름!)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# 2. bark-small 사용
# server_tts.py에서 모델 변경

# 3. 텍스트 분할
# 긴 텍스트는 문장 단위로 분할
```

**💡 참고**: Bark는 본질적으로 느린 모델입니다. 표현력과 속도의 트레이드오프입니다.

### 5. 경고 메시지

**증상:**
```
The attention mask and the pad token id were not set.
```

**설명:**
- Bark의 정상적인 동작
- 무시 가능한 경고
- 품질에 영향 없음

**해결 (이미 적용됨):**
```python
# server_tts.py v1.0.2에 이미 적용됨
import warnings
warnings.filterwarnings("ignore", message=".*attention mask.*")
```

### 6. torchaudio 에러

**증상:**
```
ImportError: TorchCodec is required for save_with_torchcodec.
```

**해결 (이미 적용됨):**
```python
# server_tts.py v1.0.2에서 scipy.io.wavfile.write 사용
import scipy.io.wavfile as wavfile
wavfile.write(temp_wav_path, sample_rate, audio_int16)
```

### 7. 포트 충돌

**증상:**
```
OSError: [Errno 48] Address already in use
```

**해결:**
```bash
# 포트 사용 프로세스 확인
lsof -i :8600

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
# server_tts.py 수정: uvicorn.run(..., port=8601)
```

---

## 📖 참고 자료

### 공식 문서
- [Bark GitHub](https://github.com/suno-ai/bark)
- [Bark Hugging Face](https://huggingface.co/suno/bark)
- [Transformers 문서](https://huggingface.co/docs/transformers)

### 관련 프로젝트
- [MeloTTS](https://github.com/myshell-ai/MeloTTS) - 빠른 다국어 TTS
- [XTTS v2](https://github.com/coqui-ai/TTS) - Voice Cloning
- [F5-TTS](https://github.com/SWivid/F5-TTS) - Zero-shot TTS

### 조사 보고서
- **한경희님 Bark TTS 조사 보고서**
  - CPU 환경 실행 (i7, 32GB RAM)
  - bark-small 성공 테스트
  - 3가지 오류 해결 방법
  - 오디오 시각화 (Waveform + Spectrogram)

---

## 🎯 사용 시나리오

### 시나리오 1: 오디오북 제작

```python
# 감정 표현이 풍부한 오디오북
chapters = [
    "옛날 옛적에... [music]",
    "주인공은 놀라서 [gasps] 뒤를 돌아봤습니다.",
    "그리고 웃음을 터뜨렸어요. [laughs]",
    "하지만 곧 슬픔에 잠겼죠... [sighs]"
]

for i, text in enumerate(chapters):
    response = requests.post(
        "http://localhost:8600/synthesize",
        data={"text": text, "voice_preset": "v2/ko_speaker_0"}
    )
    with open(f"chapter_{i}.wav", "wb") as f:
        f.write(response.content)
```

### 시나리오 2: 다국어 콘텐츠

```python
# 여러 언어로 동일 메시지
messages = {
    "ko": ("안녕하세요!", "v2/ko_speaker_0"),
    "en": ("Hello!", "v2/en_speaker_0"),
    "ja": ("こんにちは!", "v2/ja_speaker_0"),
    "zh": ("你好!", "v2/zh_speaker_0")
}

for lang, (text, preset) in messages.items():
    response = requests.post(
        "http://localhost:8600/synthesize",
        data={"text": text, "voice_preset": preset}
    )
    with open(f"greeting_{lang}.wav", "wb") as f:
        f.write(response.content)
```

### 시나리오 3: 배치 처리

```bash
# 대량 텍스트 파일 처리
for file in texts/*.txt; do
    text=$(cat "$file")
    curl -X POST http://localhost:8600/synthesize \
      -F "text=$text" \
      -o "audio/$(basename $file .txt).wav"
done
```

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

### Bark 모델 라이선스
- **라이선스**: MIT
- **상업적 사용**: ✅ 가능
- **수정/배포**: ✅ 가능
- **출처 표시**: ✅ 권장

```
Copyright (c) 2023 Suno AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 감사의 말

### Bark 모델
- [Suno AI](https://suno.ai/) - Bark TTS 모델 개발 및 오픈소스 공개

### 의존성
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [Transformers](https://huggingface.co/docs/transformers/) - 모델 로딩
- [PyTorch](https://pytorch.org/) - 딥러닝 프레임워크
- [SciPy](https://scipy.org/) - 오디오 처리

### 기여자
- **한경희** - Bark 모델 조사 및 보고서 작성
  - CPU 환경 실행 성공
  - 오류 해결 방법 제시
  - pyproject.toml 활용 팁
- **조화평** - 서버 개발 및 통합
  - FastAPI 서버 구현
  - my-voice-lab 통합
  - 에러 해결 (경고 억제, torchaudio 문제)

---

## 🎊 버전 이력

### v1.0.2 (2025-12-02) - 최종 안정 버전
- ✅ torchaudio.save → scipy.io.wavfile.write
- ✅ torchaudio 에러 완전 해결
- ✅ 오디오 정규화 추가

### v1.0.1 (2025-12-02)
- ✅ 경고 메시지 억제 코드 추가
- ✅ transformers 로거 레벨 조정

### v1.0.0 (2025-12-02)
- ✅ 초기 릴리스
- ✅ FastAPI 서버 구현
- ✅ 3개 엔드포인트 (/, /health, /synthesize)
- ✅ 100+ 화자 프리셋 지원
- ✅ 특수 토큰 지원

---

## 🎯 다음 단계

1. ✅ 서버 설치 및 실행
2. 📚 API 문서 확인 (http://localhost:8600/docs)
3. 🎭 특수 토큰 실험 ([laughs], [music])
4. 👥 화자 프리셋 탐험 (v2/ko_speaker_0 ~ 5)
5. ⚡ 성능 최적화 (GPU 사용)
6. 🚀 프로젝트에 통합

**Happy Voice Synthesis!** 🐶🎉

---

<div align="center">

Made with ❤️ by my-voice-lab team

**표현력 넘치는 음성을 만들어보세요!**

[⬆ Back to top](#-bark-tts-server)

</div>