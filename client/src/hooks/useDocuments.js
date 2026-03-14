import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.listDocuments();
      setDocuments(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const searchDocuments = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await api.search(query);
      setSearchResults(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadDocument = async (file) => {
    setLoading(true);
    setError(null);
    try {
      await api.uploadDocument(file);
      await fetchDocuments();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const selectDocument = async (id) => {
    setLoading(true);
    try {
      const response = await api.getDocument(id);
      setSelectedDoc(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id) => {
    setLoading(true);
    setError(null);
    try {
      await api.deleteDocument(id);
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
      }
      await fetchDocuments();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return {
    documents,
    searchResults,
    loading,
    error,
    selectedDoc,
    fetchDocuments,
    searchDocuments,
    uploadDocument,
    selectDocument,
    deleteDocument,
    setSelectedDoc,
  };
}
