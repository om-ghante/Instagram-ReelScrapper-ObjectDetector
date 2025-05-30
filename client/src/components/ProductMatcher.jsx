import React, { useState } from 'react';

const ProductMatcher = () => {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/process-instagram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        let errorMessage = `Request failed with status ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          console.error('Error parsing error response:', e);
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (!data.results) {
        throw new Error("No results found in response");
      }
      
      setResults(data.results);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message || 'Failed to process Instagram URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="matcher-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste Instagram Reel/Post URL"
          required
          pattern="https?://(www\.)?instagram\.com/.*"
          title="Please enter a valid Instagram URL"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Find Products'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {results && (
        <div className="results-section">
          <h2>Matching Products</h2>
          {results.map((result, index) => (
            <div key={index} className="object-group">
              <h3>Detected: {result.object} ({(result.confidence * 100).toFixed(1)}% confidence)</h3>
              <div className="product-grid">
                {result.matches.length > 0 ? (
                  result.matches.map((match, idx) => (
                    <div key={idx} className="product-card">
                      <img 
                        src={match.image_url} 
                        alt={match.name} 
                        onError={(e) => e.target.src = 'fallback.jpg'}
                      />
                      <div className="product-info">
                        <h4>{match.name}</h4>
                        <p>Similarity: {(match.similarity_score * 100).toFixed(1)}%</p>
                        <button>View Product</button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>No matches found for this object</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductMatcher;