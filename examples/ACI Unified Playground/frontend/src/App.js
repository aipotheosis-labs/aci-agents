import React, { useState } from 'react';
import './App.css';
import ProjectInfo from './components/ProjectInfo';
import Chat from './components/Chat';

function App() {
  const [promptText, setPromptText] = useState('');

  return (
    <div className="App">
      <div className="main-layout">
        <div className="left-panel">
          <ProjectInfo onPromptClick={setPromptText} />
        </div>
        <div className="right-panel">
          <Chat promptText={promptText} />
        </div>
      </div>
    </div>
  );
}

export default App;
