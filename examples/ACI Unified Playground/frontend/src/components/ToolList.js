import React, { useState, useEffect } from 'react';
import './ToolList.css';

function ToolList() {
  const [tools, setTools] = useState([]);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const response = await fetch('http://localhost:8000/tools');
        if (!response.ok) {
          throw new Error('Failed to fetch tools');
        }
        const data = await response.json();
        setTools(data.tools);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchTools();
  }, []);

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const toolsToDisplay = isExpanded ? tools : tools.slice(0, 10);

  return (
    <div className="tool-list-container">
      <h3 className="tool-list-title">AGENT TOOLS LOADED</h3>
      {error && <p className="tool-list-error">Error: {error}</p>}
      <ul className="tool-list">
        {toolsToDisplay.map((tool) => (
          <li key={tool.name} className="tool-item" title={tool.description}>
            {tool.name}
          </li>
        ))}
        {tools.length > 10 && (
          <li
            className="tool-item more-tools"
            onClick={handleToggleExpand}
            title={isExpanded ? 'Show fewer tools' : 'Show all tools'}
          >
            {isExpanded ? 'Show less' : '...'}
          </li>
        )}
      </ul>
    </div>
  );
}

export default ToolList; 