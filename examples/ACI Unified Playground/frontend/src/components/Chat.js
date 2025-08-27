import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import ToolList from './ToolList';
import './Chat.css';

function Chat({ promptText }) {
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: '🚀 Welcome to the **ACI Unified Playground**! \n\nI have access to 600+ tools through ACI.dev\'s Unified MCP Server. I can help you with:\n\n• **Memory Management**\n  Store and retrieve personal information\n\n• **Web Search**\n  Find current information and research\n\n• **Email Operations**\n  Manage your email inbox\n\n• **Database Queries**\n  Connect to and query your databases\n\n• **Multi-tool Workflows**\n  Combine multiple tools for complex tasks\n\nClick any prompt from the sidebar to explore different capabilities, or tell me what you\'d like to accomplish!',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // When a prompt is clicked in the side panel, update the input field
    if (promptText) {
      setInputValue(promptText);
    }
  }, [promptText]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: inputValue }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      let agentResponseText = "Sorry, I couldn't get a response.";
      let executedTools = [];
      let toolDetails = [];

      if (data.error) {
        agentResponseText = data.error;
      } else if (data.response) {
        agentResponseText = data.response;
        executedTools = data.executed_tools || [];
        toolDetails = data.tool_details || [];
      }

      const agentMessage = {
        sender: 'agent',
        text: agentResponseText,
        executed_tools: executedTools,
        tool_details: toolDetails,
      };
      setMessages((prevMessages) => [...prevMessages, agentMessage]);
    } catch (error) {
      console.error('Error communicating with the agent:', error);
      const errorMessage = {
        sender: 'agent',
        text: 'I am having trouble connecting to my brain right now. Please try again later.',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <ToolList />
      <div className="messages-window">
        {messages.map((msg, index) => (
          <Message key={index} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      {isLoading && (
        <div className="loading-indicator-wrapper">
          <div className="loading-dots">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
          <span>Agent is thinking...</span>
        </div>
      )}
      <div className="input-area">
        <form onSubmit={handleSendMessage} className="input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Try any ACI tool: memory, search, email, database operations..."
            autoFocus
            disabled={isLoading}
          />
          <button type="submit" disabled={!inputValue.trim() || isLoading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat; 