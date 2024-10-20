import reflex as rx

from frontend import style
from frontend.state import SettingsState
from frontend.components.settings import settings_icon
from frontend.components.reset import reset
from frontend.views.templates import templates
from frontend.views.chat import chat, action_bar
from frontend.views.video import video
from frontend.speechreflex import audio
# from frontend.state import GeminiStarter




def index() -> rx.Component:
    return rx.theme(
        rx.el.style(
            f"""
            :root {{
                --font-family: "{SettingsState.font_family}", sans-serif;
            }}
        """
        ),
        # Top bar with the reset and settings buttons
        rx.box(
            reset(),
            settings_icon(),
            class_name="top-4 right-4 absolute flex flex-row items-center gap-3.5",
        ),
        # Main content
        rx.vstack(
            
            video(),
            # Video
            rx.box(
                templates()
            ),
            rx.box(
                rx.scroll_area(
                    chat(),
                action_bar(),
                )

            ),
            # # Chat history
            # # Action bar
            # Prompt examples
            # class_name="relative flex flex-col justify-between gap-20 mx-auto px-6 pt-16 lg:pt-6 pb-6 max-w-4xl h-screen",
            align="center"
        ),
        accent_color=SettingsState.color,
    )


app = rx.App()
app = rx.App(stylesheets=style.STYLESHEETS, style={"font_family": "var(--font-family)"})
app.add_page(
    index, title="Netra", description="Your AI security assistant"
)
