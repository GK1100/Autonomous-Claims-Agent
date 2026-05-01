import { useState, useCallback } from 'react'
import './App.css'

interface ClaimResponse {
  extractedFields: any;
  missingFields: string[];
  recommendedRoute: string;
  reasoning: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ClaimResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    setResult(null);
    if (!selectedFile.name.endsWith('.txt')) {
      setError("Only text (.txt) files are supported!");
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const processClaim = async () => {
    if (!file) return;
    
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Default to relative API route for Vercel deployment
    const apiUrl = import.meta.env.VITE_API_URL || '/api/process';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to process claim");
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>Autonomous Claims Agent</h1>
        <p>Drop an FNOL document below to extract, validate, and route instantly.</p>
      </div>

      <div className="glass-card">
        <div 
          className={`upload-zone ${isDragging ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input 
            type="file" 
            className="file-input" 
            accept=".txt" 
            onChange={handleChange}
          />
          <span className="upload-icon">📄</span>
          {file ? (
            <div className="upload-text" style={{color: 'var(--success)'}}>
              Selected: {file.name}
            </div>
          ) : (
            <div className="upload-text">Drag & drop your document here</div>
          )}
          <div className="upload-subtext">Only text (.txt) files are supported</div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button 
          className="button" 
          onClick={processClaim} 
          disabled={!file || isLoading}
        >
          {isLoading ? (
            <><span className="loader"></span> Processing Claim...</>
          ) : (
            'Process Claim'
          )}
        </button>

        {result && (
          <div className="result-container">
            <div className="result-header">
              <h2>Analysis Report</h2>
              <span className={`route-badge ${result.recommendedRoute.toLowerCase()}`}>
                {result.recommendedRoute.replace(/_/g, ' ')}
              </span>
            </div>

            <div className="result-section">
              <h3>Reasoning</h3>
              <div className="reasoning-box">{result.reasoning}</div>
            </div>

            <div className="result-section">
              <h3>Missing Fields ({result.missingFields.length})</h3>
              {result.missingFields.length > 0 ? (
                <div className="missing-tags">
                  {result.missingFields.map((f, i) => (
                    <span key={i} className="missing-tag">{f}</span>
                  ))}
                </div>
              ) : (
                <span className="upload-subtext">All required data extracted successfully.</span>
              )}
            </div>

            <div className="result-section">
              <h3>Extracted JSON</h3>
              <div className="json-view">
                <pre>{JSON.stringify(result.extractedFields, null, 2)}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
