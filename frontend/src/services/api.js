
const API_BASE_URL = "http://localhost:8000";

export async function processVideo(url) {
  const response = await fetch(`${API_BASE_URL}/api/videos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to process video");
  }

  return data;
}

export async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to get answer");
  }

  return data.answer;
}
