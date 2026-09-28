document.addEventListener("DOMContentLoaded", function () {
	var toggle = document.getElementById("nav-toggle");
	var menu = document.getElementById("nav-menu");
	if (!toggle || !menu) return;

	function closeMenu() {
		menu.classList.remove("is-open");
		toggle.setAttribute("aria-expanded", "false");
	}

	toggle.addEventListener("click", function () {
		var isOpen = menu.classList.toggle("is-open");
		toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
	});

	menu.querySelectorAll("a").forEach(function (link) {
		link.addEventListener("click", closeMenu);
	});

	document.addEventListener("click", function (event) {
		if (!menu.classList.contains("is-open")) return;
		if (menu.contains(event.target) || toggle.contains(event.target)) return;
		closeMenu();
	});
});
