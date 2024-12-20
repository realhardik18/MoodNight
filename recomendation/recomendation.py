import assemblyai as aai
import os
from dotenv import load_dotenv
import together
import requests
import json
import urllib.parse

load_dotenv()
together.api_key= os.getenv('TOGETHER_AI')
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
    
def get_song(mood,artist):
    prompt = f"""Please recommend a single {mood} song by {artist}. Provide the **exact title** as it appears on YouTube, including details like "(Official Audio)" or "(Official Video)"."""
    response = together.Completion.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Specify the Together AI model
    prompt=prompt,
    max_tokens=50,
    temperature=0.7
    )    
    return response.choices[0].text


def get_youtube_link(search_query):
    search_query = search_query.replace(' ', '+')  # Replace spaces with '+'
    
    params = {
        "api_key": os.getenv('SERP_API'),
        "engine": "google",
        "q": f"{search_query}+site:youtube.com",
        "location": "India",
    }
    
    # Construct the API URL
    URL = (
        f"https://serpapi.com/search.json?engine=google"
        f"&q={params['q']}&location={params['location']}"
        f"&google_domain=google.com&gl=us&hl=en&api_key={params['api_key']}"
    )
    
    # Fetch and parse the response
    response = requests.get(URL).json()
    
    # Return the first YouTube link
    try:
        for result in response.get('organic_results', []):
            link = result.get('link')
            if "youtube.com" in link:
                return link
        return "No YouTube link found."
    except Exception as e:
        return f"Error fetching YouTube link: {str(e)}"

def update_json()

# Example usage

print(get_youtube_link(search_query=search_query))


