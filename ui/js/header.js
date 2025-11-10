document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  if (!header) return;

  // Prefer scrolling inside #child if present (index/team/about), else fall back to window (results)
  const child = document.getElementById("child");
  const scrollEl = child || window;

  // Get current scroll position for either element or window
  const getScrollTop = () => (child ? child.scrollTop : window.scrollY || document.documentElement.scrollTop || 0);

  let lastScroll = getScrollTop();
  const threshold = 50; // don't hide until user has scrolled a bit

  const onScroll = () => {
    const current = getScrollTop();
    if (current > lastScroll && current > threshold) {
      header.classList.add("hidden");
    } else {
      header.classList.remove("hidden");
    }
    lastScroll = current;
  };

  // Attach listener
  scrollEl.addEventListener("scroll", onScroll, { passive: true });
});
