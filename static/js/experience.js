// Konfigurasi (diisi lewat window.EXPERIENCE_CONFIG, lihat experience.html)
const BASE_EXPERIENCES_ENDPOINT = EXPERIENCE_CONFIG.experiencesEndpoint;
const CAN_CHANGE = EXPERIENCE_CONFIG.canChange;
const CAN_DELETE = EXPERIENCE_CONFIG.canDelete;
const CREATE_EXPERIENCE_ENDPOINT = EXPERIENCE_CONFIG.createEndpoint;
let experiencesAbortController;

// Elemen DOM
const loadingState = document.getElementById("loading");
const errorState = document.getElementById("error");
const emptyState = document.getElementById("empty");
const gridContainer = document.getElementById("grid");
const searchForm = document.getElementById("experience-search-form");
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

// Mencegah teks dari data disisipkan sebagai HTML
function escapeHtml(value) {
	return String(value ?? "")
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#39;");
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

// Membangun URL detail (update/delete/star) dari template URL dummy UUID
function buildDetailUrl(template, id) {
	return template.replace("00000000-0000-0000-0000-000000000000", id);
}

// Membuat elemen card experience
function buildExperienceCardElement(item) {
	const experience = item.fields;
	const experienceId = item.pk;
	const csrftoken = getCookie("csrftoken");

	const articleElement = document.createElement("article");
	articleElement.className = "experience-card";

	const statusText = experience.ended_at ? "Selesai" : "Sedang berlangsung";

	const starUrl = buildDetailUrl(
		EXPERIENCE_CONFIG.starUrlTemplate,
		experienceId,
	);
	const updateUrl = buildDetailUrl(
		EXPERIENCE_CONFIG.updateUrlTemplate,
		experienceId,
	);
	const deleteUrl = buildDetailUrl(
		EXPERIENCE_CONFIG.deleteUrlTemplate,
		experienceId,
	);

	const editHtml = CAN_CHANGE
		? `<a href="${updateUrl}" class="button button-secondary">Edit</a>`
		: "";

	const deleteHtml = CAN_DELETE
		? `<form method="post" action="${deleteUrl}" style="display:inline;">
                <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrftoken)}">
                <button type="submit" class="button button-danger" onclick="return confirm('Yakin ingin menghapus pengalaman ini?');">Hapus</button>
            </form>`
		: "";

	const isStarredClass = experience.is_starred ? " is-starred" : "";
	const starText = experience.is_starred ? "Unstar" : "Star";
	const starTitle =
		experience.star_count > 0 && experience.starred_by_names
			? `Dibintangi oleh ${escapeHtml(experience.starred_by_names)}`
			: "Jadilah yang pertama memberi star";

	articleElement.innerHTML = `
            <span class="experience-category">${escapeHtml(experience.category_display)}</span>
            <h2>${escapeHtml(experience.title)}</h2>
            <p class="experience-description">${escapeHtml(experience.description)}</p>
            <p class="experience-status">${statusText}</p>
            <div class="project-actions">
                <form method="post" action="${starUrl}" class="star-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrftoken)}">
                    <button type="submit"
                            class="button button-star${isStarredClass}"
                            title="${starTitle}">
                        <span aria-hidden="true">★</span>
                        ${starText}
                        <span class="star-count">${experience.star_count}</span>
                    </button>
                </form>

                ${editHtml}
                ${deleteHtml}
            </div>
        `;

	return articleElement;
}

// Fetch data experience
async function fetchExperiences() {
	if (experiencesAbortController) experiencesAbortController.abort();
	experiencesAbortController = new AbortController();

	try {
		displayPageSection({ showLoading: true });

		const params = new URLSearchParams();
		if (searchInput.value.trim()) params.set("title", searchInput.value.trim());
		if (categorySelect.value) params.set("category", categorySelect.value);
		if (sortSelect.value) params.set("sort", sortSelect.value);
		if (starredFilter && starredFilter.checked) params.set("starred", "1");

		const queryString = params.toString();
		const url = queryString
			? `${BASE_EXPERIENCES_ENDPOINT}?${queryString}`
			: BASE_EXPERIENCES_ENDPOINT;

		const response = await fetch(url, {
			headers: { Accept: "application/json" },
			signal: experiencesAbortController.signal,
		});

		if (!response.ok) throw new Error("Failed to fetch data");

		const experienceData = await response.json();

		if (experienceData.length === 0) {
			displayPageSection({ showEmpty: true });
		} else {
			gridContainer.innerHTML = "";
			experienceData.forEach((item) => {
				gridContainer.appendChild(buildExperienceCardElement(item));
			});
			displayPageSection({ showGrid: true });
		}
	} catch (error) {
		if (error.name === "AbortError") return;
		console.error("Error loading experiences:", error);
		displayPageSection({ showError: true });
	}
}

function closeExperienceModal() {
	document.getElementById("add-experience-modal").hidePopover();
}

// Mengirim data form tambah experience ke server
async function addExperience(event) {
	event.preventDefault();

	const submitButton = experienceForm.querySelector('button[type="submit"]');
	submitButton.disabled = true;

	try {
		const response = await fetch(CREATE_EXPERIENCE_ENDPOINT, {
			method: "POST",
			headers: { "X-CSRFToken": getCookie("csrftoken") },
			body: new FormData(experienceForm),
		});
		const result = await response.json().catch(() => ({}));

		if (response.ok) {
			experienceForm.reset();
			closeExperienceModal();
			showToast("Berhasil", "Pengalaman baru berhasil ditambahkan!", "success");
			fetchExperiences();
		} else {
			const errorMessages = result.errors
				? Object.values(result.errors)
						.flat()
						.map((error) => error.message)
				: [result.message || `Terjadi kesalahan (status ${response.status}).`];
			showToast("Gagal menambahkan pengalaman", errorMessages.join(" "), "error");
		}
	} catch (error) {
		console.error("Error adding experience:", error);
		showToast(
			"Gagal menambahkan pengalaman",
			"Tidak dapat terhubung ke server. Silakan coba lagi.",
			"error",
		);
	} finally {
		submitButton.disabled = false;
	}
}

const experienceForm = document.getElementById("experience-form");
if (experienceForm) {
	experienceForm.addEventListener("submit", addExperience);
}

// Event Handlers untuk Form Search & Filter
searchForm.addEventListener("submit", function (event) {
	event.preventDefault();
	clearTimeout(searchDebounceTimer);
	fetchExperiences();
});

searchInput.addEventListener("input", function () {
	clearTimeout(searchDebounceTimer);
	searchDebounceTimer = setTimeout(fetchExperiences, SEARCH_DEBOUNCE_DELAY);
});

categorySelect.addEventListener("change", fetchExperiences);
sortSelect.addEventListener("change", fetchExperiences);
if (starredFilter) {
	starredFilter.addEventListener("change", fetchExperiences);
}

// Start application
fetchExperiences();
