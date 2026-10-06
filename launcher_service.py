import os
import sys
import time
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(os.environ.get("USERPROFILE", "C:/Users/rehan")) / "Desktop"
TUNNEL_LOG = BASE_DIR / "tunnel.log"
URL_SHORTCUT = DESKTOP_DIR / "Apex Sovereign Trading Bot.url"
URL_TXT = DESKTOP_DIR / "APEX_LIVE_URL.txt"

def is_server_alive():
    import urllib.request
    try:
        req = urllib.request.urlopen("http://localhost:8000/api/status", timeout=2)
        return req.getcode() == 200
    except Exception:
        return False

def update_desktop_shortcuts(url: str):
    try:
        # Create Windows Internet Shortcut
        with open(URL_SHORTCUT, "w", encoding="utf-8") as f:
            f.write(f"[InternetShortcut]\nURL={url}\nIconIndex=0\n")
        
        # Create text file with full details
        with open(URL_TXT, "w", encoding="utf-8") as f:
            f.write(
                f"===========================================================\n"
                f"     APEX SOVEREIGN ALGORITHMIC TRADING CITADEL (24/7)\n"
                f"===========================================================\n\n"
                f"YOUR LIVE CLOUD LINK (Access from any phone or PC):\n"
                f"{url}\n\n"
                f"LOCAL ADDRESS (On this computer):\n"
                f"http://localhost:8000\n\n"
                f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Status: ONLINE & ACTIVELY TRADING 24/7\n"
                f"===========================================================\n"
            )
        print(f"[SUCCESS] Desktop links updated: {url}")
    except Exception as e:
        print(f"[WARN] Failed to write desktop link: {e}")

def main():
    print("[INIT] Starting Apex Sovereign 24/7 Background Service...")
    os.chdir(str(BASE_DIR))

    # 1. Start Web Server if not already running
    server_proc = None
    if not is_server_alive():
        print("[INIT] Launching Apex Sovereign Engine on port 8000...")
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "src.web.server"],
            cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        time.sleep(3)

    # 2. Prepare tunnel log
    if TUNNEL_LOG.exists():
        try:
            TUNNEL_LOG.unlink()
        except Exception:
            pass

    # 3. Start Cloudflare Tunnel
    cloudflared_exe = BASE_DIR / "cloudflared.exe"
    if not cloudflared_exe.exists():
        cloudflared_exe = "cloudflared"

    print("[INIT] Launching Cloudflare Tunnel...")
    tunnel_proc = subprocess.Popen(
        [str(cloudflared_exe), "tunnel", "--url", "http://localhost:8000", "--logfile", str(TUNNEL_LOG)],
        cwd=str(BASE_DIR),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # 4. Extract URL from log
    captured_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    
    for _ in range(40):
        time.sleep(1)
        if TUNNEL_LOG.exists():
            try:
                content = TUNNEL_LOG.read_text(encoding="utf-8", errors="ignore")
                match = url_pattern.search(content)
                if match:
                    captured_url = match.group(0)
                    print(f"\n[ONLINE] Live URL generated: {captured_url}")
                    update_desktop_shortcuts(captured_url)
                    break
            except Exception:
                pass

    print("[ACTIVE] Apex Sovereign Bot is running 24/7 in the background.")
    
    # 5. Continuous Supervisor loop
    try:
        while True:
            time.sleep(10)
            # Recheck health
            if server_proc and server_proc.poll() is not None:
                print("[SUPERVISOR] Web server exited, restarting...")
                server_proc = subprocess.Popen(
                    [sys.executable, "-m", "src.web.server"],
                    cwd=str(BASE_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
            if tunnel_proc and tunnel_proc.poll() is not None:
                print("[SUPERVISOR] Tunnel exited, restarting...")
                tunnel_proc = subprocess.Popen(
                    [str(cloudflared_exe), "tunnel", "--url", "http://localhost:8000", "--logfile", str(TUNNEL_LOG)],
                    cwd=str(BASE_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
    except KeyboardInterrupt:
        print("[SHUTDOWN] Stopping services...")
        if server_proc: server_proc.terminate()
        if tunnel_proc: tunnel_proc.terminate()

if __name__ == "__main__":
    main()
