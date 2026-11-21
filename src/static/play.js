const attemptId = getQueryParam("attempt");

function redirectToResult() {
  window.location.href = `result.html?attempt=${encodeURIComponent(attemptId)}`;
}

function capitalize(str) {
  if (!str) {
    return str;
  }
  return str.charAt(0).toUpperCase() + str.slice(1);
}

async function loadQuestion() {
  clearError();
  hideFeedback();

  const playView = document.getElementById("play-view");

  let question;
  try {
    question = await apiRequest(
      "GET",
      `/api/attempts/${encodeURIComponent(attemptId)}/question`
    );
  } catch (err) {
    if (err.code === "attempt_finished") {
      redirectToResult();
      return;
    }
    if (err.code === "attempt_not_found") {
      showNotFound(err.message);
      return;
    }
    showError(err.message);
    return;
  }

  if (playView) {
    playView.classList.remove("hidden");
  }

  renderQuestion(question);
}

function renderQuestion(question) {
  const progressEl = document.getElementById("progress");
  const metaEl = document.getElementById("meta");
  const questionTextEl = document.getElementById("question-text");
  const optionsEl = document.getElementById("options");

  if (progressEl) {
    progressEl.textContent = `Question ${question.position + 1} of ${question.question_count}`;
  }

  if (metaEl) {
    metaEl.textContent = `${question.category} · ${capitalize(question.difficulty)}`;
  }

  if (questionTextEl) {
    questionTextEl.textContent = question.text;
  }

  if (optionsEl) {
    optionsEl.replaceChildren();
    question.options.forEach((optionText, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option-btn";
      btn.textContent = optionText;
      btn.addEventListener("click", () => handleAnswer(question, index));
      optionsEl.appendChild(btn);
    });
  }
}

async function handleAnswer(question, selectedIndex) {
  disableOptions();
  clearError();

  let outcome;
  try {
    outcome = await apiRequest(
      "POST",
      `/api/attempts/${encodeURIComponent(attemptId)}/answer`,
      { question_id: question.question_id, selected_index: selectedIndex }
    );
  } catch (err) {
    if (err.code === "attempt_not_found") {
      showNotFound(err.message);
      return;
    }
    enableOptions();
    showError(err.message);
    return;
  }

  markOptions(selectedIndex, outcome.correct_index);
  showFeedback(question.options, outcome.correct_index, outcome.is_correct, outcome.finished);
}

function disableOptions() {
  const optionsEl = document.getElementById("options");
  if (!optionsEl) {
    return;
  }
  for (const btn of optionsEl.querySelectorAll(".option-btn")) {
    btn.disabled = true;
  }
}

function enableOptions() {
  const optionsEl = document.getElementById("options");
  if (!optionsEl) {
    return;
  }
  for (const btn of optionsEl.querySelectorAll(".option-btn")) {
    btn.disabled = false;
  }
}

function markOptions(selectedIndex, correctIndex) {
  const optionsEl = document.getElementById("options");
  if (!optionsEl) {
    return;
  }
  const buttons = optionsEl.querySelectorAll(".option-btn");
  buttons.forEach((btn, index) => {
    if (index === correctIndex) {
      btn.classList.add("correct");
    } else if (index === selectedIndex) {
      btn.classList.add("wrong");
    }
  });
}

function showFeedback(options, correctIndex, isCorrect, finished) {
  const feedbackEl = document.getElementById("feedback");
  const feedbackMessageEl = document.getElementById("feedback-message");
  const nextBtn = document.getElementById("next-btn");

  if (feedbackMessageEl) {
    if (isCorrect) {
      feedbackMessageEl.textContent = "Correct!";
      feedbackMessageEl.className = "correct";
    } else {
      feedbackMessageEl.textContent = `Wrong. Correct answer: ${options[correctIndex]}`;
      feedbackMessageEl.className = "wrong";
    }
  }

  if (nextBtn) {
    if (finished) {
      nextBtn.textContent = "See result";
      nextBtn.onclick = redirectToResult;
    } else {
      nextBtn.textContent = "Next";
      nextBtn.onclick = loadQuestion;
    }
  }

  if (feedbackEl) {
    feedbackEl.classList.remove("hidden");
  }
}

function hideFeedback() {
  const feedbackEl = document.getElementById("feedback");
  if (feedbackEl) {
    feedbackEl.classList.add("hidden");
  }
  const feedbackMessageEl = document.getElementById("feedback-message");
  if (feedbackMessageEl) {
    feedbackMessageEl.textContent = "";
    feedbackMessageEl.className = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!attemptId || !attemptId.trim()) {
    showNotFound(NO_ATTEMPT_ID_MESSAGE);
    return;
  }
  loadQuestion();
});
