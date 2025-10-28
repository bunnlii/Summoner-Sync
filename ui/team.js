document.addEventListener("DOMContentLoaded", () => {
  const bgVideo = document.getElementById("bg-video");
  const defaultVideo = "video-image/skt-t1-skins-league-of-legends-moewalls-com (online-video-cutter.com).mp4";
  const cards = document.querySelectorAll(".player-card");

  if (!bgVideo || !cards.length) return;

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("flipped");

      cards.forEach((c) => {
        if (c !== card) c.classList.remove("flipped", "active");
      });

      card.classList.add("active");

      const newVideo = card.classList.contains("flipped")
        ? card.getAttribute("data-video")
        : defaultVideo;

      bgVideo.style.opacity = 0;
      setTimeout(() => {
        bgVideo.src = newVideo;
        bgVideo.play().catch((err) => console.log("Autoplay blocked:", err));
        bgVideo.style.opacity = 1;
      }, 500); // 0.5s fade
    });
  });
});
