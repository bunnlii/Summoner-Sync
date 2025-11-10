document.addEventListener("DOMContentLoaded", () => {
  const bgVideo = document.getElementById("bg-video");
  const defaultVideo = "../video-image/skt-t1-skins-league-of-legends-moewalls-com (online-video-cutter.com).mp4";
  const cards = document.querySelectorAll(".player-card");

  if (!bgVideo || !cards.length) return;

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      // Flip effect
      card.classList.toggle("flipped");

      // Unflip all other cards
      cards.forEach((c) => {
        if (c !== card) c.classList.remove("flipped", "active");
      });

      card.classList.add("active");

      // Swap background video
      const newVideo = card.classList.contains("flipped")
        ? card.getAttribute("data-video")
        : defaultVideo;

      bgVideo.style.opacity = 0;
      setTimeout(() => {
        bgVideo.src = newVideo;
        bgVideo.play().catch((err) => console.log("Autoplay blocked:", err));
        bgVideo.style.opacity = 1;
      }, 500); // 0.5s fade transition
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const child = document.getElementById("child");
  let lastScrollY = child.scrollTop;

  child.addEventListener("scroll", () => {
    const currentScroll = child.scrollTop;

    if (currentScroll > lastScrollY && currentScroll > 50) {
      header.classList.add("hidden");
    } 
    else {
      header.classList.remove("hidden");
    }

    lastScrollY = currentScroll;
  });
});

