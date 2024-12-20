import assemblyai as aai
import os
from dotenv import load_dotenv
import spotipy as sp
from dotenv import load_dotenv
from together import Together

load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

def parse_audio(path_to_audio):    
    config = aai.TranscriptionConfig(sentiment_analysis=True)
    transcript = aai.Transcriber().transcribe(path_to_audio, config)
    text_corpse=''
    sentiment_scores=[]
    for sentiment_result in transcript.sentiment_analysis:
        text_corpse+=sentiment_result.text
        sentiment_scores.append(sentiment_result.sentiment)
    return [text_corpse,sentiment_scores]
    
def get_song():
    pass

def get_youtube_url():
    pass