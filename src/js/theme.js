// Runs before first paint (loaded synchronously in <head>) so the saved theme never flashes.
(function () {
  var theme = null;
  try { theme = localStorage.getItem("theme"); } catch (e) { /* storage blocked: keep the default */ }
  // The dark blueprint is the site's identity, so it's the default; light ("whiteprint") is opt-in.
  if (theme !== "light" && theme !== "dark") theme = "dark";
  document.documentElement.setAttribute("data-theme", theme);
  // Animations that start hidden are scoped to .js, so without JavaScript everything is visible.
  document.documentElement.classList.add("js");
})();
