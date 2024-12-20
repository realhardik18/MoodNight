import assemblyai as aai
import os
from dotenv import load_dotenv
import together
import requests
from bs4 import BeautifulSoup
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


def get_youtube_url(search_query):
    # Format the search query to be used in the URL
    search_query = urllib.parse.quote_plus(search_query)
    
    # Construct the YouTube search URL
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    try:
        # Send a GET request to YouTube search page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first video link in the search results
        video = soup.find('a', {'class': 'yt-simple-endpoint style-scope ytd-video-renderer'})
        
        # If a video is found, return the full YouTube URL
        if video:
            video_url = f"https://www.youtube.com{video['href']}"
            return video_url
        else:
            return "No videos found"
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

# Example usage
search_query = "Ed Sheeran - Happier"
print(get_youtube_url(search_query))


