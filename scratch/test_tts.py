from backend.tts.f5.engine import f5_engine
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

text = "مرحبا بك في مشروع أفيدنا للتحويل الصوتي. هذا اختبار للنظام الجديد."
task_id = "test_arabic_voice"

print(f"Starting generation for: {text}")
try:
    f5_engine.generate(task_id, text, lang="ar")
    output = f"backend/storage/audio/{task_id}.wav"
    if os.path.exists(output):
        print(f"SUCCESS: Audio generated at {output}")
        print(f"Size: {os.path.getsize(output)} bytes")
    else:
        print("FAILED: Audio file not found.")
except Exception as e:
    print(f"ERROR: {str(e)}")
