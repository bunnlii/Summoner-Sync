(function () {
  const maxPlayers = 5;
  const playersChips = document.getElementById("player-chips");
  const input = document.getElementById("player-input");
  const addBtn = document.getElementById("add-player");
  const searchBtn = document.getElementById("search-btn");

  function getChipCount() {
    return playersChips.querySelectorAll(".player-chip").length;
  }
  function updateAddButton() {
    const count = getChipCount();
    addBtn.disabled = count >= maxPlayers;
    addBtn.textContent =
      count >= maxPlayers ? "Max players added" : "Add Another Player";
  }

  function createChip(name) {
    const chip = document.createElement("div");
    chip.className = "player-chip";

    const span = document.createElement("span");
    span.className = "chip-name";
    span.textContent = name;

    const remove = document.createElement("button");
    remove.className = "remove-btn";
    remove.setAttribute("aria-label", `Remove player ${name}`);
    remove.innerHTML = "&times;";
    remove.addEventListener("click", () => {
      chip.remove();
      updateAddButton();
      input.focus();
    });

    chip.appendChild(span);
    chip.appendChild(remove);
    return chip;
  }

  function addPlayerFromInput() {
    const val = input.value.trim();
    const errorEl = document.getElementById("input-error");
    if (errorEl) errorEl.textContent = "";
    hidePopup();
    if (!val) {
      input.focus();
      return;
    }
    //make sure riot id is in the right format
    const match = val.match(/^\s*([^#]+)#([A-Za-z0-9]{1,5})\s*$/);
    if (!match) {
      showPopup("check if your RIOT ID is spelled correctly");
      input.setAttribute("aria-invalid", "true");
      input.focus();
      return;
    }
    const existing = Array.from(
      playersChips.querySelectorAll(".chip-name")
    ).map((s) => s.textContent.toLowerCase());
    if (existing.includes(val.toLowerCase())) {
      input.value = "";
      input.focus();
      return;
    }
    if (getChipCount() >= maxPlayers) return;
    playersChips.appendChild(createChip(val));
    input.value = "";
    input.focus();
    updateAddButton();
  }

  addBtn.addEventListener("click", (e) => {
    e.preventDefault();
    addPlayerFromInput();
  });

  searchBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("input-error");
    if (errorEl) errorEl.textContent = "";
    hidePopup();
    const chips = Array.from(playersChips.querySelectorAll(".chip-name")).map(
      (s) => s.textContent
    );
    const values = chips.slice();
    const cur = input.value.trim();
    if (cur) {
      const match = cur.match(/^\s*([^#]+)#([A-Za-z0-9]{1,5})\s*$/);
      if (!match) {
        showPopup("check if your RIOT ID is spelled correctly");
        input.setAttribute("aria-invalid", "true");
        input.focus();
        return;
      }
      values.push(cur);
    }
    // player names
    const players = values.map((val) => {
      const [playerName, gameTag] = val.split("#");
      return { playerName, gameTag };
    });

    // Show full-screen loading overlay
    showLoadingOverlay();
    searchBtn.disabled = true;

    fetch(
      "https://6s6bu9zrxe.execute-api.us-west-1.amazonaws.com/summsync/player/create",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ players }),
      }
    )
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Server responded with ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("AWS Response:", data);

        if (data.sessionId) {
          window.sessionId = data.sessionId;
          localStorage.setItem("players", JSON.stringify(players));
          // Auto-redirect without alert
          window.location.href = `./html/results.html?session=${data.sessionId}`;
        } else {
          hideLoadingOverlay();
          showPopup("Could not create session");
          searchBtn.disabled = false;
        }
      })
      .catch((err) => {
        console.error("Error:", err);
        hideLoadingOverlay();
        showPopup("Something went wrong connecting to the API");
        searchBtn.disabled = false;
      });
  });

  // Loading overlay functions
  function showLoadingOverlay() {
    let overlay = document.getElementById("loading-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "loading-overlay";
      overlay.className = "loading-overlay";
      overlay.setAttribute("role", "status");
      overlay.setAttribute("aria-live", "polite");
      overlay.innerHTML = `
        <div class="loading-overlay-content">
          <div class="loading-spinner-large"></div>
          <p class="loading-overlay-text">Loading...</p>
        </div>
      `;
      document.body.appendChild(overlay);
    }
    overlay.classList.add("visible");
  }

  function hideLoadingOverlay() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.classList.remove("visible");
    }
  }

  const helpIcon = document.querySelector(".help-icon");
  let popupTimeout = null;
  function showPopup(message) {
    let popup = document.getElementById("global-popup");
    if (!popup) {
      popup = document.createElement("div");
      popup.id = "global-popup";
      popup.className = "global-popup";
      popup.setAttribute("role", "alert");
      popup.setAttribute("aria-live", "assertive");
      //message + close button
      popup.innerHTML =
        '<span class="popup-message" aria-atomic="true"></span><button class="popup-close" aria-label="Dismiss notification">\u00D7</button>';
      document.body.appendChild(popup);
      // wire close button
      const closeBtn = popup.querySelector(".popup-close");
      if (closeBtn) {
        closeBtn.addEventListener("click", () => {
          hidePopup();
        });
        closeBtn.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            hidePopup();
          }
        });
      }
    }
    const msg = popup.querySelector(".popup-message");
    if (msg) msg.textContent = message;
    else popup.textContent = message;
    popup.classList.add("visible");
    popup.setAttribute("aria-hidden", "false");
    if (popupTimeout) clearTimeout(popupTimeout);
    popupTimeout = setTimeout(() => {
      hidePopup();
    }, 10000); // 10s
  }

  function hidePopup() {
    const popup = document.getElementById("global-popup");
    if (!popup) return;
    popup.classList.remove("visible");
    popup.setAttribute("aria-hidden", "true");
    if (popupTimeout) {
      clearTimeout(popupTimeout);
      popupTimeout = null;
    }
  }
  function closeAllTooltips() {
    document
      .querySelectorAll(".tooltip")
      .forEach((t) => t.setAttribute("aria-hidden", "true"));
    document
      .querySelectorAll(".help-icon")
      .forEach((h) => h.setAttribute("aria-expanded", "false"));
  }
  function toggleTooltipFor(help) {
    const id = help.getAttribute("aria-controls");
    if (!id) return;
    const tip = document.getElementById(id);
    if (!tip) return;
    const isHidden = tip.getAttribute("aria-hidden") === "true";
    closeAllTooltips();
    tip.setAttribute("aria-hidden", String(!isHidden));
    help.setAttribute("aria-expanded", String(isHidden));
  }

  if (helpIcon) {
    helpIcon.addEventListener("click", () => toggleTooltipFor(helpIcon));
    helpIcon.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleTooltipFor(helpIcon);
      }
      if (e.key === "Escape") {
        closeAllTooltips();
        helpIcon.blur();
      }
    });
  }

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".input-wrapper")) closeAllTooltips();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAllTooltips();
  });

  // initialize
  const bgRange = document.getElementById("bg-offset-range");
  const bgValue = document.getElementById("bg-offset-value");
  const bgReset = document.getElementById("bg-offset-reset");
  let defaultOffset =
    getComputedStyle(document.documentElement).getPropertyValue(
      "--bg-video-offset"
    ) || "70%";
  defaultOffset = parseInt(defaultOffset.trim(), 10) || 70;
  if (bgRange) {
    bgRange.value = defaultOffset;
    bgRange.addEventListener("input", (e) => {
      const v = e.target.value;
      document.documentElement.style.setProperty("--bg-video-offset", v + "%");
      if (bgValue) bgValue.textContent = v + "%";
    });
    // reflect initial value
    if (bgValue) bgValue.textContent = bgRange.value + "%";
  }
  if (bgReset) {
    bgReset.addEventListener("click", () => {
      document.documentElement.style.setProperty(
        "--bg-video-offset",
        defaultOffset + "%"
      );
      if (bgRange) {
        bgRange.value = defaultOffset;
      }
      if (bgValue) bgValue.textContent = defaultOffset + "%";
    });
  }

  updateAddButton();
})();

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const child = document.getElementById("child");
  let lastScrollY = child.scrollTop;

  child.addEventListener("scroll", () => {
    const currentScroll = child.scrollTop;

    if (currentScroll > lastScrollY && currentScroll > 50) {
      header.classList.add("hidden");
    } else {
      header.classList.remove("hidden");
    }

    lastScrollY = currentScroll;
  });
});
