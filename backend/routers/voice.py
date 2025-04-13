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

router = APIRouter(
    prefix="/voice",
    tags=["Voice Integration"]
)

@router.post("/upload", summary="Convert Voice to Text")
async def voice_to_text(file: UploadFile = File(...)):
    """
    Endpoint to perform speech recognition on an uploaded audio file.
    
    Request:
        - Upload an audio file in WAV format.
    
    Returns:
        - JSON containing the recognized text.
        
    Raises:
        - HTTPException (400) if conversion fails.
    """
    try:
        # Read the uploaded file content
        audio_bytes = await file.read()
        temp_file_path = "temp_audio.wav"
        
        # Save the uploaded file to disk temporarily
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)
            
        # Initialize the speech recognizer
        recognizer = sr.Recognizer()
        
        # Load the audio file for processing
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
        
        # Use Google's speech recognition API to convert speech to text
        recognized_text = recognizer.recognize_google(audio_data)
        
        # Remove the temporary file after processing
        os.remove(temp_file_path)
        
        return {"recognized_text": recognized_text}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Voice to text conversion failed: {e}")

@router.post("/tts", summary="Convert Text to Speech")
def text_to_speech(text: str = Form(...)):
    """
    Endpoint to convert provided text to speech.
    
    Request:
        - Form data containing the 'text' field.
    
    Returns:
        - A streaming response with the synthesized speech audio (WAV format).
        
    Raises:
        - HTTPException (400) if text to speech conversion fails.
    """
    try:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        output_audio_file = "output_tts.wav"
        
        # Convert the text to audio and save to file
        engine.save_to_file(text, output_audio_file)
        engine.runAndWait()
        
        # Open the audio file and read its binary contents
        with open(output_audio_file, "rb") as audio_file:
            audio_bytes = io.BytesIO(audio_file.read())
        
        # Clean up the temporary audio file
        os.remove(output_audio_file)
        
        # Return the audio file as a streaming response with the proper media type
        return StreamingResponse(audio_bytes, media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text to speech conversion failed: {e}")
