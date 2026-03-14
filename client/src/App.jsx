import { useState } from 'react'
import { DocumentsTab } from './components/DocumentsTab'
import { ChatTab } from './components/ChatTab'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('documents')

  return (
    <div className="app">
      <nav className="topbar">
        <div className="brand">
          <span>◈</span> RAG-SSW
        </div>
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            📄 Документы
          </button>
          <button 
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Чат
          </button>
        </div>
      </nav>
      
      <main className="content">
        {activeTab === 'documents' ? (
          <DocumentsTab />
        ) : (
          <ChatTab />
        )}
      </main>
    </div>
  )
}

export default App
