document.addEventListener("DOMContentLoaded", async () => {
  const main = document.querySelector("main");
  if (!main) return;

  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get("session");
  const players = JSON.parse(localStorage.getItem("players") || "[]");

  if (!sessionId || players.length === 0) {
    alert("No session or players found!");
    return;
  }

  const container = document.getElementById("players-container");

  // Fetch player stats and mastery
  async function fetchPlayerData(player) {
    const { playerName, gameTag } = player;

    // Fetch stats
    const statsResp = await fetch(
      "https://6s6bu9zrxe.execute-api.us-west-1.amazonaws.com/summsync/player/stats",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, playerName, gameTag }),
      }
    );

    if (!statsResp.ok) {
      throw new Error(`Stats API returned ${statsResp.status}`);
    }

    const stats = await statsResp.json();

    // Fetch mastery
    const masteryResp = await fetch(
      "https://6s6bu9zrxe.execute-api.us-west-1.amazonaws.com/summsync/player/mastery",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, playerName, gameTag }),
      }
    );

    if (!masteryResp.ok) {
      throw new Error(`Mastery API returned ${masteryResp.status}`);
    }

    const mastery = await masteryResp.json();

    return { stats, mastery };
  }

  // Fetch AI insight for a player
  async function fetchAIInsight(playerName, gameTag) {
    try {
      console.log(
        `Fetching AI insight for ${playerName}#${gameTag} with sessionId:`,
        sessionId
      );
      const aiResp = await fetch(
        "https://6s6bu9zrxe.execute-api.us-west-1.amazonaws.com/summsync/ai-insight/solo/player",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId,
            playerName,
            gameTag,
          }),
        }
      );

      if (!aiResp.ok) {
        const errorBody = await aiResp.text();
        console.error(
          `AI Insight API error for ${playerName}#${gameTag}: ${aiResp.status}`,
          errorBody
        );
        throw new Error(
          `AI Insight API returned ${aiResp.status}: ${errorBody}`
        );
      }

      const aiData = await aiResp.json();
      console.log(`AI Insight for ${playerName}#${gameTag}:`, aiData);

      // Handle different response field names
      const insight =
        aiData.answer ||
        aiData.insight ||
        aiData.message ||
        aiData.content ||
        aiData.response ||
        JSON.stringify(aiData);
      return insight;
    } catch (err) {
      console.error(
        `Error fetching AI insight for ${playerName}#${gameTag}:`,
        err
      );
      return `Unable to generate AI insight: ${err.message}`;
    }
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

  // Helper function to get lane icon from Community Dragon
  function getLaneIcon(lane) {
    const iconMap = {
      TOP: '<img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-top.png" alt="Top Lane" class="lane-icon" title="Top Lane" />',
      JUNGLE:
        '<img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png" alt="Jungle" class="lane-icon" title="Jungle" />',
      MIDDLE:
        '<img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png" alt="Mid Lane" class="lane-icon" title="Mid Lane" />',
      BOTTOM:
        '<img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-bottom.png" alt="Bot Lane" class="lane-icon" title="Bot Lane" />',
      UTILITY:
        '<img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-utility.png" alt="Support" class="lane-icon" title="Support" />',
    };
    return (
      iconMap[lane] || '<i class="fas fa-question-circle" title="Unknown"></i>'
    );
  }

  // Create a player card
  function createPlayerCard(player, data, masteryData) {
    const stats = data.stats || {};
    const mastery = masteryData.mastery || [];

    // Extract profile picture URL from stats using iconLink
    const profilePicUrl =
      stats.iconLink ||
      stats.profileIcon ||
      stats.summonerProfileIcon ||
      "../video-image/bunnlii.jpg";

    // Get top mastery champion for background
    const topMasteryChampion =
      mastery.length > 0 ? mastery[0].championName : null;
    const championSplashUrl = topMasteryChampion
      ? `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${topMasteryChampion.replace(
          /\s/g,
          ""
        )}_0.jpg`
      : "";

    const card = document.createElement("div");
    card.className = "player-card";

    // Set background image if champion found
    if (championSplashUrl) {
      card.style.backgroundImage = `url('${championSplashUrl}')`;
      card.style.backgroundSize = "cover";
      card.style.backgroundPosition = "center";
      card.style.backgroundAttachment = "fixed";
    }

    card.innerHTML = `
    <div class="player-top">
      <div class="player-left">
        <div class="player-image-section">
          <img src="${profilePicUrl}" alt="Profile" class="profile-img" />
          <h2 class="player-name">${player.playerName}#${player.gameTag}</h2>
          <div class="player-rank">
            <div class="rank-item">
              <div class="rank-tier">
                <img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-mini-crests/${
                  stats.rankedSolo
                    ? stats.rankedSolo.tier.toLowerCase()
                    : "unranked"
                }.svg" alt="Solo Rank" class="rank-emblem" />
                <span class="rank-value">
                  ${
                    stats.rankedSolo
                      ? `${stats.rankedSolo.tier} ${stats.rankedSolo.rank}`
                      : "Unranked"
                  }
                </span>
              </div>
              <span class="rank-label">Solo</span>
            </div>
            <div class="rank-item">
              <div class="rank-tier">
                <img src="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-mini-crests/${
                  stats.rankedFlex
                    ? stats.rankedFlex.tier.toLowerCase()
                    : "unranked"
                }.svg" alt="Flex Rank" class="rank-emblem" />
                <span class="rank-value">
                  ${
                    stats.rankedFlex
                      ? `${stats.rankedFlex.tier} ${stats.rankedFlex.rank}`
                      : "Unranked"
                  }
                </span>
              </div>
              <span class="rank-label">Flex</span>
            </div>
          </div>
        </div>
      </div>
      <div class="player-ai-top ai-top-section">
        <h3 class="ai-title">AI Insight</h3>
        <ul class="ai-list">
          <li class="ai-insight-item">
            <p id="ai-${player.playerName}-${player.gameTag}"><span class="loading-spinner"></span> Okay… interesting. Let's break this down....</p>
          </li>
        </ul>
      </div>
    </div>

    <hr>

    <div class="bottom-headings">
      <h3>Stats</h3>
      <h3>Top 3 Mastery</h3>
    </div>

    <div class="player-bottom-row">
      <div class="stats-section-bottom">
        <div class="stat-section">
          <p><strong>Most Played Role:</strong> 
            <span class="role-icon-container">
              ${getLaneIcon(stats.mostPlayedRole)}
            </span>
          </p>
          <p><strong>Avg KDA:</strong> ${stats.kda?.toFixed(2) || "N/A"}</p>
          <p><strong>Avg KP:</strong> ${
            stats.kp ? (stats.kp * 100).toFixed(1) : "N/A"
          }%</p>
        </div>

        <div class="stat-section">
          <p><strong>Avg  Gold/Min:</strong> ${
            stats.goldPerMin?.toFixed(1) || "N/A"
          }</p>
          <p><strong>Avg CS Per Game:</strong> ${
            stats.cs?.toFixed(1) || "N/A"
          }</p>
          <p><strong>Avg CS/Min:</strong> ${
            stats.csPerMin?.toFixed(2) || "N/A"
          }</p>
        </div>

        <div class="stat-section">
          <p><strong>AVG Vision Score:</strong> ${
            stats.visionScore?.toFixed(1) || "N/A"
          }</p>
          <p><strong>AVG Vision/Min:</strong> ${
            stats.visionPerMin?.toFixed(2) || "N/A"
          }</p>
          <p><strong>Avg Wards Placed per game:</strong> ${
            stats.wardsPlaced?.toFixed(1) || "N/A"
          }</p>
          <p><strong>Avg Wards Killed per game:</strong> ${
            stats.wardsKilled?.toFixed(1) || "N/A"
          }</p>
        </div>

        <div class="stat-section">
          <p><strong>Lifetime Objective DMG:</strong> ${
            stats.objDamage?.toLocaleString() || "N/A"
          }</p>
        </div>
      </div>
      <div class="player-mastery mastery-vertical">
        <ul class="mastery-list">
          ${
            mastery.length
              ? mastery
                  .slice(0, 3)
                  .map(
                    (m) =>
                      `<li class="mastery-champion">
                        <div class="champion-icon-name">
                          <img class="champion-icon" src="https://ddragon.leagueoflegends.com/cdn/13.21.1/img/champion/${
                            m.championName
                              ? m.championName.replace(/\s/g, "")
                              : "Unknown"
                          }.png" alt="${
                        m.championName || "Unknown"
                      } icon" onerror=\"this.style.display='none'\" />
                          <span class="champion-name">${
                            m.championName || "Unknown"
                          }</span>
                        </div>
                        <div class="champion-details">
                          <span class="champion-level">Lvl ${
                            m.championLevel
                          }</span>
                          <span class="champion-points">(${m.championPoints?.toLocaleString()} pts)</span>
                        </div>
                      </li>`
                  )
                  .join("")
              : "<li>No mastery data available.</li>"
          }
        </ul>
      </div>
    </div>
  `;

    container.appendChild(card);
  }

  // Fetch all players and create cards
  console.log(
    `Attempting to fetch data for ${players.length} players:`,
    players
  );

  for (let i = 0; i < players.length; i++) {
    const p = players[i];
    try {
      console.log(
        `Fetching data for player ${i + 1}/${players.length}: ${p.playerName}#${
          p.gameTag
        }`
      );
      const { stats, mastery } = await fetchPlayerData(p);
      console.log(`Successfully fetched data for ${p.playerName}#${p.gameTag}`);
      createPlayerCard(p, stats, mastery);

      // Fetch AI insight asynchronously (don't block card creation)
      fetchAIInsight(p.playerName, p.gameTag).then((insight) => {
        const aiElement = document.getElementById(
          `ai-${p.playerName}-${p.gameTag}`
        );
        if (aiElement) {
          // Use marked library to convert markdown to HTML
          aiElement.innerHTML = marked.parse(insight);
        }
      });
    } catch (err) {
      console.error(
        `Error fetching data for player ${i + 1}/${players.length} (${
          p.playerName
        }#${p.gameTag}):`,
        err
      );
      // Create a card with error message
      const errorCard = document.createElement("div");
      errorCard.className = "player-card";
      errorCard.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
          <h2 style="color: var(--primary-light);">${p.playerName}#${p.gameTag}</h2>
          <p style="color: var(--gold); margin-top: 1rem;">Failed to load data for this player. </p><p>Please check if you entered the right summoner name and tag.</p>
          <p style="color: var(--white-accent); margin-top: 0.5rem; font-size: 0.9rem;">Error: ${err.message}</p>
        </div>
      `;
      container.appendChild(errorCard);
    }
  }

  console.log("Finished fetching all player data");

  // Create team AI insight card at the bottom
  const teamAiCard = document.createElement("div");
  teamAiCard.className = "team-ai-card";
  teamAiCard.innerHTML = `
    <video class="team-ai-background" autoplay muted loop playsinline>
      <source src="../video-image/yunara-league-of-legends-moewalls-com.mp4" type="video/mp4">
    </video>
    <h2>Team AI Insight</h2>
    <p id="team-ai-content"><span class="loading-spinner"></span> Hm... Interesting team, let's see....</p>
  `;
  container.appendChild(teamAiCard);

  // Fetch team AI insight asynchronously
  fetchTeamAIInsight().then((insight) => {
    const teamAiElement = document.getElementById("team-ai-content");
    if (teamAiElement) {
      // Use marked library to convert markdown to HTML
      teamAiElement.innerHTML = marked.parse(insight);
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const scrollToTopBtn = document.getElementById("scroll-to-top");
  let lastScrollY = 0;

  window.addEventListener("scroll", () => {
    const currentScroll = window.scrollY;

    // Show header only when at the very top
    if (currentScroll <= 10) {
      header.classList.remove("hidden");
    } else {
      header.classList.add("hidden");
    }

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
