
function switchMap(mapId, newUrl, buttonElement) {
    // Switch image
    const img = document.getElementById(`map-image-${mapId}`);
    img.src = newUrl;

    // Find the parent .variant-buttons container
    const group = buttonElement.closest(".variant-buttons");

    // Remove active from all buttons in this group
    const buttons = group.querySelectorAll(".map-filter-button");
    buttons.forEach(btn => btn.classList.remove("active"));

    // Add active to clicked button
    buttonElement.classList.add("active");
}


// Filter Official maps by year
document.addEventListener("DOMContentLoaded", function () {
    const yearContainer = document.getElementById("year-filter-buttons");

    // The year filter only exists on the Official maps page.
    if (!yearContainer) return;

    const mapReleases = Array.from(
        document.querySelectorAll(".map-release")
    );

    // Find all unique years and sort newest first.
    const years = [...new Set(
        mapReleases.map(map => map.dataset.year)
    )].sort((a, b) => Number(b) - Number(a));

    // Create a button for each year.
    years.forEach(year => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "header-filter-button";
        button.dataset.year = year;
        button.textContent = year;

        yearContainer.appendChild(button);
    });

    // Handle year selection.
    yearContainer.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-year]");

        if (!button) return;

        const selectedYear = button.dataset.year;

        // Update active button styling.
        yearContainer.querySelectorAll("button[data-year]").forEach(btn => {
            btn.classList.toggle("active", btn === button);
        });

        // Show all maps or only maps from the selected year.
        mapReleases.forEach(map => {
            const isVisible =
                selectedYear === "all" || map.dataset.year === selectedYear;

            map.style.display = isVisible ? "" : "none";

            // Show or hide the divider immediately following this map.
            const divider = map.nextElementSibling;

            if (divider && divider.classList.contains("map-release-divider")) {
                divider.style.display = isVisible ? "" : "none";
            }
        });
    });
});