import './App.css'

function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">RU</div>
        <nav className="nav">
          <button className="nav-item">Home</button>
          <button className="nav-item">Projects</button>
          <button className="nav-item">Settings</button>
        </nav>
      </aside>
      <main className="main">
        <div className="cards">
          <div className="card">
            <h2>Card One</h2>
            <p>This is the first card with some placeholder content. You can add your Google Gemini API integration here.</p>
          </div>
          <div className="card">
            <h2>Card Two</h2>
            <p>This is the second card where you can add more functionality for your hackathon project.</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
