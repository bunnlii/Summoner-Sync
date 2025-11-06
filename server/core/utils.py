import os
import json
import urllib.request
from urllib.parse import quote
import json, os, pathlib
from importlib.resources import files as ir_files

_CHAMPIONS = None

def _load_champions():
    errors = []

    # 1) Load from package data: summsync/data/champion.json
    try:
        with ir_files("summsync.data").joinpath("champion.json").open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        errors.append(f"package summsync.data: {e}")

    here = pathlib.Path(__file__).resolve()
    candidates = [
        here.parent / "data" / "champion.json",          # same dir has /data
        here.parent.parent / "data" / "champion.json",   # one level up has /data
        pathlib.Path("/var/task/data/champion.json"),    # Lambda code root
        pathlib.Path("/opt/data/champion.json"),         # Lambda Layer path
    ]
    for p in candidates:
        try:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{p}: {e}")

    raise FileNotFoundError("champion.json not found. Tried:\n" + "\n".join(f"- {x}" for x in errors))

def get_puuid(name, gameTag):
    name_enc = quote(str(name), safe='')
    tag_enc = quote(str(gameTag), safe='')
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name_enc}/{str(tag_enc)}?api_key={os.environ.get("RIOT_API_KEY")}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            '''
            RESPONSE:
            {
                "puuid": {puuid},
                "gameName": "Crolwick",
                "tagLine": "LION"
            }
            '''

            if "puuid" not in data.keys():
                raise KeyError(f"The key puuid does not exist. Please check the API documentation to ensure format is still correct, else you gave the wrong URL.")

            print('Status Code: 200')
        return  data['puuid']
    except Exception as e:
        print(f"Error making API call: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    
def get_champion_name(champ_id: int):
    # Match The champ_id parameter to it's corresponding champion name in the champions json
    global _CHAMPIONS
    if _CHAMPIONS is None:
        _CHAMPIONS = _load_champions()['data']

    for key, value in _CHAMPIONS.items():
        if int(value['key']) == int(champ_id):
            return _CHAMPIONS[key]
        
def get_match(match_id):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={os.environ.get("RIOT_API_KEY")}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        '''
        
        '''
        return data
    except Exception as e:
        print(f"Error making API call: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    
def find_player(participants, name, gameTag):
    for participant in participants:
        if participant['riotIdGameName'].lower() == name.lower() and participant['riotIdTagline'].lower() == gameTag.lower():
            return participant
        
    raise LookupError(f"Unable to find the player in list of participants. Please provide correct participant information")