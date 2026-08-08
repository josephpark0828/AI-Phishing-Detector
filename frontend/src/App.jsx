import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyzeMessage() {
    const cleanedMessage = message.trim();

    if (!cleanedMessage) {
      setError("Please enter a message.");
      setPrediction(null);
      return;
    }

    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: cleanedMessage,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "The analysis request failed."
        );
      }

      setPrediction(data);
    } catch (requestError) {
      console.error(requestError);

      setError(
        requestError.message ||
          "Could not connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const phishingPercentage = prediction
    ? Math.round(prediction.phishing_probability * 100)
    : null;

  return (
    <div className="page">
      <div className="card">
        <h1>Phishing Message Detector</h1>

        <p>
          Paste a message below to check whether it may be
          phishing.
        </p>

        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Paste suspicious message here..."
          disabled={loading}
        />

        <button
          type="button"
          onClick={analyzeMessage}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Message"}
        </button>

        <div className="result">
          {error && <strong>{error}</strong>}

          {!error && !prediction && (
            <strong>Result will appear here.</strong>
          )}

          {prediction && (
            <>
              <strong>{prediction.result}</strong>

              <p>
                Phishing probability: {phishingPercentage}%
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;