document.addEventListener("DOMContentLoaded", function () {
    const page = document.getElementById("balance-sheet-ordering");
    if (!page || typeof Sortable === "undefined") {
        return;
    }

    const saveUrl = page.dataset.saveUrl;
    const status = document.getElementById("save-status");

    const csrfToken = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];

    function getChanges() {
        const changes = [];

        document.querySelectorAll(".item-list").forEach(list => {
            const sectionId = list.dataset.sectionId;

            list.querySelectorAll(".sortable-item").forEach((item, index) => {
                changes.push({
                    id: Number(item.dataset.itemId),
                    section_id: Number(sectionId),
                    ordering: index
                });
            });
        });

        return changes;
    }

    async function saveOrder() {
        status.textContent = "Saving…";

        try {
            const response = await fetch(saveUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken || ""
                },
                body: JSON.stringify({ items: getChanges() })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || "Could not save changes.");
            }

            status.textContent = "Order saved.";
        } catch (error) {
            status.textContent = "Save failed. Refresh the page and try again.";
            console.error(error);
        }
    }

    document.querySelectorAll(".item-list").forEach(list => {
        new Sortable(list, {
            group: "balance-sheet-items",
            animation: 150,
            draggable: ".sortable-item",

            onEnd: function () {
                document.querySelectorAll(".empty-message").forEach(message => {
                    message.remove();
                });

                document.querySelectorAll(".item-list").forEach(list => {
                    if (!list.querySelector(".sortable-item")) {
                        const message = document.createElement("li");
                        message.className = "empty-message";
                        message.textContent = "Drop items here";
                        list.appendChild(message);
                    }
                });

                saveOrder();
            }
        });
    });
});