// Runs before first paint (loaded synchronously in <head>) so the saved theme never flashes.
(function () {
  var theme = null;
  try { theme = localStorage.getItem("theme"); } catch (e) { /* storage blocked: keep the default */ }
  // The night sky is the default; light (an old printed star atlas) is opt-in and remembered.
  if (theme !== "light" && theme !== "dark") theme = "dark";
  document.documentElement.setAttribute("data-theme", theme);
  // Animations that start hidden are scoped to .js, so without JavaScript everything is visible.
  document.documentElement.classList.add("js");
})();
