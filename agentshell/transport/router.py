"""
Router — central message hub between transports and the core.

Why it exists:
    The core (L2) must not know WHO is talking to it — terminal,
    Telegram bot, or web UI. The router sits in between: it receives
    input from any transport, passes it to the core, and broadcasts
    the core's response back to all registered transports.

Flow:
    Transport (terminal / telegram / web)
        └──> Router ──> Core (L2)
                  <──
        <──┘

Today:  only `terminal` is connected, so the router is a thin pass-through.
Later:  more transports plug in without touching the core.
"""


class TrafficRouter:
    def __init__(self):
        pass

    def process(self, text: str) -> str:
        """ ... """
        return text
