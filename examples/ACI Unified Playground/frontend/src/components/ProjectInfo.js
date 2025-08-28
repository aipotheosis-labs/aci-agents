import React, { useState, useEffect } from 'react';
import './ProjectInfo.css';

function ProjectInfo({ onPromptClick }) {
  const [config, setConfig] = useState({
    linkedAccountOwnerId: '',
    aciApiKey: ''
  });
  const [configStatus, setConfigStatus] = useState('');

  useEffect(() => {
    // Load current config on component mount
    loadCurrentConfig();
  }, []);

  const loadCurrentConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/config');
      if (response.ok) {
        const data = await response.json();
        setConfig({
          linkedAccountOwnerId: data.linkedAccountOwnerId || '',
          aciApiKey: data.aciApiKey ? '••••••••' : '' // Mask API key for display
        });
      }
    } catch (error) {
      console.warn('Could not load current config:', error);
    }
  };

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const saveConfig = async () => {
    try {
      setConfigStatus('Saving...');
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        setConfigStatus('✓ Saved! Restart server to apply changes.');
        setTimeout(() => setConfigStatus(''), 3000);
      } else {
        setConfigStatus('❌ Save failed');
        setTimeout(() => setConfigStatus(''), 3000);
      }
    } catch (error) {
      setConfigStatus('❌ Save failed');
      setTimeout(() => setConfigStatus(''), 3000);
    }
  };
  const toolCategories = [
    {
      category: "Memory Management (MEM0)",
      prompts: [
        {
          name: 'Store Personal Info',
          prompt: 'I am a software developer who loves working with Python and AI. I recently moved to San Francisco and enjoy hiking on weekends.',
        },
        {
          name: 'Retrieve Memories',
          prompt: 'What do you remember about my professional background and interests?',
        },
        {
          name: 'Update Memory',
          prompt: 'Update my location - I just moved from San Francisco to New York City.',
        },
      ]
    },
    {
      category: "Web Search (BRAVE_SEARCH)",
      prompts: [
        {
          name: 'Current Events',
          prompt: 'Search for the latest developments in artificial intelligence and large language models.',
        },
        {
          name: 'Technical Research',
          prompt: 'Find information about the newest Python web frameworks released in 2024.',
        },
        {
          name: 'Market Research',
          prompt: 'Search for current trends in remote work and developer productivity tools.',
        },
      ]
    },
    {
      category: "Email Management (GMAIL)",
      prompts: [
        {
          name: 'Check Latest Emails',
          prompt: 'Show me my latest Gmail inbox messages and summarize the important ones.',
        },
        {
          name: 'Compose Email',
          prompt: 'Help me compose and send a professional email about a project update to my team.',
        },
        {
          name: 'Search Emails',
          prompt: 'Find emails from last week that mention "meeting" or "schedule".',
        },
      ]
    },
    {
      category: "Database Operations (SUPABASE)",
      prompts: [
        {
          name: 'Query Data',
          prompt: 'Connect to my Supabase database and show me the recent user registrations.',
        },
        {
          name: 'Insert Records',
          prompt: 'Add a new record to my projects table with title "ACI Playground" and status "active".',
        },
        {
          name: 'Analytics Query',
          prompt: 'Run analytics on my user engagement data and show me the top performing features.',
        },
      ]
    },
    {
      category: "Multi-Tool Workflows",
      prompts: [
        {
          name: 'Research & Store',
          prompt: 'Search for information about GraphQL best practices and store the key insights in my memory.',
        },
        {
          name: 'Email + Database',
          prompt: 'Check my latest emails for project updates and log them in my Supabase projects database.',
        },
        {
          name: 'Full Workflow',
          prompt: 'Research the latest React 18 features, store important points in memory, and email a summary to my development team.',
        },
      ]
    }
  ];

  return (
    <div className="project-info">
      <div className="logo">
        <span className="logo-text">ACI</span>
      </div>
      <h1 className="title">ACI Unified<br />Playground</h1>
      
      <div className="powered-by">
        <p>
          Powered by{' '}
          <a
            href="https://aci.dev"
            target="_blank"
            rel="noopener noreferrer"
          >
            ACI.dev
          </a>{' '}
          Unified MCP Server
        </p>
      </div>

      <p className="description">
        Explore the power of ACI.dev's Unified MCP Server with 600+ tools at your fingertips. Test memory management, web search, email operations, database queries, and multi-tool workflows. Click any prompt below to get started.
      </p>

      <div className="config-section">
        <h3 className="config-title">Configuration</h3>
        <div className="config-inputs">
          <div className="config-input-group">
            <label htmlFor="linkedAccountOwnerId">Linked Account Owner ID</label>
            <input
              id="linkedAccountOwnerId"
              type="text"
              value={config.linkedAccountOwnerId}
              onChange={(e) => handleConfigChange('linkedAccountOwnerId', e.target.value)}
              placeholder="Enter your account ID"
              className="config-input"
            />
          </div>
          
          <div className="config-input-group">
            <label htmlFor="aciApiKey">ACI API Key</label>
            <input
              id="aciApiKey"
              type="password"
              value={config.aciApiKey}
              onChange={(e) => handleConfigChange('aciApiKey', e.target.value)}
              placeholder="Enter your ACI API key"
              className="config-input"
            />
          </div>
          
          <div className="config-actions">
            <button onClick={saveConfig} className="config-save-btn">
              Save Configuration
            </button>
            {configStatus && (
              <span className="config-status">{configStatus}</span>
            )}
          </div>
        </div>
      </div>

      <div className="features">
        {toolCategories.map((category) => (
          <div key={category.category} className="category-section">
            <h3 className="category-title">{category.category}</h3>
            <ul className="category-prompts">
              {category.prompts.map((prompt) => (
                <li key={prompt.name} onClick={() => onPromptClick(prompt.prompt)}>
                  <strong>{prompt.name}</strong>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="footer">
        ACI.dev Playground
        <span className="year">2024</span>
      </div>
    </div>
  );
}

export default ProjectInfo;