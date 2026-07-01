import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  return (
    <div className="page">
      <div className="card">
        <h1>Phishing Message Detector</h1>

        <p>Paste a message below to check if it may be phishing.</p>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Paste suspicious message here..."
        />

        <button>Analyze Message</button>

        <div className="result">
          <strong>Result will appear here.</strong>
        </div>
      </div>
    </div>
  );
}

export default App;