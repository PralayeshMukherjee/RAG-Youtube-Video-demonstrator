
import { useState } from "react";
import { processVideo, askQuestion } from "./services/api";
import "./App.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [videoId, setVideoId] = useState("");
  const [messages, setMessages] = useState([]);
  const [loadingVideo, setLoadingVideo] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [error, setError] = useState("");

  async function handleVideoSubmit(e) {
    e.preventDefault();
    setError("");
    setLoadingVideo(true);

    try {
      const result = await processVideo(url);

      setVideoId(result.videoId);
      setMessages([]);
    } catch (err) {
      setError(err.message);
      setVideoId("");
    } finally {
      setLoadingVideo(false);
    }
  }

  async function handleChatSubmit(e) {
    e.preventDefault();

    const q = question.trim();
    if (!q || !videoId || loadingAnswer) return;

    setQuestion("");
    setError("");

    setMessages((prev) => [
      ...prev,
      { role: "user", text: q },
    ]);

    setLoadingAnswer(true);

    try {
      const answer = await askQuestion(q);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: answer },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAnswer(false);
    }
  }

  return (
    <main className="app">
      <h1>YouTube RAG Assistant</h1>
      <p>Ask questions and get answers from a video.</p>

      <form onSubmit={handleVideoSubmit}>
        <input
          type="url"
          placeholder="Paste YouTube video URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />

        <button type="submit" disabled={loadingVideo}>
          {loadingVideo ? "Processing..." : "Load Video"}
        </button>
      </form>

      {videoId && (
        <p className="success">
          Video loaded successfully: {videoId}
        </p>
      )}

      {error && <p className="error">{error}</p>}

      <section className="chat">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <strong>
              {message.role === "user" ? "You" : "AI"}
            </strong>
            <p>{message.text}</p>
          </div>
        ))}

        {loadingAnswer && <p>AI is thinking...</p>}
      </section>

      <form onSubmit={handleChatSubmit}>
        <input
          type="text"
          placeholder="Ask something about the video..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={!videoId || loadingAnswer}
        />

        <button
          type="submit"
          disabled={!videoId || loadingAnswer || !question.trim()}
        >
          Ask
        </button>
      </form>
    </main>
  );
}
