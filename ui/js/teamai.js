document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session");

  if (!sessionId) {
    alert("No session found!");
    window.location.href = "../html/results.html";
    return;
  }

  // Fetch team AI insight
  async function fetchTeamAIInsight() {
    try {
      console.log("Fetching team AI insight with sessionId:", sessionId);
      const teamAiResp = await fetch(
        "https://6s6bu9zrxe.execute-api.us-west-1.amazonaws.com/summsync/ai-insight/group",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId }),
        }
      );

      if (!teamAiResp.ok) {
        const errorBody = await teamAiResp.text();
        console.error("Team AI Insight API error body:", errorBody);
        
        // Check if it's a "not enough players" error
        if (teamAiResp.status === 400 && errorBody.includes("At least 2 players")) {
          return "Unable to generate team AI insight at this time. At least 2 players are required for this insight";
        }
        
        // Check if it's a service unavailable error
        if (teamAiResp.status === 503) {
          return "Unable to generate team AI insight at this time. Too many request are being done right now, please try again later.";
        }
        
        throw new Error(
          `Team AI Insight API returned ${teamAiResp.status}: ${errorBody}`
        );
      }

      const teamAiData = await teamAiResp.json();
      console.log("Team AI Insight:", teamAiData);

      // Handle different response field names
      const insight =
        teamAiData.answer ||
        teamAiData.insight ||
        teamAiData.message ||
        teamAiData.content ||
        teamAiData.response ||
        JSON.stringify(teamAiData);
      return insight;
    } catch (err) {
      console.error("Error fetching team AI insight:", err);
      return `Unable to generate team AI insight at this time. Error: ${err.message}`;
    }
  }

  // Fetch team AI insight asynchronously
  fetchTeamAIInsight().then((insight) => {
    const teamAiElement = document.getElementById("team-ai-content");
    if (teamAiElement) {
      // Use marked library to convert markdown to HTML
      teamAiElement.innerHTML = marked.parse(insight);
    }
  });

  // Back to Results Button
  const backButton = document.getElementById("back-to-results");
  if (backButton) {
    backButton.addEventListener("click", () => {
      window.location.href = `../html/results.html?session=${encodeURIComponent(sessionId)}`;
    });
  }
});

// Scroll to Top functionality
document.addEventListener("DOMContentLoaded", () => {
  const scrollToTopBtn = document.getElementById("scroll-to-top");
  let lastScrollY = 0;

  window.addEventListener("scroll", () => {
    const currentScroll = window.scrollY;

    // Show/hide scroll to top button
    if (currentScroll > 300) {
      scrollToTopBtn.classList.add("visible");
    } else {
      scrollToTopBtn.classList.remove("visible");
    }

    lastScrollY = currentScroll;
  });

  // Scroll to top when button is clicked
  scrollToTopBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
});
