// =========================================================
// chat.js — handles chat.html only
// =========================================================
const API_BASE_URL = "http://127.0.0.1:8000";

const userDisplayName = document.getElementById("user-display-name");
const logoutBtn = document.getElementById("logout-btn");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const optionPills = document.querySelectorAll(".quick-options .option-pill");
const histList = document.getElementById("hist-list");

// --- Auth guard: bounce to auth.html if not logged in ---------------------
const token = localStorage.getItem("access_token");
const userEmail = localStorage.getItem("user_email");

if (!token) {
  window.location.href = "auth.html";
} else {
  if (userDisplayName) userDisplayName.innerText = userEmail || "Active Session";
  ensureConversationId();
  loadChatHistory();
  loadConversationList();
}

// --- Conversation (session) management --------------------------------------
function newConversationId() {
  return (crypto.randomUUID && crypto.randomUUID()) ||
    `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function ensureConversationId() {
  if (!localStorage.getItem("current_conversation_id")) {
    localStorage.setItem("current_conversation_id", newConversationId());
  }
}

function currentConversationId() {
  return localStorage.getItem("current_conversation_id") || "default";
}

function startNewConsultation() {
  localStorage.setItem("current_conversation_id", newConversationId());
  chatMessages.innerHTML = "";
  appendMessage(
    "Hello! Describe your symptoms or medical concerns below to begin your consultation.",
    "bot"
  );
  chatInput.value = "";
  chatInput.focus();
  highlightActiveConversation();
}

function switchConversation(conversationId) {
  localStorage.setItem("current_conversation_id", conversationId);
  loadChatHistory();
  highlightActiveConversation();
}

async function loadConversationList() {
  if (!histList) return;
  try {
    const response = await fetch(`${API_BASE_URL}/chat/conversations`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    if (!response.ok) return;

    const data = await response.json();
    histList.innerHTML = "";

    (data.conversations || []).forEach((conv) => {
      const item = document.createElement("div");
      item.className = "hist-item";
      item.dataset.conversationId = conv.conversation_id;
      item.textContent = conv.title;
      item.addEventListener("click", () => switchConversation(conv.conversation_id));
      histList.appendChild(item);
    });

    highlightActiveConversation();
  } catch (err) {
    console.error("Could not load conversation list:", err);
  }
}

function highlightActiveConversation() {
  if (!histList) return;
  const current = currentConversationId();
  histList.querySelectorAll(".hist-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.conversationId === current);
  });
}

const newConsultationBtn = document.getElementById("new-consultation-btn");
if (newConsultationBtn) newConsultationBtn.addEventListener("click", startNewConsultation);

// --- Sending a message -----------------------------------------------------
const sendBtn = document.getElementById("send-btn");

function sendMessage() {
  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  if (!localStorage.getItem("access_token")) {
    alert("Session expired. Please log in again.");
    handleLogout();
    return;
  }

  appendMessage(userMessage, "user");
  chatInput.value = "";

  const thinkingId = appendMessage("E-Ilaaj is thinking...", "system");

  (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ message: userMessage, conversation_id: currentConversationId() }),
      });

      const data = await response.json();
      removeMessage(thinkingId);

      if (response.ok) {
        appendMessage(data.reply || "How can I help you?", "bot");
        loadConversationList();
      } else if (response.status === 401) {
        alert("Session expired. Please log in again.");
        handleLogout();
      } else {
        appendMessage(`Error: ${data.detail || "Failed to process"}`, "bot");
      }
    } catch (err) {
      console.error("Chat error:", err);
      removeMessage(thinkingId);
      appendMessage("Network error: could not reach the server.", "bot");
    }
  })();
}

if (sendBtn) sendBtn.addEventListener("click", sendMessage);
if (chatInput) {
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });
}

// --- Quick-option pills fill the input and send -----------------------------
optionPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    chatInput.value = pill.textContent;
    sendMessage();
  });
});

// --- Load history on page load --------------------------------------------
async function loadChatHistory() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/chat/history?conversation_id=${encodeURIComponent(currentConversationId())}`,
      { headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` } }
    );

    if (response.ok) {
      const data = await response.json();
      chatMessages.innerHTML = "";

      if (data.history && data.history.length > 0) {
        data.history.forEach((item) => appendMessage(item.message, item.sender));
      } else {
        appendMessage(
          "Hello! Describe your symptoms or medical concerns below to begin your consultation.",
          "bot"
        );
      }
    } else if (response.status === 401) {
      handleLogout();
    }
  } catch (err) {
    console.error("History load error:", err);
  }
}

// --- Logout ------------------------------------------------------------
function handleLogout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_email");
  localStorage.removeItem("current_conversation_id");
  window.location.href = "auth.html";
}

if (logoutBtn) logoutBtn.addEventListener("click", handleLogout);

// --- Message rendering helpers ---------------------------------------------
function appendMessage(text, sender) {
  const messageDiv = document.createElement("div");
  const uniqueId = `msg-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
  messageDiv.id = uniqueId;

  if (sender === "user") {
    messageDiv.className = "message user-msg";
    messageDiv.innerText = text;
  } else if (sender === "bot") {
    messageDiv.className = "message bot-msg";
    messageDiv.innerHTML = `<strong>E-Ilaaj:</strong><br>${formatBotText(text)}`;
  } else {
    messageDiv.className = "message system-msg";
    messageDiv.innerText = text;
  }

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return uniqueId;
}

function removeMessage(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.remove();
}

// Minimal markdown -> HTML: "## Heading" and "- bullet" lines only.
function formatBotText(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const lines = escaped.split("\n");
  let html = "";
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("## ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<div style="margin-top:14px;font-weight:700;color:var(--brass-bright);">${trimmed.slice(3)}</div>`;
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) { html += '<ul style="margin:6px 0 6px 18px;padding:0;">'; inList = true; }
      html += `<li>${trimmed.slice(2)}</li>`;
    } else if (trimmed === "") {
      if (inList) { html += "</ul>"; inList = false; }
      html += "<br>";
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      html += `${trimmed}<br>`;
    }
  }
  if (inList) html += "</ul>";
  return html;
}
