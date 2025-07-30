'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [url, setUrl] = useState('');

  const formatSummary = (summary: string) => {
    const lines = summary.split('\n');
    const formattedLines = lines.map(line => {
      if (line.startsWith('**') && line.endsWith('**')) {
        return `<h3 class="text-lg font-semibold text-black dark:text-white mb-2">${line.replace(/\*\*/g, '')}</h3>`;
      } else if (line.startsWith('##')) {
        return `<h2 class="text-xl font-bold text-black dark:text-white mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">${line.replace(/##\s*/, '')}</h2>`;
      } else if (line.startsWith('#')) {
        return `<h1 class="text-2xl font-bold text-black dark:text-white mb-4">${line.replace(/^#+\s*/, '')}</h1>`;
      } else if (line.startsWith('- ') || line.startsWith('• ')) {
        return `<li class="ml-4 mb-1 text-gray-700 dark:text-gray-300">${line.replace(/^[-•]\s*/, '')}</li>`;
      } else if (line.trim() === '') {
        return '<br>';
      } else if (line.includes('**') && line.includes(':')) {
        const [key, value] = line.split(':');
        return `<div class="mb-2"><span class="font-semibold text-black dark:text-white">${key.replace(/\*\*/g, '')}:</span><span class="text-gray-700 dark:text-gray-300">${value}</span></div>`;
      } else {
        return `<p class="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">${line}</p>`;
      }
    });
    
    return formattedLines.join('');
  };

  const addMessage = (role: 'user' | 'assistant', content: string) => {
    setMessages(prev => [...prev, { role, content }]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || isLoading) return;

    setIsLoading(true);
    addMessage('user', `Analyzing: ${url}`);

    try {
      const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.success) {
        const summaryMessage = data.summary;
        addMessage('assistant', summaryMessage);
      } else {
        addMessage('assistant', `Error: ${data.error || 'Failed to process URL'}`);
      }
    } catch (error) {
      addMessage('assistant', `Network Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;
        
        if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
          addMessage('assistant', 'HTTPS Required: Speech recognition requires a secure connection. Please use the text input instead.');
          return;
        }
        
        recognition.onstart = () => {
          setIsRecording(true);
          addMessage('user', 'Listening... Speak now!');
          
          setTimeout(() => {
            if (isRecording) {
              recognition.stop();
              setIsRecording(false);
              setMessages(prev => prev.filter(msg => msg.content !== 'Listening... Speak now!'));
              addMessage('assistant', 'Timeout: No speech detected. Please try again or use the text input.');
            }
          }, 10000);
        };
        
        recognition.onresult = async (event: any) => {
          const transcribedText = event.results[0][0].transcript;
          
          setIsRecording(false);
          setMessages(prev => prev.filter(msg => msg.content !== 'Listening... Speak now!'));
          addMessage('user', `Voice Command: ${transcribedText}`);
          
          // Extract URL from voice input
          const urlRegex = /(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})(?:\/[^\s]*)?/g;
          const matches = transcribedText.match(urlRegex);
          
          if (matches && matches.length > 0) {
            let extractedUrl = matches[0];
            if (!extractedUrl.startsWith('http')) {
              extractedUrl = 'https://' + extractedUrl;
            }
            
            // Set the URL in the input field
            setUrl(extractedUrl);
            
            // Automatically submit the form
            setIsLoading(true);
            addMessage('user', `Analyzing: ${extractedUrl}`);

            try {
              const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: extractedUrl }),
              });

              const data = await response.json();

              if (data.success) {
                const summaryMessage = data.summary;
                addMessage('assistant', summaryMessage);
              } else {
                addMessage('assistant', `Error: ${data.error || 'Failed to process URL'}`);
              }
            } catch (error) {
              addMessage('assistant', `Network Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`);
            } finally {
              setIsLoading(false);
            }
          } else {
            addMessage('assistant', 'No URL found in voice input. Please try saying something like "summarize github.com" or "summarize https://example.com"');
          }
        };
        
        recognition.onerror = (event: any) => {
          setIsRecording(false);
          setMessages(prev => prev.filter(msg => msg.content !== 'Listening... Speak now!'));
          
          let errorMessage = '';
          switch (event.error) {
            case 'network':
              errorMessage = 'Network Error: Speech recognition requires an internet connection. Please try using the text input below.';
              break;
            case 'not-allowed':
              errorMessage = 'Permission Denied: Please allow microphone access in your browser settings and try again.';
              break;
            case 'no-speech':
              errorMessage = 'No Speech Detected: Please try speaking more clearly or check your microphone.';
              break;
            case 'audio-capture':
              errorMessage = 'Microphone Error: Please check your microphone connection and permissions.';
              break;
            case 'service-not-allowed':
              errorMessage = 'Service Not Allowed: Speech recognition is not available in this browser or context.';
              break;
            default:
              errorMessage = `Speech Recognition Error: ${event.error}. Please try using the text input instead.`;
          }
          
          addMessage('assistant', errorMessage);
        };
        
        recognition.onend = () => {
          setIsRecording(false);
        };
        
        recognition.start();
      } else {
        addMessage('assistant', 'Speech recognition is not supported in this browser. Please use the text input below.');
      }
    } catch (error) {
      addMessage('assistant', `Recording Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black flex items-center justify-center font-sans">
      
      <div className="w-full max-w-2xl mx-auto p-4 sm:p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-black dark:text-white mb-4 tracking-tight">
            Voice Webpage Summarizer
          </h1>
          <p className="text-base sm:text-lg text-gray-600 dark:text-gray-400 font-medium">
            Powered by ACI.dev + Slack Integration
          </p>
        </div>

        <div className="mb-6 flex justify-center">
          <button
            onClick={startRecording}
            disabled={isRecording || isLoading}
            className={`px-4 sm:px-6 py-3 rounded-full font-medium transition-all text-sm sm:text-base ${
              isRecording 
                ? 'bg-black text-white hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-200 animate-pulse' 
                : 'bg-black text-white hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-200'
            } disabled:bg-gray-400 disabled:text-gray-600 dark:disabled:bg-gray-600 dark:disabled:text-gray-400 disabled:cursor-not-allowed`}
          >
            {isRecording ? 'Listening...' : 'Start Voice Command'}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="relative">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Or paste a URL to summarize..."
              className="w-full px-4 py-3 pr-24 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent bg-white dark:bg-black text-black dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm sm:text-base"
              disabled={isLoading || isRecording}
            />
            <button
              type="submit"
              disabled={isLoading || !url.trim() || isRecording}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-black text-white rounded-md font-medium hover:bg-gray-800 disabled:bg-black disabled:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              {isLoading ? 'Processing...' : 'Go'}
            </button>
          </div>
        </form>

        <div className="space-y-4 max-h-96 overflow-y-auto">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                  : 'bg-white dark:bg-black border border-gray-200 dark:border-gray-700'
              }`}
            >
              {message.role === 'assistant' && message.content.includes('##') ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-black dark:text-white">AI Summary</h2>
                    <span className="text-sm text-gray-500 dark:text-gray-400">Generated by ACI.dev</span>
                  </div>
                  <div 
                    className="prose max-w-none dark:prose-invert prose-sm sm:prose-base"
                    dangerouslySetInnerHTML={{ __html: formatSummary(message.content) }}
                  />
                </div>
              ) : (
                <div className="prose max-w-none dark:prose-invert prose-sm sm:prose-base">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              )}
            </div>
          ))}
        </div>

        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black dark:border-white"></div>
            <p className="mt-2 text-gray-600 dark:text-gray-400">Processing your request...</p>
          </div>
        )}
      </div>
    </div>
  );
}
