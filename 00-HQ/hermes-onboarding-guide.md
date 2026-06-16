# Hermes Onboarding Guide — For Vanito & Daydron

A non-technical, step-by-step guide to getting a GenTech-flavored Hermes agent running.

**Why this exists:** Jordan wants to share his agent setup, but the manual install is technical even for him. This guide separates what Jordan prepares from what the new user does.

---

## What Jordan Prepares First (One-Time)

Before Vanito or Daydron start, Jordan exports his GenTech profile as a starter pack.

```bash
hermes profile export gentech-starter
```

This creates a file like `gentech-starter.tar.gz`. Share this securely (Telegram file, cloud link, etc.).

**What the starter pack includes:**
- All GenTech skills
- Cron job templates
- Dashboard config
- Toolset preferences

**What it does NOT include (they add these themselves):**
- API keys / LLM access
- Their Telegram bot token
- Their wallet address
- Their GitHub credentials

---

## What Vanito / Daydron Need Before Starting

1. A computer running one of:
   - **Windows 10/11** with WSL2 installed
   - **macOS** (Intel or Apple Silicon)
   - **Linux** (Ubuntu recommended)

2. An internet connection

3. Their own API key for the AI model (Jordan will help pick one — OpenCode Go is ~$10/mo and recommended)

4. A Telegram account (to talk to their agent)

5. Patience. The first setup takes 30–60 minutes.

---

## Step 1: Install Hermes

Open a terminal.

**On Windows:**
- Press `Win + R`, type `wt`, press Enter. This opens Windows Terminal.
- Make sure WSL2 is installed. If not, Jordan helps or see Microsoft’s WSL guide.

**On Mac:**
- Press `Cmd + Space`, type `Terminal`, press Enter.

**On Linux:**
- Press `Ctrl + Alt + T` or search for Terminal.

Then paste this command and press Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Wait. It downloads and installs Hermes. When it finishes, close and reopen the terminal.

---

## Step 2: Import the GenTech Starter Pack

Jordan sends you a file named something like `gentech-starter.tar.gz`.

Save it to your computer. Then in the terminal, run:

```bash
hermes profile import /path/to/gentech-starter.tar.gz
```

Replace `/path/to/` with the actual location. On most systems you can drag the file into the terminal and it will auto-fill the path.

Then switch to the imported profile:

```bash
hermes profile use gentech
```

---

## Step 3: Add Your AI Model API Key

Hermes needs an AI model to think. Jordan recommends **OpenCode Go** (~$10/month, good for coding tasks).

1. Go to https://opencode.ai and sign up
2. Copy your API key
3. In the terminal, run:

```bash
hermes config edit
```

This opens a config file. Find the section that says `model:` and add or update:

```yaml
model:
  default: mimo-v2.5
  provider: opencode-go
  api_key: your-opencode-go-key-here
```

Save the file and close the editor.

**Alternative:** If you don’t want to pay, ask Jordan about using a free-tier provider.

---

## Step 4: Connect Telegram

This lets you text your agent like you text Jordan.

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow the prompts to create a bot name and username
4. @BotFather will give you a token that looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxyz
   ```
5. Save that token somewhere safe
6. In the terminal, run:

```bash
hermes gateway setup
```

Choose **Telegram** and paste your token when asked.

7. Start the gateway:

```bash
hermes gateway run
```

Leave this running. Now you can message your bot and it will respond.

**To keep it running 24/7:** This requires a server or leaving your computer on. For now, just run it when you want to use it. Later, Jordan can help set up a VPS.

---

## Step 5: Test It

Send your bot a message like:

```
Hello, what can you do?
```

It should reply. If it does, the agent is working.

---

## Step 6: Add Personal Config (Optional)

If you want the DeFi dashboard and LP monitor to work for you:

1. Get your wallet address from MetaMask
2. Ask the agent:
   ```
   Update my DeFi config with wallet 0x... and range ...
   ```
   (Jordan can help you find the exact values.)

3. The agent will update the config files for you.

---

## Common Problems

### “command not found: hermes”
Close the terminal and reopen it. If it still doesn’t work, restart the computer.

### Config file won’t save
Make sure you close the text editor after saving. If using `nano`, press `Ctrl + O`, then Enter, then `Ctrl + X`.

### Telegram bot doesn’t respond
- Make sure you messaged the bot first (open the chat and send `/start`)
- Make sure `hermes gateway run` is still running in a terminal window
- Check that you pasted the token correctly

### Agent responds but can’t use tools
Some tools need API keys. Ask the agent:
```
Which tools are missing credentials?
```
It will tell you what to add.

---

## Support Flow

If something breaks:

1. Take a screenshot of the error
2. Send it to Jordan
3. Jordan can either fix it remotely or ask the agent to help

**Do not share:**
- API keys
- Wallet private keys
- Bot tokens

---

## Next Level (Later)

Once the basics work:
- Move the agent to a cheap VPS so it runs 24/7 (~$5–10/month)
- Add more skills from the Hermes skill hub
- Connect Discord or other platforms
- Customize the agent’s personality

---

*Last updated: 2026-06-16*
