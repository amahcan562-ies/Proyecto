(() => {
  const body = document.body;
  const toggle = document.querySelector(".menu-toggle");
  const sidebar = document.querySelector(".sidebar");

  if (!toggle || !sidebar) {
    return;
  }

  const closeSidebar = () => {
    body.classList.remove("sidebar-open");
  };

  toggle.addEventListener("click", () => {
    body.classList.toggle("sidebar-open");
  });

  sidebar.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.closest("a")) {
      closeSidebar();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) {
      closeSidebar();
    }
  });
})();

