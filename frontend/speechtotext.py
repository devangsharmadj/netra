import requests
from datetime import datetime
# Set your Deepgram API key
API_KEY = '65a890e9867c3dda76519eb728d08d69547761c6'
URL = 'https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true'

# Prepare the headers
headers = {
    'Authorization': f'Token {API_KEY}'
}

# Get the audio file from the user
# audio_file_path = input("Enter the path to the audio file you want to upload: ")

# Open the audio file in binary mode
with open(f'{datetime.now()}', 'rb') as audio_file:
    # Send the POST request with the audio file
    response = requests.post(URL, headers=headers, data=audio_file)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        transcript_data = response.json()
        
        # Extract the transcription text
        transcript = transcript_data['results']['channels'][0]['alternatives'][0]['transcript']
        
        # Print the transcribed sentence
        print("Transcription result:")
        print(transcript)
    else:
        # If there's an error, print the error message
        print("Error:", response.status_code)
        print("Message:", response.text)