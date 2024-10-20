# """Take screenshots and video recordings from webcam."""
# import time
# from pathlib import Path
# from urllib.request import urlopen
# from PIL import Image

# import reflex as rx
# import reflex_webcam as webcam


# # Identifies a particular webcam component in the DOM
# WEBCAM_REF = "webcam"
# VIDEO_FILE_NAME = "video.webm"

# # The path containing the app
# APP_PATH = Path(__file__)
# APP_MODULE_DIR = APP_PATH.parent
# SOURCE_CODE = [
#     APP_MODULE_DIR.parent.parent / "custom_components/reflex_webcam/webcam.py",
#     APP_PATH,
#     APP_MODULE_DIR.parent / "requirements.txt",
# ]

# # Mark Upload as used so StaticFiles can get mounted on /_upload
# rx.upload()


# class State(rx.State):
#     last_screenshot: Image.Image | None = None
#     last_screenshot_timestamp: str = ""
#     loading: bool = False
#     recording: bool = False

#     def handle_screenshot(self, img_data_uri: str):
#         """Webcam screenshot upload handler.
#         Args:
#             img_data_uri: The data uri of the screenshot (from upload_screenshot).
#         """
#         if self.loading:
#             return
#         self.last_screenshot_timestamp = time.strftime("%H:%M:%S")
#         with urlopen(img_data_uri) as img:
#             self.last_screenshot = Image.open(img)
#             self.last_screenshot.load()
#             # convert to webp during serialization for smaller size
#             self.last_screenshot.format = "WEBP"  # type: ignore

#     def _video_path(self) -> Path:
#         return Path(rx.get_upload_dir()) / VIDEO_FILE_NAME

#     @rx.var(cache=True)
#     def video_exists(self) -> bool:
#         if not self.recording:
#             return self._video_path().exists()
#         return False

#     def on_start_recording(self):
#         self.recording = True
#         print("Started recording")
#         with self._video_path().open("wb") as f:
#             f.write(b"")

#     def _strip_codec_part(self, chunk: str) -> str:
#         parts = chunk.split(";")
#         for part in parts:
#             if "codecs=" in part:
#                 parts.remove(part)
#                 break
#         return ";".join(parts)

#     def handle_video_chunk(self, chunk: str):
#         print("Got video chunk", len(chunk))
#         with self._video_path().open("ab") as f:
#             with urlopen(self._strip_codec_part(chunk)) as vid:
#                 f.write(vid.read())

#     def on_stop_recording(self):
#         print(f"Stopped recording: {self._video_path()}")
#         self.recording = False

#     def start_recording(self, ref: str):
#         """Start recording a video."""
#         return webcam.start_recording(
#             ref,
#             on_data_available=State.handle_video_chunk,
#             on_start=State.on_start_recording,
#             on_stop=State.on_stop_recording,
#             timeslice=1000,
#         )


# def last_screenshot_widget() -> rx.Component:
#     """Widget for displaying the last screenshot and timestamp."""
#     return rx.box(
#         rx.cond(
#             State.last_screenshot,
#             rx.fragment(
#                 rx.image(src=State.last_screenshot),
#                 rx.text(State.last_screenshot_timestamp),
#             ),
#             rx.center(
#                 rx.text("Click image to capture.", size="4"),
#             ),
#         ),
#         height="270px",
#     )


# def webcam_upload_component(ref: str) -> rx.Component:
#     """Component for displaying webcam preview and uploading screenshots.
#     Args:
#         ref: The ref of the webcam component.
#     Returns:
#         A reflex component.
#     """
#     return rx.vstack(
#         webcam.webcam(
#             id=ref,
#             on_click=webcam.upload_screenshot(
#                 ref=ref,
#                 handler=State.handle_screenshot,  # type: ignore
#             ),
#             audio=True,
#         ),
#         rx.cond(
#             ~State.recording,
#             rx.button(
#                 "🟢 Start Recording",
#                 on_click=State.start_recording(ref),
#                 color_scheme="green",
#                 size="4",
#             ),
#             rx.button(
#                 "🟤 Stop Recording",
#                 on_click=webcam.stop_recording(ref),
#                 color_scheme="tomato",
#                 size="4",
#             ),
#         ),
#         rx.cond(
#             State.video_exists,
#             rx.link(
#                 "Download Last Video", href=rx.get_upload_url(VIDEO_FILE_NAME), size="4"
#             ),
#         ),
#         last_screenshot_widget(),
#         width="320px",
#         align="center",
#     )


# def index() -> rx.Component:
#     return rx.fragment(
#         rx.color_mode.button(position="top-right"),
#         rx.center(
#             webcam_upload_component(WEBCAM_REF),
#             padding_top="3em",
#         ),
#         *[
#             rx.vstack(
#                 rx.heading(f"Source Code: {p.name}"),
#                 rx.code_block(
#                     p.read_text(),
#                     language="python",
#                     width="90%",
#                     overflow_x="auto",
#                 ),
#                 margin_top="5em",
#                 padding_x="1em",
#                 width="100vw",
#                 align="center",
#             )
#             for p in SOURCE_CODE
#         ],
#     )


# app = rx.App()
# app.add_page(index)

"""Reflex custom component Webcam."""
from __future__ import annotations
from typing import Any, List

import reflex as rx
from reflex.vars import Var


class Webcam(rx.Component):
    """Wrapper for react-webcam component."""

    # The React library to wrap.
    library = "react-webcam"

    # The React component tag.
    tag = "Webcam"

    # If the tag is the default export from the module, you can set is_default = True.
    # This is normally used when components don't have curly braces around them when importing.
    is_default = True
    
    # The props of the React component.
    # Note: when Reflex compiles the component to Javascript,
    # `snake_case` property names are automatically formatted as `camelCase`.
    # The prop names may be defined in `camelCase` as well.

    # enable/disable audio
    audio: Var[bool] = False

    # format of screenshot
    screenshot_format: Var[str] = "image/jpeg"  # type: ignore

    # show camera preview and get the screenshot mirrored
    mirrored: Var[bool] = False

    # allow passing video constraints such as facingMode
    video_constraints: Var[dict] = {}

    special_props: set[Var] = [Var.create_safe("muted", _var_is_string=False)]

    def add_hooks(self) -> List[str]:
        if self.id is not None:
            return [
                f"refs['mediarecorder_{self.id}'] = useRef(null)",
            ]
        return []


webcam = Webcam.create


def upload_screenshot(ref: str, handler: rx.event.EventHandler):
    """Helper to capture and upload a screenshot from a webcam component.
    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the screenshot.
    """
    return rx.call_script(
        f"refs['ref_{ref}'].current.getScreenshot()",
        callback=handler,
    )


def _validate_event_handler(handler: Any, name: str) -> None:
    if not isinstance(handler, rx.event.EventHandler):
        raise ValueError(
            f"{name} must be an EventHandler referenced from a state class, "
            f"got {handler}."
        )


def start_recording(
    ref: str,
    on_data_available: rx.event.EventHandler,
    on_start: rx.event.EventHandler | None = None,
    on_stop: rx.event.EventHandler | None = None,
    timeslice: str = "",
) -> str:
    """Helper to start recording a video from a webcam component.
    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the video chunk by chunk.
        timeslice: How often to emit a chunk. Defaults to "" which means only at the end.
    Returns:
        The ref of the media recorder to stop recording.
    """
    _validate_event_handler(on_data_available, "on_data_available")
    on_data_available_event = rx.utils.format.format_event(
        rx.event.call_event_handler(on_data_available, arg_spec=lambda data: [data])
    )
    if on_start is not None:
        _validate_event_handler(on_start, "on_start")
        on_start_event = rx.utils.format.format_event(
            rx.event.call_event_handler(on_start, arg_spec=lambda e: [])
        )
        on_start_callback = f"mediaRecorderRef.current.addEventListener('start', () => applyEvent({on_start_event}, socket))"
    else:
        on_start_callback = ""

    if on_stop is not None:
        _validate_event_handler(on_stop, "on_stop")
        on_stop_event = rx.utils.format.format_event(
            rx.event.call_event_handler(on_stop, arg_spec=lambda e: [])
        )
        on_stop_callback = f"mediaRecorderRef.current.addEventListener('stop', () => applyEvent({on_stop_event}, socket))"
    else:
        on_stop_callback = ""

    return rx.call_script(
        f"""
        const handleDataAvailable = (e) => {{
            if (e.data.size > 0) {{
                var a = new FileReader();
                a.onload = (e) => {{
                    const _data = e.target.result
                    applyEvent({on_data_available_event}, socket)
                }}
                a.readAsDataURL(e.data);
            }}
        }}
        const mediaRecorderRef = refs['mediarecorder_{ref}']
        if (mediaRecorderRef.current != null) {{
            mediaRecorderRef.current.stop()
        }}
        mediaRecorderRef.current = new MediaRecorder(refs['ref_{ref}'].current.stream, {{mimeType: 'video/webm'}})
        mediaRecorderRef.current.addEventListener(
          "dataavailable",
          handleDataAvailable,
        );
        {on_start_callback}
        {on_stop_callback}
        mediaRecorderRef.current.start({timeslice})""",
    )


def stop_recording(ref: str):
    """Helper to stop recording a video from a webcam component.
    Args:
        ref: The ref of the webcam component.
        handler: The event handler that receives the video blob.
    """
    return rx.call_script(
        f"refs['mediarecorder_{ref}'].current.stop()",
    )