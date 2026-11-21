document.addEventListener("DOMContentLoaded", async () => {
  const attemptId = getQueryParam("attempt");
  if (!attemptId) {
    showError("No attempt id provided.");
    return;
  }

  let result;
  try {
    result = await apiRequest(
      "GET",
      `/api/attempts/${encodeURIComponent(attemptId)}/result`
    );
  } catch (err) {
    showError(err.message);
    return;
  }

  const resultView = document.getElementById("result-view");
  if (resultView) {
    resultView.style.display = "flex";
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
      timeEl.closest("p").style.display = "none";
    }
    if (notFinishedEl) {
      notFinishedEl.style.display = "flex";
    }
    if (backToGameLink) {
      backToGameLink.href = `play.html?attempt=${encodeURIComponent(attemptId)}`;
    }
  } else {
    if (timeEl) {
      timeEl.textContent = formatDuration(result.duration_seconds);
    }
    if (notFinishedEl) {
      notFinishedEl.style.display = "none";
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
