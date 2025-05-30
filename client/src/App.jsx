import React from 'react';
import ProductMatcher from './components/ProductMatcher';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Instagram Product Finder</h1>
      </header>
      <main>
        <ProductMatcher />
      </main>
    </div>
  );
}

export default App;