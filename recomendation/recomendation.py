import assemblyai as aai
import os
from dotenv import load_dotenv
import together
import requests
import json
import random

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

def update_json(url):
    # Load the existing data from the JSON file
    with open(r'recomendation\data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    data['youtube-url'] = url
    
    # Save the updated data back to the JSON file
    with open(r'recomendation\data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)  # Pretty-print JSON for readability

# Example usage

#print(get_youtube_link(search_query=search_query))

def get_latest_audio():
    return list(filter(lambda x: x.split('.')[-1]=='wav',os.listdir('audio')))[-1]

hip_hop_artists = [
    "Tupac Shakur",
    "The Notorious B.I.G.",
    "Jay-Z",
    "Nas",
    "Kendrick Lamar",
    "Dr. Dre",
    "Eminem",
    "Snoop Dogg",
    "Kanye West",
    "Lil Wayne"
]

while True:
    audio_file='recording/'+get_latest_audio()
    data=parse_audio(audio_file)
    update_json(get_youtube_link(get_song(data,random.choice(hip_hop_artists))))



