import reflex as rx
from frontend.state import State


def template_card(icon: str, title: str, description: str, color: str) -> rx.Component:
    return rx.el.button(
        rx.icon(tag=icon, color=rx.color(color, 9), size=16),
        rx.text(title, class_name="font-medium text-slate-11 text-sm"),
        rx.text(description, class_name="text-slate-10 text-xs"),
        class_name="relative align-top flex flex-col gap-2 border-slate-4 bg-slate-1 hover:bg-slate-3 shadow-sm px-3 pt-3 pb-4 border rounded-2xl text-[15px] text-start transition-colors",
        on_click=[State.set_question(description), State.answer],
    )


def templates() -> rx.Component:
    return rx.box(
        rx.image(
            src="/logo.svg",
            class_name="opacity-70 w-auto h-11 pointer-events-none",
        ),
        rx.box(
            template_card(
                "align-center",
                "Get event summaries",
                "What happened between 2pm and 3pm today?",
                "grass",
            ),
            template_card(
                "package-search",
                "Package delivery information",
                "When did I receive a package?",
                "tomato",
            ),
            template_card(
                "shield-check",
                "Know about intruders",
                "Give me the timestamp where there was an intruder",
                "blue",
            ),

            template_card(
                "search",
                "Query the database in seconds",
                "How many red cars passed?",
                "purple",
            ),
    
            class_name="gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
        ),
        class_name="flex flex-col justify-center items-center gap-10 w-full max-w-4xl px-6 z-50",
        style={
            "animation": "reveal 0.35s ease-out",
            "@keyframes reveal": {"0%": {"opacity": "0"}, "100%": {"opacity": "1"}},
        },
        display=rx.cond(State.chat_history, "none", "flex"),
    )
