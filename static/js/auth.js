// =========================================================
// auth.js — handles auth.html only (login / signup)
// =========================================================
const API_BASE_URL = "http://127.0.0.1:8000";

const tabLogin = document.getElementById("tab-login");
const tabSignup = document.getElementById("tab-signup");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const loginError = document.getElementById("login-error");
const signupError = document.getElementById("signup-error");

// If already logged in, skip straight to chat.
(function redirectIfLoggedIn() {
  const token = localStorage.getItem("access_token");
  if (token) window.location.href = "chat.html";
})();

// --- Tab switching ---------------------------------------------------------
if (tabLogin && tabSignup) {
  tabLogin.addEventListener("click", () => {
    tabLogin.classList.add("active");
    tabSignup.classList.remove("active");
    loginForm.classList.add("active");
    signupForm.classList.remove("active");
    loginError.innerText = "";
    signupError.innerText = "";
  });

  tabSignup.addEventListener("click", () => {
    tabSignup.classList.add("active");
    tabLogin.classList.remove("active");
    signupForm.classList.add("active");
    loginForm.classList.remove("active");
    loginError.innerText = "";
    signupError.innerText = "";
  });
}

// --- Signup ------------------------------------------------------------
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    signupError.innerText = "";

    const name = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;

    try {
      const response = await fetch(`${API_BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json();

      if (response.ok) {
        alert("Account created successfully! Please sign in.");
        signupForm.reset();
        tabLogin.click();
      } else {
        signupError.innerText = data.detail || "Signup failed.";
      }
    } catch (err) {
      console.error("Signup error:", err);
      signupError.innerText = "Unable to connect to the backend server.";
    }
  });
}

// --- Login ---------------------------------------------------------------
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.innerText = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_email", data.email || email);
        window.location.href = "chat.html";
      } else {
        loginError.innerText = data.detail || "Invalid credentials.";
      }
    } catch (err) {
      console.error("Login error:", err);
      loginError.innerText = "Unable to connect to the backend server.";
    }
  });
}