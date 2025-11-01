# Summoner-Sync
LOL AI that gives valuable insights
League of Legends AI Coach

A fun, interactive web app that analyzes League of Legends players using Riot API data and provides personalized coaching, champion recommendations, and team synergy advice. Perfect for solo players, duos, trios, or full teams.

Features

Analyze 1–5 players at a time by summoner name.

Individual player breakdowns:

KDA, CS per Minute, Gold per Minute, Vision Score, Kill Participation, Win Rate, Games Played, Rank

Champion Mastery (Top 5)

Strengths, Weaknesses, Improvements

Champion Recommendations tailored to their playstyle

Multi-player synergy:

Duo / Trio / Full Team analysis

Recommended team compositions (5 full-team setups for 4–5 players)

Detailed explanation: how to play each comp, what to avoid, and what lessons they teach

End-of-season style review:

Overall stats summary

Key focus areas for improvement

Suggestions for future growth

Fun, casual AI tone — playful teasing, motivational comments, not robotic

Demo / Screenshots

(Optional: Include screenshots or GIFs of the site showing player stats, AI output, or team comps.)

Installation / Setup

Clone the repository:

git clone https://github.com/YourTeam/LoL-AI-Coach.git


Install dependencies:

npm install
# or
yarn install


Configure environment variables in a .env file:

RIOT_API_KEY=your_riot_api_key_here
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-2


Start the development server:

npm run dev
# or
yarn dev


Open your browser at http://localhost:3000 to test the app.

Usage

Enter 1–5 summoner names in the search bar (e.g., "Hide on Bush" or "GenG Ruler").

Click Analyze.

The AI outputs:

Individual player stats (KDA, CS, Gold, Vision Score, Rank, Champion Mastery)

Strengths, Weaknesses, Improvements per player

Champion Recommendations for skill growth

Duo/Trio/Team synergy and recommended team compositions (depending on the number of players)

End-of-season style overall review, summarizing stats and suggesting next steps

Configuration

Riot API:

summoner-v4 → basic player info

champion-mastery-v4 → top champions

league-v4 / match-v5 → stats like KDA, KP, CS, Gold, Vision Score

AWS Bedrock AI:

Processes player data and generates coaching advice

Dynamically adapts to 1–5 players

Keeps a casual, fun, and motivational tone

Notes

Only the players entered are analyzed — no extra/random players.

Champion recommendations help expand fundamentals without forcing a complete playstyle change.

End-of-season style reviews are designed for reflection and long-term growth.

Contributing

Open issues or submit pull requests for bug fixes or feature suggestions.

Ensure new features do not break Riot API integration or AWS Bedrock AI prompts.

License

MIT License — see LICENSE file for details.
