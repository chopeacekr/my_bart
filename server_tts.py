"""
Bark TTS Server v1.0.0

Suno AI의 Bark 모델을 사용한 표현력 높은 다국어 음성 합성 서버
- 13개 언어 지원
- 100개 이상의 화자 프리셋
- 비언어적 표현 (웃음, 한숨, 울음 등)
- 배경음악 및 효과음 생성 가능
"""

import logging
import time
import io
import os
import warnings
from pathlib import Path
from typing import Optional

import torch
import torchaudio
from transformers import AutoProcessor, BarkModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# ⭐ Bark 특유의 경고 메시지 억제
warnings.filterwarnings("ignore", message=".*attention mask.*")
warnings.filterwarnings("ignore", message=".*pad_token_id.*")
warnings.filterwarnings("ignore", message=".*pad token.*")

# transformers 로거 경고 억제
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Bark TTS Server",
    description="Expressive multi-language speech synthesis with Bark",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
processor = None
model = None
device = None
sample_rate = 24000  # Bark의 기본 샘플레이트


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    global processor, model, device, sample_rate
    
    logger.info("")
    logger.info("╔═══════════════════════════════════════════╗")
    logger.info("║   Bark TTS Server                         ║")
    logger.info("║   포트: 8600                              ║")
    logger.info("║   모델: Bark Small (API v1.0.0)           ║")
    logger.info("╚═══════════════════════════════════════════╝")
    logger.info("")
    logger.info("==================================================")
    logger.info("🚀 Bark TTS Server 시작 중...")
    logger.info("==================================================")
    
    # 디바이스 설정
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"📱 GPU 감지: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("📱 CPU 모드로 실행")
    
    # 메모리 사용량 출력
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"💾 현재 메모리 사용량: {memory_info.rss / 1024 / 1024:.1f} MB")
    
    try:
        # Bark Small 모델 로드
        logger.info("📦 Bark Small 모델 로딩 중: suno/bark-small")
        logger.info("⏳ 첫 실행 시 모델 다운로드로 1-2분 소요될 수 있습니다...")
        
        processor = AutoProcessor.from_pretrained("suno/bark-small")
        model = BarkModel.from_pretrained("suno/bark-small")
        model = model.to(device)
        
        sample_rate = model.generation_config.sample_rate
        
        # 메모리 사용량 재확인
        memory_info = process.memory_info()
        logger.info(f"💾 모델 로드 후 메모리: {memory_info.rss / 1024 / 1024:.1f} MB")
        
        logger.info("==================================================")
        logger.info("✅ Bark Small 모델 로딩 완료!")
        logger.info("🎉 Bark TTS Server 준비 완료! (포트: 8600)")
        logger.info("==================================================")
        
    except Exception as e:
        logger.error(f"❌ 모델 로딩 실패: {e}")
        raise


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Bark TTS Server",
        "version": "1.0.0",
        "model": "suno/bark-small",
        "status": "running",
        "features": [
            "Multi-language support (13 languages)",
            "100+ speaker presets",
            "Non-verbal expressions ([laughs], [sighs], etc.)",
            "Music and sound effects generation",
        ]
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "device": str(device),
        "sample_rate": sample_rate,
    }


@app.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice_preset: Optional[str] = Form(None),
    speed: float = Form(1.0),
):
    """
    텍스트를 음성으로 변환
    
    Args:
        text: 변환할 텍스트 (특수 토큰 사용 가능: [laughs], [sighs], [music], etc.)
        voice_preset: 화자 프리셋 (예: v2/en_speaker_0, v2/ko_speaker_1)
        speed: 음성 속도 (0.5 ~ 2.0, 기본값: 1.0)
    
    Returns:
        WAV 오디오 파일
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    temp_files = []
    
    try:
        logger.info(f"📝 TTS 요청: '{text[:50]}...' (길이: {len(text)})")
        
        if voice_preset:
            logger.info(f"🎭 화자 프리셋: {voice_preset}")
        else:
            logger.info("ℹ️  기본 화자 프리셋 사용")
        
        logger.info(f"⚡ 속도: {speed}x")
        
        # 텍스트 전처리
        inputs = processor(text, return_tensors="pt", voice_preset=voice_preset).to(device)
        
        # TTS 생성
        logger.info("🎤 음성 생성 중...")
        
        with torch.inference_mode():
            audio_array = model.generate(**inputs)
        
        # NumPy 배열로 변환 및 차원 조정
        audio_array = audio_array.cpu().numpy().squeeze()
        
        # 속도 조절
        if speed != 1.0:
            import scipy.signal as signal
            audio_array = signal.resample(
                audio_array,
                int(len(audio_array) / speed)
            )
        
        # 오디오 정규화 (int16 범위로)
        audio_array = audio_array / max(abs(audio_array.max()), abs(audio_array.min()))
        audio_int16 = (audio_array * 32767).astype('int16')
        
        # 임시 파일에 WAV 저장 (scipy 사용)
        import scipy.io.wavfile as wavfile
        temp_wav_path = f"/tmp/bark_output_{int(time.time())}.wav"
        temp_files.append(temp_wav_path)
        
        wavfile.write(temp_wav_path, sample_rate, audio_int16)
        
        # 임시 파일을 메모리로 읽기
        with open(temp_wav_path, "rb") as f:
            audio_bytes = f.read()
        
        elapsed_time = time.time() - start_time
        audio_size = len(audio_bytes)
        
        logger.info(f"✅ TTS 변환 완료")
        logger.info(f"   - 처리 시간: {elapsed_time:.2f}초")
        logger.info(f"   - 샘플레이트: {sample_rate}Hz")
        logger.info(f"   - 오디오 크기: {audio_size / 1024:.1f} KB")
        
        # 임시 파일 정리
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug(f"🗑️  임시 파일 삭제: {temp_file}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️  임시 파일 삭제 실패: {temp_file} - {cleanup_error}")
        
        # WAV 파일 반환
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "X-Processing-Time": str(round(elapsed_time, 2)),
                "X-Sample-Rate": str(sample_rate),
                "X-Device": str(device),
            }
        )
        
    except Exception as e:
        logger.error(f"❌ TTS 변환 실패: {e}")
        logger.error(f"Traceback (most recent call last):")
        import traceback
        logger.error(traceback.format_exc())
        
        # 에러 발생 시에도 임시 파일 정리
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server_tts:app",
        host="0.0.0.0",
        port=8600,
        reload=False
    )