import reflex as rx

def video() -> rx.Component:
    return rx.box(
        rx.video(
            url="/calhacks.mp4",
            controls=True,
            #position="relative",
            # width="50%",
            # height="100%",
            border="none",
        ),
        margin_bottom="2rem",
    )
