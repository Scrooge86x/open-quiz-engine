document.addEventListener("DOMContentLoaded", async () => {
  const attemptId = getQueryParam("attempt");
  if (!attemptId || !attemptId.trim()) {
    showNotFound(NO_ATTEMPT_ID_MESSAGE);
    return;
  }

  let result;
  try {
    result = await apiRequest(
      "GET",
      `/api/attempts/${encodeURIComponent(attemptId)}/result`
    );
  } catch (err) {
    if (err.code === "attempt_not_found") {
      showNotFound(err.message);
      return;
    }
    showError(err.message);
    return;
  }

  const resultView = document.getElementById("result-view");
  if (resultView) {
    resultView.classList.remove("hidden");
  }

  const nickEl = document.getElementById("result-nick");
  const scoreEl = document.getElementById("result-score");
  const timeEl = document.getElementById("result-time");
  const notFinishedEl = document.getElementById("not-finished");
  const backToGameLink = document.getElementById("back-to-game");
  const playAgainBtn = document.getElementById("play-again-btn");

  if (nickEl) {
    nickEl.textContent = result.nick;
  }
  if (scoreEl) {
    scoreEl.textContent = `${result.score} / ${result.question_count}`;
  }

  if (result.duration_seconds === null || result.duration_seconds === undefined) {
    if (timeEl) {
      timeEl.closest("p").classList.add("hidden");
    }
    if (notFinishedEl) {
      notFinishedEl.classList.remove("hidden");
    }
    if (backToGameLink) {
      backToGameLink.href = `play.html?attempt=${encodeURIComponent(attemptId)}`;
    }
  } else {
    if (timeEl) {
      timeEl.closest("p").classList.remove("hidden");
      timeEl.textContent = formatDuration(result.duration_seconds);
    }
    if (notFinishedEl) {
      notFinishedEl.classList.add("hidden");
    }
  }

  if (playAgainBtn) {
    playAgainBtn.href = `quiz.html?id=${encodeURIComponent(result.quiz_id)}`;
  }

  const leaderboardTable = document.getElementById("leaderboard-table");
  const leaderboardBody = document.getElementById("leaderboard-body");
  const leaderboardEmpty = document.getElementById("leaderboard-empty");

  try {
    const entries = await apiRequest(
      "GET",
      `/api/quizzes/${encodeURIComponent(result.quiz_id)}/leaderboard`
    );
    renderLeaderboard(entries, leaderboardTable, leaderboardBody, leaderboardEmpty);
  } catch (err) {
    showError(err.message);
  }
});
