import os
import json
from core.utils import get_puuid, get_champion_name, get_match, find_player
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

            match = {}

            player = find_player(match_info['info']['participants'], self._player_name, self._game_tag)
            chal = player['challenges']
            game_time = match_info['info']['gameDuration']

            # Formatted TIme
            minutes = game_time // 100
            seconds = game_time % 100

            # CS / Farming
            self.cs += player['totalMinionsKilled']
            self.cs_min += (player['totalMinionsKilled'] // minutes)

            # Vision
            self.vision_score += player['visionScore']
            self.vision_min += chal['visionScorePerMinute']
            self.wards_place += player['wardsPlaced']
            self.wards_kill += player['wardsKilled']
            self.pink_wards += chal['controlWardsPlaced']

            self.longest_living_time += player['longestTimeSpentLiving']

            # Gold
            self.gold += player['goldEarned']
            self.gold_min += chal['goldPerMinute']
            self.bounty_gold += chal['bountyGold']

            # Firsts
            self.first_bloods += player['firstBloodKill']
            self.first_towers += player['firstTowerKill']
            self.obj_dmg += player['damageDealtToObjectives']
            self.avg_dmg += player['totalDamageDealt']

            # KDA
            self.kills += player['kills']
            self.assits += player['assists']
            self.deaths += player['deaths']
            self.kda += chal['kda']
            self.kp += chal['killParticipation']

            # Win/Lose
            self.wins += player['win']
            self.loses += not player['win']
            
            # Lanes & Roles
            lane = player['lane']
            role = player['role']
            gamemode = match_info['info']['gameMode']

            if lane not in self.lanes.keys():
                self.lanes[lane] = 1
            else:
                self.lanes[lane] += 1

            if role not in self.roles.keys():
                self.roles[role] = 1
            else:
                self.roles[role] += 1

            if gamemode not in self.gamemodes.keys():
                self.gamemodes[gamemode] = 1
            else:
                self.gamemodes[gamemode] += 1

    def returnPlayerStats(self):
        # Compile and Organize Player Data
        totalGames = self.wins + self.loses

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