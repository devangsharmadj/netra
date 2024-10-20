from urllib.request import urlopen

import reflex as rx 
import requests

from reflex_audio_capture import AudioRecorderPolyfill, get_codec, strip_codec_part

API_KEY = '65a890e9867c3dda76519eb728d08d69547761c6'
URL = 'https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true'

# Prepare the headers
headers = {
    'Authorization': f'Token {API_KEY}'
}


# from openai import AsyncOpenAI

# client = AsyncOpenAI()

REF = "myaudio"


class Audio(rx.State):
    """The app state."""

    has_error: bool = False
    processing: bool = False
    transcript: list[str] = []
    timeslice: int = 0
    device_id: str = ""
    use_mp3: bool = True

    async def on_data_available(self, chunk: str):
        mime_type, _, codec = get_codec(chunk).partition(";")
        audio_type = mime_type.partition("/")[2]
        if audio_type == "mpeg":
            audio_type = "mp3"
        print(len(chunk), mime_type, codec, audio_type)
        with urlopen(strip_codec_part(chunk)) as audio_data:
            # print(type(audio_data))
            with open("output_audio.mp3", "wb") as audio_file:
                audio_file.write(audio_data.read())
        with open(f'output_audio.mp3', 'rb') as audio_file:
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

            # try:
            #     self.processing = True
            #     yield
            #     transcription = await client.audio.transcriptions.create(
            #         model="whisper-1",
            #         file=("temp." + audio_type, audio_data.read(), mime_type),
            #     )
            # except Exception as e:
            #     self.has_error = True
            #     yield capture.stop()
            #     raise
            # finally:
            #     self.processing = False
            self.transcript.append(transcript)

    def set_timeslice(self, value):
        self.timeslice = value[0]

    def set_device_id(self, value):
        self.device_id = value
        yield capture.stop()

    def on_error(self, err):
        print(err)

    def on_load(self):
        # We can start the recording immediately when the page loads
        return capture.start()


capture = AudioRecorderPolyfill.create(
    id=REF,
    on_data_available=Audio.on_data_available,
    on_error=Audio.on_error,
    timeslice=Audio.timeslice,
    device_id=Audio.device_id,
    use_mp3=Audio.use_mp3,
)


def input_device_select():
    return rx.select.root(
        rx.select.trigger(placeholder="Select Input Device"),
        rx.select.content(
            rx.foreach(
                capture.media_devices,
                lambda device: rx.cond(
                    device.deviceId & device.kind == "audioinput",
                    rx.select.item(device.label, value=device.deviceId),
                ),
            ),
        ),
        on_change=Audio.set_device_id,
    )


def audio() -> rx.Component:
    return rx.container(
        rx.vstack(
            capture,
            rx.cond(
                capture.is_recording,
                rx.button("Stop Recording", on_click=capture.stop()),
                rx.button(
                    rx.icon(tag="mic"),
                    on_click=capture.start(),
                ),
            ),
            style={"width": "100%", "> *": {"width": "100%"}},
        ),
        size="1",
        margin_y="2em",
    )


# Add state and page to the app.
app = rx.App()
app.add_page(audio)