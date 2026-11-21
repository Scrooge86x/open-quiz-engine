document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("create-quiz-form");
  const createBtn = document.getElementById("create-btn");
  const questionCountInput = document.getElementById("question-count");
  const difficultySelect = document.getElementById("difficulty");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    const questionCount = parseInt(questionCountInput.value, 10);
    const difficulty = difficultySelect.value;

    const payload = {
      question_count: questionCount,
    };
    if (difficulty) {
      payload.difficulty = difficulty;
    }

    createBtn.disabled = true;

    try {
      const quiz = await apiRequest("POST", "/api/quizzes", payload);
      window.location.href = `quiz.html?id=${encodeURIComponent(quiz.id)}`;
    } catch (err) {
      showError(err.message);
      createBtn.disabled = false;
    }
  });
});
