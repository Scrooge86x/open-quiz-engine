function formatDifficulty(difficulty) {
  if (!difficulty) {
    return "Any";
  }
  const normalized = String(difficulty).toLowerCase();
  if (normalized === "easy") {
    return "Easy";
  }
  if (normalized === "medium") {
    return "Medium";
  }
  if (normalized === "hard") {
    return "Hard";
  }
  return difficulty;
}

function showNotFound(message) {
  const quizView = document.getElementById("quiz-view");
  const notFoundView = document.getElementById("not-found-view");
  const notFoundMessage = document.getElementById("not-found-message");

  if (quizView) {
    quizView.style.display = "none";
  }
  if (notFoundView) {
    notFoundView.style.display = "flex";
  }
  if (notFoundMessage) {
    notFoundMessage.textContent = message;
  }
}

async function loadLeaderboard(quizId) {
  const leaderboardTable = document.getElementById("leaderboard-table");
  const leaderboardBody = document.getElementById("leaderboard-body");
  const leaderboardEmpty = document.getElementById("leaderboard-empty");

  try {
    const entries = await apiRequest(
      "GET",
      `/api/quizzes/${encodeURIComponent(quizId)}/leaderboard`
    );
    renderLeaderboard(entries, leaderboardTable, leaderboardBody, leaderboardEmpty);
  } catch (err) {
    showError(err.message);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const quizId = getQueryParam("id");
  if (!quizId) {
    showNotFound("Quiz not found.");
    return;
  }

  let quiz;
  try {
    quiz = await apiRequest("GET", `/api/quizzes/${encodeURIComponent(quizId)}`);
  } catch (err) {
    showNotFound(err.message);
    return;
  }

  const quizView = document.getElementById("quiz-view");
  if (quizView) {
    quizView.style.display = "flex";
  }

  const questionCountEl = document.getElementById("quiz-question-count");
  const difficultyEl = document.getElementById("quiz-difficulty");
  if (questionCountEl) {
    questionCountEl.textContent = quiz.question_count;
  }
  if (difficultyEl) {
    difficultyEl.textContent = formatDifficulty(quiz.difficulty);
  }

  const shareUrlInput = document.getElementById("share-url");
  if (shareUrlInput) {
    shareUrlInput.value = window.location.href;
  }

  const copyBtn = document.getElementById("copy-btn");
  const copyStatus = document.getElementById("copy-status");
  if (copyBtn && shareUrlInput && copyStatus) {
    let copyTimeoutId = null;
    copyBtn.addEventListener("click", async () => {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(shareUrlInput.value);
        } else {
          shareUrlInput.select();
          document.execCommand("copy");
        }
      } catch {
        shareUrlInput.select();
        document.execCommand("copy");
      }
      copyStatus.textContent = "Link copied";
      if (copyTimeoutId) {
        clearTimeout(copyTimeoutId);
      }
      copyTimeoutId = setTimeout(() => {
        copyStatus.textContent = "";
      }, 2500);
    });
  }

  const startForm = document.getElementById("start-form");
  const nickInput = document.getElementById("nick");
  const startBtn = document.getElementById("start-btn");

  if (startForm && nickInput && startBtn) {
    startForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearError();

      const nick = nickInput.value;
      startBtn.disabled = true;

      try {
        const attempt = await apiRequest(
          "POST",
          `/api/quizzes/${encodeURIComponent(quizId)}/attempts`,
          { nick }
        );
        window.location.href = `play.html?attempt=${encodeURIComponent(attempt.attempt_id)}`;
      } catch (err) {
        showError(err.message);
        startBtn.disabled = false;
      }
    });
  }

  await loadLeaderboard(quizId);
});
