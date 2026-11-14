
document.addEventListener("DOMContentLoaded", () => {
    /* =====================================
       MOBILE NAVIGATION
    ===================================== */

    const menuButton = document.getElementById("mobileMenuButton");
    const mobileNav = document.getElementById("mobileNav");

    if (menuButton && mobileNav) {
        const menuIcon = menuButton.querySelector(".menu-icon");

        const setMenuState = (isOpen) => {
            mobileNav.classList.toggle("open", isOpen);

            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.setAttribute(
                "aria-label",
                isOpen ? "Close navigation menu" : "Open navigation menu"
            );

            mobileNav.setAttribute("aria-hidden", String(!isOpen));

            if (menuIcon) {
                menuIcon.textContent = isOpen ? "✕" : "☰";
            }
        };

        menuButton.addEventListener("click", () => {
            const isOpen =
                menuButton.getAttribute("aria-expanded") === "true";

            setMenuState(!isOpen);
        });

        mobileNav.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                setMenuState(false);
            });
        });

        mobileNav.querySelectorAll("form").forEach((form) => {
            form.addEventListener("submit", () => {
                setMenuState(false);
            });
        });

        document.addEventListener("click", (event) => {
            const isOpen =
                menuButton.getAttribute("aria-expanded") === "true";

            if (!isOpen) return;

            const clickedInsideMenu = mobileNav.contains(event.target);
            const clickedButton = menuButton.contains(event.target);

            if (!clickedInsideMenu && !clickedButton) {
                setMenuState(false);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                setMenuState(false);
                menuButton.focus();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 760) {
                setMenuState(false);
            }
        });

        setMenuState(false);
    }

    /* =====================================
       PRODUCT SORTING
    ===================================== */

    const sortSelect = document.getElementById("sortSelect");

    if (sortSelect) {
        sortSelect.addEventListener("change", () => {
            if (sortSelect.form) {
                if (typeof sortSelect.form.requestSubmit === "function") {
                    sortSelect.form.requestSubmit();
                } else {
                    sortSelect.form.submit();
                }
            }
        });
    }
});
