from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq()

def whisper(file_path: str) -> dict[str]:
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3-turbo",
                language="en",
                response_format="json",
                temperature=0.0,
            )
        return {"transcript": transcription.text}
    except Exception as e:
        print(e)
        return None
