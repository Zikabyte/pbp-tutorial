(function () {
	var theme = localStorage.getItem("theme");
	if (!theme) {
		theme = window.matchMedia("(prefers-color-scheme: dark)").matches
			? "dark"
			: "light";
	}
	document.documentElement.setAttribute("data-theme", theme);
})();

document.addEventListener("DOMContentLoaded", function () {
	var toggle = document.getElementById("theme-toggle");
	var root = document.documentElement;

	toggle.addEventListener("click", function () {
		var newTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
		root.setAttribute("data-theme", newTheme);
		localStorage.setItem("theme", newTheme);
	});
});
