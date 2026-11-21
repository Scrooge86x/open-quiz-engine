async function apiRequest(method, path, body) {
  const options = {
    method: method,
    headers: {},
  };

  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(path, options);
  } catch (networkError) {
    throw new Error("Something went wrong. Please try again.");
  }

  if (!response.ok) {
    let data = null;
    try {
      data = await response.json();
    } catch {
      // Body is not JSON
    }

    const message =
      data && typeof data.message === "string" && data.message.length > 0
        ? data.message
        : "Something went wrong. Please try again.";

    const error = new Error(message);
    if (data && data.error) {
      error.code = data.error;
    }
    throw error;
  }

  return await response.json();
}

function showError(message) {
  const errorBox = document.getElementById("error-box");
  if (errorBox) {
    errorBox.textContent = message;
    errorBox.style.display = "block";
  }
}

function clearError() {
  const errorBox = document.getElementById("error-box");
  if (errorBox) {
    errorBox.textContent = "";
    errorBox.style.display = "none";
  }
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined || isNaN(seconds)) {
    return "-";
  }
  return `${Number(seconds).toFixed(1)} s`;
}

function renderLeaderboard(entries, tableEl, bodyEl, emptyEl) {
  if (!Array.isArray(entries) || entries.length === 0) {
    if (emptyEl) {
      emptyEl.style.display = "block";
    }
    if (tableEl) {
      tableEl.style.display = "none";
    }
    return;
  }

  if (emptyEl) {
    emptyEl.style.display = "none";
  }

  if (bodyEl) {
    bodyEl.replaceChildren();
    for (const entry of entries) {
      const row = document.createElement("tr");

      const rankCell = document.createElement("td");
      rankCell.textContent = entry.rank;
      row.appendChild(rankCell);

      const nickCell = document.createElement("td");
      nickCell.textContent = entry.nick;
      row.appendChild(nickCell);

      const scoreCell = document.createElement("td");
      scoreCell.textContent = entry.score;
      row.appendChild(scoreCell);

      const timeCell = document.createElement("td");
      timeCell.textContent = formatDuration(entry.duration_seconds);
      row.appendChild(timeCell);

      bodyEl.appendChild(row);
    }
  }

  if (tableEl) {
    tableEl.style.display = "table";
  }
}
