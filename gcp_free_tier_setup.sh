# GCP FREE TIER SETUP SCRIPT (Automates setup on an e2-micro instance)
# Run these commands inside your Google Cloud VM SSH terminal:

# 1. Update system & install Python and Git
sudo apt update && sudo apt install -y python3-pip python3-venv git tmux

# 2. Clone or upload your bot folder:
# (If using git) git clone <your-repo-url>
# cd Apex-Sovereign-Bot

# 3. Create virtual environment & install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run 24/7 inside tmux (stays alive even when you close SSH terminal):
tmux new -s tradingbot
python3 -m src.web.server

# Press Ctrl+B then D to detach from tmux. The bot will now run 24/7 forever for $0!
