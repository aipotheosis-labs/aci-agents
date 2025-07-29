# Voice Webpage Summarizer

This demo is a voice-enabled webpage summarization tool built with **Next.js** and **ACI.dev**, using the EXA AI and Slack Integrations. You can either speak or type out a URL to get instant AI-generated summaries with real-time Slack notifications.

## Features

- **Voice Commands**: Speak URLs naturally - for example "summarize github.com" or "summarize https://example.com"
- **Text Input**: Traditional URL input for manual entry
- **Smart Content Extraction**: Uses advanced web scraping to extract clean content
- **AI Summarization**: Leverages Exa AI via ACI.dev for intelligent, structured summaries
- **Slack Integration**: Also Leverages Slack via ACI.dev for automatic notifications sent to your Slack channel 

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd vocalops-nextjs
npm install
```

### 2. Environment Setup

Create a `.env.local` file in the root directory:

```env
# Required: ACI.dev API Key
ACI_API_KEY=your_aci_api_key_here
LINKED_ACCOUNT_OWNER_ID=your_linked_account_owner_id_here
```

### 3. Configure ACI.dev

1. Go to [ACI.dev Platform](https://platform.aci.dev)
2. Configure **Exa AI** for web search and content extraction
3. Configure **Slack** for notifications on summaries

### 4. Run the Application

```bash
npm run dev
```

Visit `http://localhost:3000` and start summarizing webpages with your voice!

## Usage

### Voice Commands
1. **Click "Start Voice Command"** 
2. **Speak naturally**: "summarize github.com" or "summarize https://example.com"
3. **Get instant results** - AI-generated summary with Slack notification

### Text Input
1. **Paste a URL** in the input field
2. **Click "Go"** or press Enter
3. **Get instant results** - AI-generated summary with Slack notification

### Example Voice Commands
- "summarize github.com"
- "summarize https://blog.openai.com"
- "summarize nextjs.org/blog"
- "summarize dev.to/microtica/amazon-bedrock"

## Architecture

```
Voice Input / Text Input
    ↓
URL Extraction & Validation
    ↓
Exa AI (Content Extraction & Summarization)
    ↓
Slack Notification
    ↓
Formatted Summary Output
```

## How It Works

1. **Voice Recognition**: Uses Web Speech API to capture voice input
2. **URL Extraction**: Intelligently extracts URLs from voice or text input
3. **Content Processing**: Uses Exa AI to extract and summarize webpage content
4. **Slack Integration**: Automatically sends summaries to configured Slack channel
5. **Rich Output**: Returns formatted markdown with structured summaries

## Demo Video
To see how this project works, watch this video below: 
