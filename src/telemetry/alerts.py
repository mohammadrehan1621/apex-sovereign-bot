import aiohttp
import asyncio
from rich.console import Console

console = Console(force_terminal=True, legacy_windows=False)

class TelemetryAlerts:
    def __init__(self, telegram_token: str = None, chat_id: str = None, discord_url: str = None):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.discord_url = discord_url

    async def emit_alert(self, title: str, message: str, level: str = "INFO"):
        prefix = {
            "INFO": "[INFO]",
            "WARNING": "[WARNING]",
            "CRITICAL": "[DEFENSE PROTOCOL TRIGGERED]",
            "EXECUTION": "[ORDER EXECUTED]",
            "TERMINATION": "[ABSOLUTE KILL SWITCH ENGAGED]"
        }.get(level, "[INFO]")

        formatted = f"{prefix} {title}\n{message}"
        console.print(f"[bold cyan]{formatted}[/bold cyan]")

        # Push to Telegram if configured
        if self.telegram_token and self.chat_id:
            tg_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": formatted,
                "parse_mode": "Markdown"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(tg_url, json=payload, timeout=5) as resp:
                        pass
            except Exception as e:
                console.print(f"[red]Failed to send Telegram alert: {e}[/red]")

        # Push to Discord Webhook if configured
        if self.discord_url:
            dc_payload = {"content": f"**{prefix} {title}**\n```{message}```"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.discord_url, json=dc_payload, timeout=5) as resp:
                        pass
            except Exception as e:
                console.print(f"[red]Failed to send Discord webhook: {e}[/red]")
