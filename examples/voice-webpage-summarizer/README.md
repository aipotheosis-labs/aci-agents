# Voice Webpage Summarizer

A modern, voice-enabled webpage summarization tool built with **Next.js**, **ACI.dev**, and **Slack integration**. Speak a URL or paste it to get instant AI-generated summaries with automatic Slack notifications.

## Features

- **Voice Commands**: Speak URLs naturally - "summarize github.com" or "summarize https://example.com"
- **Text Input**: Traditional URL input for manual entry
- **Smart Content Extraction**: Uses advanced web scraping to extract clean content
- **AI Summarization**: Leverages Exa AI via ACI.dev for intelligent, structured summaries
- **Slack Integration**: Automatic notifications sent to your Slack channel
- **Dark Mode**: Beautiful responsive design with dark/light theme support
- **Real-time Processing**: Instant feedback with loading states and error handling
- **TypeScript**: Built with Next.js 15 and TypeScript for reliability

## Tech Stack

- **Next.js 15** - React framework with App Router
- **ACI.dev** - AI agent orchestration and tool management
- **Exa AI** - Advanced web search and content extraction
- **Slack API** - Automated notifications and messaging
- **TypeScript** - Type safety and developer experience
- **Tailwind CSS** - Modern, responsive styling
- **React Markdown** - Rich text rendering
- **Web Speech API** - Voice recognition capabilities

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

# Optional: Slack Channel ID for notifications
SLACK_CHANNEL_ID=your_channel_id_here
```

### 3. Configure ACI.dev

1. Go to [ACI.dev Platform](https://platform.aci.dev)
2. Configure **Exa AI** for web search and content extraction
3. Configure **Slack** integration for notifications (optional)

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
Slack Notification (Optional)
    ↓
Formatted Summary Output
```

## API Endpoints

### POST `/api/summarize`

Summarizes a webpage using Exa AI and optionally sends to Slack.

**Request:**
```json
{
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "## Summary\n\n**Key Points:**\n• Point 1\n• Point 2\n\n**Main Topics:**\n• Topic 1\n• Topic 2"
}
```

## How It Works

1. **Voice Recognition**: Uses Web Speech API to capture voice input
2. **URL Extraction**: Intelligently extracts URLs from voice or text input
3. **Content Processing**: Uses Exa AI to extract and summarize webpage content
4. **Slack Integration**: Automatically sends summaries to configured Slack channel
5. **Rich Output**: Returns formatted markdown with structured summaries

## Voice Recognition Features

- **Natural Language Processing**: Understands various ways to say URLs
- **Timeout Protection**: 10-second timeout with user feedback
- **Error Handling**: Comprehensive error messages for different scenarios
- **HTTPS Requirement**: Secure connection required for voice features
- **Browser Compatibility**: Works with Chrome, Safari, and other modern browsers

## Troubleshooting

### Voice Recognition Issues
- **"HTTPS Required"**: Voice recognition needs a secure connection
- **"Permission Denied"**: Allow microphone access in browser settings
- **"No Speech Detected"**: Speak more clearly or check microphone
- **"Browser Not Supported"**: Use Chrome, Safari, or other modern browsers

### ACI.dev Issues
- **"Function not found"**: Ensure Exa AI is configured in your ACI.dev account
- **"Invalid API key"**: Check your ACI_API_KEY in `.env.local`
- **"No summary generated"**: Verify Exa AI configuration in ACI.dev

### Slack Integration Issues
- **"No Slack messages"**: Check Slack integration in ACI.dev
- **"Wrong channel"**: Verify SLACK_CHANNEL_ID environment variable
- **"Function not found"**: Ensure Slack integration is enabled

## Browser Support

- **Voice Recognition**: Chrome, Safari, Edge (requires HTTPS)
- **Text Input**: All modern browsers
- **Dark Mode**: All browsers with CSS support

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme detection
- **Loading States**: Visual feedback during processing
- **Error Handling**: Clear error messages and recovery options
- **Accessibility**: Keyboard navigation and screen reader support

## Development

This project demonstrates:
- **Voice-first UX** with Web Speech API
- **Modern React patterns** with Next.js 15 App Router
- **AI integration** via ACI.dev platform
- **Real-time notifications** with Slack
- **TypeScript** for type safety
- **Responsive design** with Tailwind CSS

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for your own applications!

## Related Documentation

- [Environment Setup](./ENVIRONMENT_SETUP.md) - Detailed setup instructions
- [Slack Integration](./SLACK_SETUP.md) - Slack configuration guide
- [ACI.dev Documentation](https://docs.aci.dev) - Platform documentation
