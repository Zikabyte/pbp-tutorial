// Konfigurasi (diisi lewat window.PROJECT_CONFIG, lihat project.html)
const BASE_PROJECTS_ENDPOINT = PROJECT_CONFIG.projectsEndpoint;
const CREATE_PROJECT_ENDPOINT = PROJECT_CONFIG.createEndpoint;
const IS_SUPERUSER = PROJECT_CONFIG.isSuperuser;
let projectsAbortController;

// Elemen DOM
const loadingState = document.getElementById("loading");
const errorState = document.getElementById("error");
const emptyState = document.getElementById("empty");
const gridContainer = document.getElementById("grid");
const searchForm = document.getElementById("project-search-form");
const searchInput = document.getElementById("search-input");
const categorySelect = document.getElementById("category-select");
const sortSelect = document.getElementById("sort-select");
const starredFilter = document.getElementById("starred-filter");

const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;

// Membaca nilai cookie, digunakan untuk mengambil token CSRF
function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== "") {
		const cookies = document.cookie.split(";");
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === name + "=") {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

// Menyembunyikan/Menampilkan section halaman
function displayPageSection({
	showLoading = false,
	showError = false,
	showEmpty = false,
	showGrid = false,
}) {
	loadingState.classList.toggle("hide", !showLoading);
	errorState.classList.toggle("hide", !showError);
	emptyState.classList.toggle("hide", !showEmpty);
	gridContainer.classList.toggle("hide", !showGrid);
}

// Membangun URL detail (delete/star) dari template URL dummy UUID
function buildDetailUrl(template, projectId) {
	return template.replace("00000000-0000-0000-0000-000000000000", projectId);
}

// Membuat elemen card project
function buildProjectCardElement(item) {
	const project = item.fields;
	const projectId = item.pk;
	const csrftoken = getCookie("csrftoken");

	const articleElement = document.createElement("article");
	articleElement.className = "experience-card";

	const imageHtml = project.image_url
		? `<img src="${project.image_url}" alt="Gambar ${project.name}" class="project-image">`
		: "";

	const urlHtml = project.project_url
		? `<a href="${project.project_url}" class="button">Lihat Project</a>`
		: "";

	const deleteUrl = buildDetailUrl(PROJECT_CONFIG.deleteUrlTemplate, projectId);
	const starUrl = buildDetailUrl(PROJECT_CONFIG.starUrlTemplate, projectId);

	const deleteHtml = IS_SUPERUSER
		? `<form method="post" action="${deleteUrl}" style="display:inline;">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                <button type="submit" class="button button-danger" onclick="return confirm('Yakin ingin menghapus project ini?');">Hapus</button>
            </form>`
		: "";

	const isStarredClass = project.is_starred ? " is-starred" : "";
	const starText = project.is_starred ? "Unstar" : "Star";
	const starTitle =
		project.star_count > 0 && project.starred_by_names
			? `Dibintangi oleh ${project.starred_by_names}`
			: "Jadilah yang pertama memberi star";

	// Komponen card
	const completeCardHtml = `
            ${imageHtml}
            <h2>${project.name}</h2>
            <span class="experience-category">${project.category}</span>
            <p class="experience-description">${project.description}</p>
            <div class="project-card-actions">
                <div class="project-actions">
                    ${urlHtml}

                    <form method="post" action="${starUrl}" class="star-form">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                        <button type="submit"
                                class="button button-star${isStarredClass}"
                                title="${starTitle}">
                            <span aria-hidden="true">★</span>
                            ${starText}
                            <span class="star-count">${project.star_count}</span>
                        </button>
                    </form>

                    ${deleteHtml}
                </div>
            </div>
        `;

	articleElement.innerHTML = completeCardHtml;
	return articleElement;
}

// Fetch data project
async function fetchProjects() {
	if (projectsAbortController) projectsAbortController.abort();
	projectsAbortController = new AbortController();

	try {
		displayPageSection({ showLoading: true });

		const params = new URLSearchParams();
		if (searchInput.value.trim()) params.set("title", searchInput.value.trim());
		if (categorySelect.value) params.set("category", categorySelect.value);
		if (sortSelect.value) params.set("sort", sortSelect.value);
		if (starredFilter && starredFilter.checked) params.set("starred", "1");

		const queryString = params.toString();
		const url = queryString ? `${BASE_PROJECTS_ENDPOINT}?${queryString}` : BASE_PROJECTS_ENDPOINT;

		const response = await fetch(url, {
			headers: { Accept: "application/json" },
			signal: projectsAbortController.signal,
		});

		if (!response.ok) throw new Error("Failed to fetch data");

		const projectData = await response.json();

		if (projectData.length === 0) {
			displayPageSection({ showEmpty: true });
		} else {
			gridContainer.innerHTML = "";
			projectData.forEach((item) => {
				gridContainer.appendChild(buildProjectCardElement(item));
			});
			displayPageSection({ showGrid: true });
		}
	} catch (error) {
		if (error.name === "AbortError") return;
		console.error("Error loading projects:", error);
		displayPageSection({ showError: true });
	}
}

function closeProjectModal() {
	document.getElementById("add-project-modal").hidePopover();
}

// Mengirim data form ke server
async function addProject(event) {
	event.preventDefault();

	const submitButton = projectForm.querySelector('button[type="submit"]');
	submitButton.disabled = true;

	try {
		const response = await fetch(CREATE_PROJECT_ENDPOINT, {
			method: "POST",
			headers: { "X-CSRFToken": getCookie("csrftoken") },
			body: new FormData(projectForm),
		});
		const result = await response.json().catch(() => ({}));

		if (response.ok) {
			projectForm.reset();
			closeProjectModal();
			showToast("Berhasil", "Proyek baru berhasil ditambahkan!", "success");
			fetchProjects();
		} else {
			const errorMessages = result.errors
				? Object.values(result.errors)
						.flat()
						.map((error) => error.message)
				: [result.message || `Terjadi kesalahan (status ${response.status}).`];
			showToast("Gagal menambahkan proyek", errorMessages.join(" "), "error");
		}
	} catch (error) {
		console.error("Error adding project:", error);
		showToast(
			"Gagal menambahkan proyek",
			"Tidak dapat terhubung ke server. Silakan coba lagi.",
			"error",
		);
	} finally {
		submitButton.disabled = false;
	}
}

const projectForm = document.getElementById("project-form");
if (projectForm) {
	projectForm.addEventListener("submit", addProject);
}

// Event Handlers untuk Form Search
searchForm.addEventListener("submit", function (e) {
	e.preventDefault();
	clearTimeout(searchDebounceTimer);
	fetchProjects();
});

searchInput.addEventListener("input", function () {
	clearTimeout(searchDebounceTimer);
	searchDebounceTimer = setTimeout(fetchProjects, SEARCH_DEBOUNCE_DELAY);
});

categorySelect.addEventListener("change", fetchProjects);
sortSelect.addEventListener("change", fetchProjects);
if (starredFilter) {
	starredFilter.addEventListener("change", fetchProjects);
}

// Start application
fetchProjects();
