import os
import json
from core.utils import get_puuid, get_champion_name, get_match, find_player, get_player_rank
import urllib.request

class Player:
    def __init__(self, player_name, game_tag):
        self._player_name = player_name
        self._game_tag = game_tag

        # GET PUUID
        # Response returns two keys, status_code and body containing the puuid
        self.puuid = get_puuid(player_name, game_tag)

        # Important Stats
        self.kills = 0
        self.assits = 0
        self.deaths = 0
        self.kda = 0
        self.kp = 0
        self.avg_dmg = 0
        self.dmg_min = 0 # Damage per min
        self.gold = 0 # Average gold per Game
        self.gold_min = 0 # Gold per min
        self.bounty_gold = 0 # Average Bounty Gold per Game
        self.cs = 0 # Average Farming
        self.cs_min = 0 # CS per min
        self.vision_score = 0 # Average Vision Score by Game
        self.vision_min = 0 # Vision Score per min
        self.wards_place = 0 # Average Wards Placed
        self.wards_kill = 0 # Average Wards Killed
        self.pink_wards = 0 # Average Pink Wards Placed
        self.obj_dmg = 0 # Average Objective Damage by Game
        self.wins = 0 # Average Win Rate
        self.loses = 0 # Average Loss Rate
        self.longest_living_time = 0  # Average Time Spent Alive
        self.first_bloods = 0 # Average Number of First Bloods
        self.first_towers = 0 # Average Number of First Towers

        self.lanes = {"TOP": 0, "JUNGLE": 0, "MID": 0, "BOTTOM": 0, "SUPPORT": 0, "NONE": 0}
        self.roles = {}
        self.gamemodes = {}
        self.multi_kills = {"doubleKills": 0, "tripleKills": 0, "quadraKills": 0, "pentaKills": 0}

    def matchHistory(self):
        '''
            matchHistory -> Will fetch Match History from Riot API data and manipualte the most improtant details
        '''
        num_history = 20
        history_id_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?start=0&count={num_history}&api_key={os.environ.get("RIOT_API_KEY")}"
        history_ids = None

        try:
            with urllib.request.urlopen(history_id_url) as response:
                '''
                    EXAMPLE RESPONSE FOR NUM_HISTORY:
                    [
                        "NA1_5370142317",
                        "NA1_5370138029",
                        "NA1_5370133124",
                        ...
                    ]
                '''
                history_ids = json.loads(response.read().decode())
        except Exception as e:
            print(f"Error making API call: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error: {str(e)}")
            }
        
        for history_id in history_ids:
            match_info = get_match(history_id)

            if match_info['info']['gameMode'] != "CLASSIC":
                continue

            if match_info['info']['gameDuration'] < 240: # Game is a Remake
                continue

            print(f"Match ID: {history_id}")

            player = find_player(match_info['info']['participants'], self._player_name, self._game_tag)
            chal = player['challenges']
            game_time = match_info['info']['gameDuration']

            # Formatted TIme
            minutes = game_time // 100
            seconds = game_time % 100

            # CS / Farming
            self.cs += player.get('totalMinionsKilled', 0)
            self.cs_min += player.get('totalMinionsKilled', 0) / minutes

            # Vision
            self.vision_score += player.get('visionScore', 0)
            self.vision_min   += chal.get('visionScorePerMinute', 0)
            self.wards_place  += player.get('wardsPlaced', 0)
            self.wards_kill   += player.get('wardsKilled', 0)
            self.pink_wards   += chal.get('controlWardsPlaced', 0)

            self.longest_living_time += player.get('longestTimeSpentLiving', 0)

            # Gold
            self.gold        += player.get('goldEarned', 0)
            self.gold_min    += chal.get('goldPerMinute', 0)
            self.bounty_gold += chal.get('bountyGold', 0)

            # Firsts
            self.first_bloods += 1 if player.get('firstBloodKill') else 0
            self.first_towers += 1 if player.get('firstTowerKill') else 0
            self.obj_dmg      += player.get('damageDealtToObjectives', 0)
            self.avg_dmg      += player.get('totalDamageDealt', 0)

            # KDA / KP
            self.kills  += player.get('kills', 0)
            self.assits += player.get('assists', 0)
            self.deaths += player.get('deaths', 0)
            self.kda    += chal.get('kda', 0)
            self.kp     += chal.get('killParticipation', 0)

            # Win / Lose
            if player.get('win') is True:
                self.wins += 1
            elif player.get('win') is False:
                self.loses += 1

            # Lane / Role / Gamemode
            lane     = player.get('lane', 'NONE')
            role     = player.get('role', 'UNKNOWN')
            gamemode = match_info['info'].get('gameMode', 'UNKNOWN')

            self.lanes[lane]        = self.lanes.get(lane, 0) + 1
            self.roles[role]        = self.roles.get(role, 0) + 1
            self.gamemodes[gamemode]= self.gamemodes.get(gamemode, 0) + 1

    def returnPlayerStats(self):
        # Compile and Organize Player Data
        totalGames = self.wins + self.loses

        player_ranks = get_player_rank(self.puuid)

        rank_solo = ranked_flex = None

        for rank in player_ranks:
            if rank['queueType'] == 'RANKED_SOLO_5x5':
                ranked_solo = {"tier": rank['tier'], "rank": rank['rank'], "wins": rank['wins'], "losses": rank['losses']}
            
            if rank['queueType'] == 'RANKED_FLEX_SR':
                ranked_flex = {"tier": rank['tier'], "rank": rank['rank'], "wins": rank['wins'], "losses": rank['losses']}

        player = {
            "kda": self.kda,
            "kp": self.kp,
            "damageDealt": self.avg_dmg,
            "goldEarned": self.gold,
            "goldPerMin": self.gold_min,
            "bountyGold": self.bounty_gold,
            "winRate": self.wins,
            "loseRate": self.loses,
            "longestAliveTime": self.longest_living_time,
            "visionScore": self.vision_score,
            "visionPerMin": self.vision_min,
            "wardsPlaced": self.wards_place,
            "wardsKilled": self.wards_kill,
            "pinkWardsPlaced": self.pink_wards,
            "cs": self.cs,
            "csPerMin": self.cs_min,
            "firstBloods": self.first_bloods,
            "firstTowers": self.first_towers,
            "objDamage": self.obj_dmg
        }

        for key in player:
            player[key] /= totalGames

        max_role =  max(self.roles, key=self.roles.get)
        max_lane =  max(self.lanes, key=self.lanes.get)
        max_gamemode =  max(self.gamemodes, key=self.gamemodes.get)

        player['mostPlayedRole'] = max_role
        player['mostPlayedLane'] = max_lane
        player['mostPlayedGamemode'] = max_gamemode
        player['rankedSolo'] = ranked_solo
        player['rankedFlex'] = ranked_flex

        return player

    def topMastery(self, n):
        '''
            topMastery -> Will fetch top n mastered champions of the player
            n: int -> Number of top champions to fetch
        '''
        if not isinstance(n, int):
            raise TypeError(f"We got the wrong type for n. It must be an integer number. Instead got {type(n)})")
        
        
        url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.puuid}/top?count={n}&api_key={os.environ.get("RIOT_API_KEY")}"

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                '''

                EXAMPLE RESPONSE USING N = 3:
                [
                    {
                        "puuid": {PUUID},
                        "championId": 92,
                        "championLevel": 47,
                        "championPoints": 490290,
                        "lastPlayTime": 1757237563000,
                        "championPointsSinceLastLevel": 7690,
                        "championPointsUntilNextLevel": 3310,
                        "markRequiredForNextLevel": 2,
                        "tokensEarned": 4,
                        "championSeasonMilestone": 0,
                        "nextSeasonMilestone": {
                            "requireGradeCounts": {
                                "A-": 1
                            },
                            "rewardMarks": 1,
                            "bonus": false,
                            "totalGamesRequires": 1
                        }
                    },
                    {
                        "puuid": {PUUID},
                        "championId": 141,
                        "championLevel": 16,
                        "championPoints": 160147,
                        "lastPlayTime": 1756285211000,
                        "championPointsSinceLastLevel": 18547,
                        "championPointsUntilNextLevel": -7547,
                        "markRequiredForNextLevel": 2,
                        "tokensEarned": 0,
                        "championSeasonMilestone": 0,
                        "nextSeasonMilestone": {
                            "requireGradeCounts": {
                                "A-": 1
                            },
                            "rewardMarks": 1,
                            "bonus": false,
                            "totalGamesRequires": 1
                        }
                    },
                    ...
                ]
                '''
            res = []
            champ_ids = []

            for champ in data:
                champ_ids.append(champ['championId'])
            
            for i, champ_id in enumerate(champ_ids):
                champ_info = get_champion_name(champ_id)

                champ_obj = {}
                champ_obj['championLevel'] = data[i]['championLevel']
                champ_obj['championPoints'] = data[i]['championPoints']
                champ_obj['championName'] = champ_info['name']
                champ_obj['roles'] = champ_info['tags']
                champ_obj['title'] = champ_info['title']

                res.append(champ_obj) # Sorted by Top Mastery -> Least Top Mastery
            print("Successfully created TopMasteries")
            return {
                'statusCode': 200,
                'body': json.dumps(res)
            }
        except Exception as e:
            print(f"Error making API call: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error: {str(e)}")
            }