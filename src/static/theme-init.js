var THEME_STORAGE_KEY = "quiz-theme";
var DEFAULT_THEME = "dark";

(function () {
  var theme = DEFAULT_THEME;
  try {
    var saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved === "dark" || saved === "light") {
      theme = saved;
    }
  } catch (e) {
    // localStorage unavailable — use default
  }
  document.documentElement.dataset.theme = theme;
})();
