"""
Voice Integration Router for MIND_ECHO API
Provides endpoints for converting speech to text and text to speech.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
import speech_recognition as sr
import pyttsx3
import os
import io

router = APIRouter(prefix="/voice", tags=["Voice Integration"])

@router.post("/upload", summary="Convert Voice to Text")
async def voice_to_text(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        temp_file_path = "temp_audio.wav"
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
        recognized_text = recognizer.recognize_google(audio_data)
        os.remove(temp_file_path)
        return {"recognized_text": recognized_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Voice to text conversion failed: {e}")

@router.post("/tts", summary="Convert Text to Speech")
def text_to_speech(text: str = Form(...)):
    try:
        engine = pyttsx3.init()
        output_audio_file = "output_tts.wav"
        engine.save_to_file(text, output_audio_file)
        engine.runAndWait()
        with open(output_audio_file, "rb") as audio_file:
            audio_bytes = io.BytesIO(audio_file.read())
        os.remove(output_audio_file)
        return StreamingResponse(audio_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text to speech conversion failed: {e}")
