/**
 * Modern enhancements for Django Admin FilteredSelectMultiple (Permissions / Groups)
 */
document.addEventListener("DOMContentLoaded", () => {
    function formatText(text) {
        if (!text) return text;
        if (text.includes(" | ")) {
            const parts = text.split(" | ");
            if (parts.length === 3) {
                // e.g., "Appointments | appointment | Can add appointment" -> "Appointments › Can add appointment"
                return `${parts[0]} › ${parts[2]}`;
            }
        }
        return text;
    }

    function initSelectorEnhancements() {
        const selectors = document.querySelectorAll(".selector");
        if (!selectors.length) return;

        // Clean SelectBox internal cache if present
        if (window.SelectBox && window.SelectBox.cache) {
            for (const key in window.SelectBox.cache) {
                const items = window.SelectBox.cache[key];
                if (Array.isArray(items)) {
                    items.forEach((item) => {
                        if (item && item.text) {
                            item.text = formatText(item.text);
                        }
                    });
                }
            }
        }

        selectors.forEach((selector) => {
            const fromSelect = selector.querySelector("select[id$='_from']");
            const toSelect = selector.querySelector("select[id$='_to']");
            const availableTitle = selector.querySelector(".selector-available-title label");
            const chosenTitle = selector.querySelector(".selector-chosen-title label");

            if (!fromSelect || !toSelect) return;

            // 1. Create or update count badges
            let availableBadge = availableTitle ? availableTitle.querySelector(".selector-count-badge") : null;
            if (availableTitle && !availableBadge) {
                availableBadge = document.createElement("span");
                availableBadge.className = "selector-count-badge";
                availableTitle.appendChild(availableBadge);
            }

            let chosenBadge = chosenTitle ? chosenTitle.querySelector(".selector-count-badge") : null;
            if (chosenTitle && !chosenBadge) {
                chosenBadge = document.createElement("span");
                chosenBadge.className = "selector-count-badge";
                chosenTitle.appendChild(chosenBadge);
            }

            function updateCounts() {
                if (availableBadge && fromSelect) {
                    availableBadge.textContent = fromSelect.options.length;
                }
                if (chosenBadge && toSelect) {
                    chosenBadge.textContent = toSelect.options.length;
                }
            }

            // 2. Clean option labels in DOM
            function cleanOptions(selectElement) {
                if (!selectElement) return;
                for (let i = 0; i < selectElement.options.length; i++) {
                    const opt = selectElement.options[i];
                    opt.text = formatText(opt.text);
                }
            }

            cleanOptions(fromSelect);
            cleanOptions(toSelect);
            updateCounts();

            // Observe option changes
            const observer = new MutationObserver(() => {
                cleanOptions(fromSelect);
                cleanOptions(toSelect);
                updateCounts();
            });

            observer.observe(fromSelect, { childList: true });
            observer.observe(toSelect, { childList: true });

            // Listen to chooser button clicks
            selector.querySelectorAll("button, a, input").forEach((el) => {
                el.addEventListener("click", () => {
                    setTimeout(() => {
                        cleanOptions(fromSelect);
                        cleanOptions(toSelect);
                        updateCounts();
                    }, 50);
                });
                el.addEventListener("keyup", () => {
                    setTimeout(() => {
                        cleanOptions(fromSelect);
                        cleanOptions(toSelect);
                        updateCounts();
                    }, 50);
                });
            });
        });
    }

    // Run after SelectFilter2.js initializes
    setTimeout(initSelectorEnhancements, 100);
    setTimeout(initSelectorEnhancements, 400);
});
