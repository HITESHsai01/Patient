// SentinelOps Patient Frontend Controller

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

function initApp() {
  checkHealth();
  loadUsers();

  // Attach Lookup Form Handler
  const lookupForm = document.getElementById("lookupForm");
  if (lookupForm) {
    lookupForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const userId = document.getElementById("userIdInput").value;
      if (userId) {
        fetchUser(userId);
      }
    });
  }

  // Attach Bug Simulation Trigger
  const triggerBugBtn = document.getElementById("triggerBugBtn");
  if (triggerBugBtn) {
    triggerBugBtn.addEventListener("click", () => {
      document.getElementById("userIdInput").value = "999";
      fetchUser("999");
    });
  }

  // Refresh Button
  const refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      checkHealth();
      loadUsers();
    });
  }
}

// 1. Live Health Probe
async function checkHealth() {
  const badge = document.getElementById("healthBadge");
  const text = document.getElementById("healthText");
  const latencyVal = document.getElementById("latencyVal");

  const start = performance.now();
  try {
    const res = await fetch("/api/health");
    const elapsed = Math.round(performance.now() - start);

    if (res.ok) {
      const data = await res.json();
      badge.className = "status-badge healthy";
      text.textContent = "System: Healthy";
      if (latencyVal) latencyVal.textContent = `${elapsed} ms`;
    } else {
      badge.className = "status-badge degraded";
      text.textContent = "System: Degraded";
      if (latencyVal) latencyVal.textContent = `${elapsed} ms`;
    }
  } catch (err) {
    badge.className = "status-badge degraded";
    text.textContent = "System: Unreachable";
    if (latencyVal) latencyVal.textContent = "Timeout";
  }
}

// 2. Load Customers List
async function loadUsers() {
  const container = document.getElementById("customerList");
  const countEl = document.getElementById("customerCount");

  try {
    const res = await fetch("/api/users");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const users = await res.json();

    if (countEl) countEl.textContent = users.length;

    container.innerHTML = "";
    users.forEach((user) => {
      const card = document.createElement("div");
      card.className = "customer-item";
      card.innerHTML = `
        <div>
          <div class="customer-id">Customer #${user.id}</div>
          <div class="customer-name">${escapeHtml(user.name)}</div>
          <div class="customer-email">${escapeHtml(user.email)}</div>
        </div>
        <div>
          <span class="status-tag ${user.status.toLowerCase()}">${user.status}</span>
        </div>
      `;
      card.addEventListener("click", () => {
        document.getElementById("userIdInput").value = user.id;
        fetchUser(user.id);
      });
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div class="error-msg" style="color:var(--error-color)">Failed to load customers: ${err.message}</div>`;
  }
}

// 3. Lookup Individual Customer (or Trigger Bug)
async function fetchUser(userId) {
  const statusEl = document.getElementById("responseStatus");
  const resultDisplay = document.getElementById("resultJson");

  statusEl.className = "response-status";
  statusEl.textContent = "Fetching...";
  resultDisplay.textContent = `GET /api/user/${userId} in progress...`;

  try {
    const res = await fetch(`/api/user/${userId}`);
    const data = await res.json();

    if (res.ok) {
      statusEl.className = "response-status ok";
      statusEl.textContent = `HTTP ${res.status} OK`;
      resultDisplay.textContent = JSON.stringify(data, null, 2);
    } else {
      statusEl.className = "response-status error";
      statusEl.textContent = `HTTP ${res.status} Error`;
      resultDisplay.textContent = JSON.stringify(data, null, 2);

      // Verify that health endpoint still returns 200 after exception
      checkHealth();
    }
  } catch (err) {
    statusEl.className = "response-status error";
    statusEl.textContent = "Network Error";
    resultDisplay.textContent = JSON.stringify({ error: err.message }, null, 2);
    checkHealth();
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
