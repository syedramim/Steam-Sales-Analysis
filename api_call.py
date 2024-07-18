import asyncio
import aiohttp
import json

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url}: Status {response.status}")
                return None
    except Exception as e:
        print(f"Exception occurred while fetching {url}: {e}")
        return None

async def apps_json():
    game_id_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    async with aiohttp.ClientSession() as session:
        response_id = await fetch(session, game_id_url)
        if response_id:
            game_dict = json.loads(response_id)['applist']['apps']
            return game_dict
        return {}

async def steamspy_json():
    steamspy_dict = dict()
    index = 0
    page = 0
    steamspy_columns = ['appid', 'positive', 'negative', 
                        'userscore', 'score_rank', 'price', 
                        'owners', 'ccu', 'developer', 'publisher']
    
    async with aiohttp.ClientSession() as session:
        while True:
            steamspy_url = f"https://steamspy.com/api.php?request=all&page={page}"
            steamspy_response_text = await fetch(session, steamspy_url)
            if steamspy_response_text:
                steamspy_json = json.loads(steamspy_response_text)
                if not steamspy_json:
                    break
                for i in steamspy_json:
                    app = steamspy_json[i]
                    info = {element: str(app[element]) for element in steamspy_columns}
                    steamspy_dict[index] = info
                    index += 1
                page += 1
            else:
                break
        
    return steamspy_dict

async def steamhf_json():
    steamhf_columns = ['AppID', 'Estimated owners', 'Price', 
                    'Metacritic score', 'User score', 'Positive', 'Negative', 
                    'Recommendations', 'Categories', 'Tags', 'Peak CCU', 'Genres' ]
    steamhf_dict = dict()
    offset = 0
    index = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            steamhf_url = f"https://datasets-server.huggingface.co/rows?dataset=FronkonGames%2Fsteam-games-dataset&config=default&split=train&offset={offset}&length=100"
            steamhf_response_text = await fetch(session, steamhf_url)
            if steamhf_response_text:
                steamhf_json = json.loads(steamhf_response_text)
                rows = steamhf_json.get('rows', [])
                if not rows:
                    break
                for i in range(len(rows)):
                    row_info = {column.lower(): rows[i]['row'][column] for column in steamhf_columns}
                    steamhf_dict[index] = row_info
                    index += 1
                offset += 100
            else:
                break
        
    return steamhf_dict

async def gamalytic_json():
    gamalytic_cols = ['steamId', 'publisherClass', 'copiesSold']
    gamalytic_dict = dict()
    page = 0
    index = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            gamalytic_url = f"https://api.gamalytic.com/steam-games/list?page={page}&fields=copiesSold,publisherClass,steamId"
            gamalytic_response_text = await fetch(session, gamalytic_url)
            if gamalytic_response_text:
                gamalytic_json = json.loads(gamalytic_response_text)
                results = gamalytic_json.get('result', [])
                if not results:
                    break
                gamalytic_data = [{col.lower(): result.get(col, None) for col in gamalytic_cols} for result in results]
                for row in gamalytic_data:
                    gamalytic_dict[index] = row
                    index += 1
                page += 1
            else:
                break
        
    return gamalytic_dict