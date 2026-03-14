import { useState, useRef, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import './DocumentsTab.css';

export function DocumentsTab() {
  const {
    documents,
    searchResults,
    loading,
    error,
    selectedDoc,
    uploadDocument,
    selectDocument,
    deleteDocument,
    setSelectedDoc,
    searchDocuments,
    fetchDocuments,
  } = useDocuments();

  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const fileInputRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (searchQuery.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        searchDocuments(searchQuery);
        setShowSearchResults(true);
      }, 300);
    } else {
      setShowSearchResults(false);
      setSearchResults([]);
    }
    
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery, searchDocuments]);

  const handleFileSelect = async (file) => {
    setUploading(true);
    const success = await uploadDocument(file);
    setUploading(false);
    if (success) {
      setSearchQuery('');
      setShowSearchResults(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleSearchResultClick = (result) => {
    selectDocument(result.id);
    setShowSearchResults(false);
    setSearchQuery('');
  };

  const handleDeleteDocument = async (e, docId) => {
    e.stopPropagation();
    if (confirm('Вы уверены, что хотите удалить этот документ?')) {
      await deleteDocument(docId);
    }
  };

  const displayDocuments = showSearchResults ? searchResults : documents;

  return (
    <div className="documents-tab">
      <div className="documents-grid">
        <div className="documents-sidebar">
          <div 
            className={`upload-zone ${dragOver ? 'dragover' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="upload-icon">📤</div>
            <div className="upload-text">
              {uploading ? 'Загрузка...' : 'Перетащите файл или кликните'}
            </div>
            <div className="upload-hint">PDF, DOC, DOCX и другие</div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
              style={{ display: 'none' }}
            />
          </div>

          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input 
              type="text" 
              placeholder="Поиск по документам..." 
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {showSearchResults && searchResults.length > 0 && (
            <div className="search-results-header">
              Результаты поиска: {searchResults.length}
            </div>
          )}

          <div className="doc-list-header">
            <span>{showSearchResults ? 'Результаты' : 'База документов'}</span>
            <span className="badge">{displayDocuments.length}</span>
          </div>

          <div className="doc-list">
            {displayDocuments.map((doc) => (
              <div
                key={doc.id}
                className={`doc-item ${selectedDoc?.id === doc.id ? 'selected' : ''}`}
                onClick={() => showSearchResults ? handleSearchResultClick(doc) : selectDocument(doc.id)}
              >
                <div className="doc-name">
                  <span className="icon">📄</span>
                  {doc.filename}
                  {!showSearchResults && (
                    <button 
                      className="delete-btn"
                      onClick={(e) => handleDeleteDocument(e, doc.id)}
                      title="Удалить"
                    >
                      ×
                    </button>
                  )}
                </div>
                <div className="doc-meta">
                  <span>{doc.content_type?.split('/')[1] || 'FILE'}</span>
                  <span>{formatSize(doc.size)}</span>
                  {doc.embedded && !showSearchResults && <span className="indexed">✓</span>}
                  {showSearchResults && doc.score !== undefined && (
                    <span className="score">{Math.round(doc.score * 100)}%</span>
                  )}
                </div>
              </div>
            ))}
            {displayDocuments.length === 0 && !loading && (
              <div className="empty-list">
                {showSearchResults ? 'Ничего не найдено' : 'Нет документов'}
              </div>
            )}
          </div>
        </div>

        <div className="documents-viewer">
          {selectedDoc ? (
            <div className="doc-content">
              <div className="doc-content-header">
                <h2>{selectedDoc.filename}</h2>
                <div className="doc-status">
                  {selectedDoc.embedded ? (
                    <span className="indexed-badge">✓ Индексировано</span>
                  ) : (
                    <span className="not-indexed-badge">Не индексировано</span>
                  )}
                </div>
              </div>
              <div className="doc-content-body">
                <pre>{selectedDoc.content || 'Нет содержимого'}</pre>
              </div>
            </div>
          ) : (
            <div className="empty-viewer">
              <div className="empty-icon">📄</div>
              <div>Выберите документ для просмотра</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
