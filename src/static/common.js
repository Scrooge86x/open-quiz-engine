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
