# mental_health_ai/companion.py

import pyttsx3
import requests
from textblob import TextBlob
import speech_recognition as sr
import re
import datetime
import json
import time

#from companion import main

# === Configuration ===
CONFIG = {
    "ollama": {
        "model": "mental-health-ai",
        "api_url": "http://localhost:11434/api/generate",
        "timeout": 30,
        "retries": 3
    },
    "voice": {
        "preferred_voice": "zira",
        "speech_rate": 150
    },
    "privacy": {
        "max_history": 20,  # Max conversation turns to remember
        "clear_on_exit": False
    }
}

# === Initialize Text-to-Speech ===
engine = pyttsx3.init()
engine.setProperty('rate', CONFIG['voice']['speech_rate'])

# Try to find preferred voice
voices = engine.getProperty('voices')
for voice in voices:
    if CONFIG['voice']['preferred_voice'].lower() in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break
else:
    engine.setProperty('voice', voices[1].id)  # Fallback

def speak(text):
    """Convert text to speech with basic sanitization"""
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
    try:
        engine.say(clean_text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠ TTS Error: {e}")

# === Voice Input ===
def save_conversation_history(history, filename="conversation_log.txt"):
    with open(filename, "a") as file:
        for entry in history:
            file.write(f"{entry}\n")

def get_voice_input(timeout=5, phrase_time_limit=10):
    """Capture voice input with configurable timeout"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print(f"🎙 Listening (timeout: {timeout}s)...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            print("⌛ Listening timed out")
            return ""
        except Exception as e:
            print(f"⚠ Voice input error: {e}")
            return ""

# === Time-Based Greeting ===
def get_greeting():
    """Return appropriate greeting based on time of day"""
    hour = datetime.datetime.now().hour
    if hour < 5:
        return "🌙 It's late! How are you holding up?"
    elif hour < 12:
        return "☀ Good morning! How are you feeling today?"
    elif hour < 18:
        return "🌼 Good afternoon! What's on your mind?"
    else:
        return "🌙 Good evening. How was your day?"

# === Mood Analysis ===
def analyze_mood(text):
    """Analyze text sentiment and return appropriate response prefix"""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    mood = ""
    breathing_prompt = ""
    
    if polarity > 0.3:
        mood = "The user seems positive. Respond with warmth and encouragement. 😊\n\n"
    elif polarity < -0.3:
        mood = "The user may be struggling. Respond with empathy and care. 💖\n\n"
        if subjectivity > 0.6:  # Highly personal/emotional
            breathing_prompt = "\nRemember to breathe... inhale deeply... hold... and exhale slowly. 🌬\n"
    else:
        mood = "The user seems neutral. Respond with gentle curiosity. 🌱\n\n"
    
    return mood + breathing_prompt

# === Conversation Management ===
conversation_history = []

def add_to_history(role, content):
    """Add message to history, enforcing max length"""
    conversation_history.append({"role": role, "content": content})
    if len(conversation_history) > CONFIG['privacy']['max_history']:
        conversation_history.pop(0)

# === Query Ollama ===
def ask_ollama(user_input, retries=CONFIG['ollama']['retries']):
    """Get response from Ollama with error handling and retries"""
    mood_prefix = analyze_mood(user_input)
    add_to_history("user", user_input)
    
    prompt = (
        # 1. Context and Role Definition
        "You are MindfulMate, a compassionate mental health companion. "
        "Your role is to provide emotional support through:\n"
        "- Active listening and validation\n"
        "- Gentle guidance (not clinical advice)\n"
        "- Brief coping strategies when appropriate\n\n"
    
        # 2. Response Guidelines
        "Response Requirements:\n"
        f"{mood_prefix}"  # Insert analyzed mood context
        "• Tone: Warm, empathetic, human-like\n"
        "• Length: 2-4 sentences (adjust based on need)\n"
        "• Style: Simple language, occasional emojis (😊, 💖, 🌱)\n"
        "• Focus: Stay on the user's emotional needs\n\n"
    
        # 3. Conversation History (clear formatting)
        "Conversation Context:\n"
            + "\n".join(
            f"[{m['role'].upper()}]: {m['content']}" 
            for m in conversation_history[-4:]  # Slightly more context
        )
        + "\n\n"
    
        # 4. Clear Instruction
        "Please respond thoughtfully to the USER's last message, "
        "focusing on their emotional state shown above:"
    )
    
    data = {
        "model": CONFIG['ollama']['model'],
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(
                CONFIG['ollama']['api_url'],
                json=data,
                timeout=CONFIG['ollama']['timeout']
            )
            response.raise_for_status()
            
            reply = response.json().get("response", "").strip()
            if not reply:
                raise ValueError("Empty response from model")
                
            add_to_history("assistant", reply)
            return reply
            
        except Exception as e:
            if attempt == retries - 1:
                return f"⚠ Sorry, I'm having trouble responding. Please try again later. ({str(e)})"
            time.sleep(1)  # Wait before retrying

# === Main Interaction ===
def main():
    print("\n🧠 Mental Health Companion")
    print("Type 'help' for options or 'exit' to quit\n")
    
    greeting = get_greeting()
    print(greeting)
    
    # Initial voice preference
    use_voice = input("🔊 Enable voice responses? (y/n): ").strip().lower() == 'y'
    if use_voice:
        speak(greeting)
    
    while True:
        try:
            # Input method selection
            input_method = input("\n🎤 Use voice input? (y/n/help): ").strip().lower()
            
            if input_method == 'help':
                print("\nHelp Options:")
                print("- 'y': Speak your response")
                print("- 'n': Type your response")
                print("- 'clear': Reset conversation")
                print("- 'exit': End the conversation")
                print("- 'voice': Toggle voice responses")
                continue
            elif input_method == 'clear':
                conversation_history.clear()
                print("🗑 Conversation history cleared")
                continue
            elif input_method == 'voice':
                use_voice = not use_voice
                print(f"🔊 Voice responses {'enabled' if use_voice else 'disabled'}")
                continue
            elif input_method == 'exit':
                break
            
            # Get user input
            if input_method == 'y':
                user_input = get_voice_input()
                if not user_input:
                    continue
                print(f"📝 You said: {user_input}")
            else:
                user_input = input("📝 Your thoughts: ").strip()
                if not user_input:
                    continue
            
            # Check for exit phrases
            if any(word in user_input.lower() for word in ['exit', 'bye', 'goodbye', 'quit']):
                break
            
            # Get and display response
            response = ask_ollama(user_input)
            print(f"\n💡 Companion: {response}\n")
            
            if use_voice:
                speak(response)
                
        except KeyboardInterrupt:
            print("\n🛑 Session interrupted")
            break
    
    # Exit message
    farewell = "🌟 Remember to be kind to yourself. Reach out if you need support. 💖"
    print(f"\n{farewell}")
    if use_voice:
        speak(farewell)
    
    if CONFIG['privacy']['clear_on_exit']:
        conversation_history.clear()

def start_mental_health_session():
    main()
    print("🧠 Mental Health Companion is active. Type 'exit' to quit.")
    greeting = get_greeting()
    print("🤖:", greeting)
    speak(greeting)

    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ("exit", "quit", "bye", "stop", "thank you"):
            farewell = "🌟 Take care of yourself. I'm always here when you need me."
            print("🤖:", farewell)
            speak(farewell)
            if CONFIG['privacy']['clear_on_exit']:
                conversation_history.clear()
            break

        if not user_input:
            print("⚠ Please say or type something.")
            continue

        response = ask_ollama(user_input)
        print("🤖:", response)
        speak(response)


if __name__ == "__main__":
    main()