import reflex as rx
# from frontend.components.badge import made_with_reflex
from frontend.state import State
from frontend.speechreflex import audio, capture, Audio

import requests

from reflex_audio_capture import AudioRecorderPolyfill, get_codec, strip_codec_part

from urllib.request import urlopen



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
            return rx.set_value("input1", transcript)
            

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





def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        # Question
        rx.box(
            rx.markdown(
                question,
                class_name="[&>p]:!my-2.5",
            ),
            class_name="relative bg-slate-3 px-5 rounded-3xl max-w-[70%] text-slate-12 self-end",
        ),
        # Answer
        rx.box(
            rx.box(
                rx.image(
                    src="/logo.svg",
                    class_name="h-6" + rx.cond(State.processing, " animate-pulse", ""),
                ),
            ),
            rx.box(
                rx.markdown(
                    answer,
                    class_name="[&>p]:!my-2.5",
                ),
                rx.box(
                    rx.el.button(
                        rx.icon(tag="copy", size=18),
                        class_name="p-1 text-slate-10 hover:text-slate-11 transform transition-colors cursor-pointer",
                        on_click=[rx.set_clipboard(answer), rx.toast("Copied!")],
                        title="Copy",
                    ),
                    class_name="-bottom-9 left-5 absolute opacity-0 group-hover:opacity-100 transition-opacity",
                ),
                class_name="relative bg-accent-4 px-5 rounded-3xl max-w-[70%] text-slate-12 self-start",
            ),
            class_name="flex flex-row gap-6",
        ),
        class_name="flex flex-col gap-8 pb-10 group",
    )


def chat() -> rx.Component:
    return rx.scroll_area(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        ),
        scrollbars="vertical",
        class_name="w-full",
        padding_top="2rem",
    )


def action_bar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.el.input(
                placeholder="Ask anything",
                on_blur=State.set_question,
                id="input1",
                class_name="box-border bg-slate-3 px-4 py-2 pr-14 rounded-full w-full outline-none focus:outline-accent-10 h-[48px] text-slate-12 placeholder:text-slate-9",
            ),

            rx.el.button(
                rx.cond(
                    State.processing,
                    rx.icon(
                        tag="loader-circle",
                        size=19,
                        color="white",
                        class_name="animate-spin",
                    ),
                    rx.icon(tag="arrow-up", size=19, color="white"),
                ),
                on_click=[State.answer, rx.set_value("input1", "")],
                class_name="top-1/2 right-4 absolute bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
                disabled=rx.cond(
                    State.processing | (State.question == ""), True, False
                ),
            ),
            # rx.box(
            #     audio()
            # ),
            class_name="relative w-full",
            
        ),
        rx.container(
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
    ),
                    
        # Made with Reflex link
        # made_with_reflex(),
        class_name="flex flex-col justify-center items-center gap-6 w-full",
    )


# def video_icon() -> rx.component:
#     return rx.box(
#         rx.icon("microphone"),
#     )