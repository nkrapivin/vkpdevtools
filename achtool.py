import requests
import json
import argparse
import io

def cookies2dict(cookiestring):
    d = {}
    s = cookiestring
    # "a=abc; b=cde; c=aaa"
    while True:
        eqidx = s.find('=')
        if eqidx < 0:
            break
        name = s[0 : eqidx].strip()
        endidx = s.find(';', eqidx)
        if endidx < 0:
            endidx = len(s)
        value = s[eqidx + 1 : endidx]
        s = s[endidx + 1 : ]
        d[name] = value
    return d

def file2lines(filename):
    lines = []
    with open(filename) as file:
        lines = file.read().splitlines()
    return lines

# очень плохой конвертер vdf -> json
# работает только с vdf-ками из Raw Settings и ничем больше...
def vdf2json(lines_):
    linescopy = lines_.copy()
    linescopylen = len(linescopy)
    for i in range(linescopylen):
        l = linescopy[i]
        if "\"\t\"" in l:
            linescopy[i] = l.replace("\"\t\"", "\":\t\"")
            if (i+1 < linescopylen) and (not linescopy[i+1].endswith("}")):
                linescopy[i] = linescopy[i] + ","
            continue
        if l.endswith("}") and (i+1 < linescopylen) and linescopy[i+1].strip() and (not linescopy[i + 1].endswith("}")):
            linescopy[i] = l + ","
            continue
        if l.count("\"") == 2:
            linescopy[i] = l + ":"
            continue
    # wrap in a root object
    linescopy.append("}")
    linescopy.insert(0, "{")
    fulljson = ""
    for l in linescopy:
        fulljson += l + "\n"
    return json.loads(fulljson)

def localeconv(locale):
    table = {
        # 'steam': 'vk',
        # 'vk': 'steam',
        'russian': 'ru_RU',
        'ru_RU': 'russian',
        'english': 'en_US',
        'en_US': 'english',
        'french': 'fr_FR',
        'fr_FR': 'french',
        'spanish': 'es_ES',
        'es_ES': 'spanish',
        'polish': 'pl_PL',
        'pl_PL': 'polish',
        'turkish': 'tr_TR',
        'tr_TR': 'turkish',
        'german': 'de_DE',
        'de_DE': 'german',
        'arabic': 'ar_AA',
        'ar_AA': 'arabic'
    }
    if locale not in table:
        return None
    return table[locale]

def stm2vk2(ach, idx, stmurlpfx, gameid, csrf, csrf_jwt, cookies):
    url = f"https://developers.vkplay.ru/dev/api/game/{gameid}/achievements/add/"
    payload = {}
    payload['main-priority'] = (None, str(idx)) # should be the INVERSE..???
    payload['main-is_published'] = (None, 'false') # паблиш лучше делать из Кабинета...
    payload['main-is_hidden'] = (None, 'false') # VK PLAY ЭКСКЛЮЗИВ
    payload['main-is_hidden_until_get'] = (None, str(ach['display']['hidden'] == '1').lower())
    maxprogress = '0'
    if 'progress' in ach:
        maxprogress = ach['progress']['max_val']
    payload['main-max_progress'] = (None, maxprogress)
    payload['main-rareness'] = (None, 'C') # VK PLAY ЭКСКЛЮЗИВ

    iconfileobj = None
    if True or ('icon' in ach['display']):
        iconfilename = ach['display']['icon']
        iconurl = stmurlpfx + iconfilename
        r = requests.get(iconurl)
        r.raise_for_status()
        iconfileobj = io.BytesIO(r.content)
        payload['main-picture'] = (iconfilename, iconfileobj, 'image/jpeg')
        # iconfileobj = open("D:\\hwrpage\\test_unlocked.jpg", "rb")
        # payload['main-picture'] = ('test_unlocked.jpg', iconfileobj, 'image/jpeg')
    
    payload['main-apiname'] = (None, ach['name'])

    icongrayfileobj = None
    if True or ('icon_gray' in ach['display']):
        icongrayfilename = ach['display']['icon_gray']
        icongrayurl = stmurlpfx + icongrayfilename
        r = requests.get(icongrayurl)
        r.raise_for_status()
        icongrayfileobj = io.BytesIO(r.content)
        payload['main-picture_locked'] = (icongrayfilename, icongrayfileobj, 'image/jpeg')
        # icongrayfileobj = open("D:\\hwrpage\\test_locked.jpg", "rb")
        # payload['main-picture_locked'] = ('test_locked.jpg', icongrayfileobj, 'image/jpeg')

    for k, v in ach['display']['name'].items():
        vklocale = localeconv(k)
        if vklocale is None:
            continue
        payload[vklocale + '-name'] = (None, v)

    for k, v in ach['display']['desc'].items():
        vklocale = localeconv(k)
        if vklocale is None:
            continue
        payload[vklocale + '-descr'] = (None, v)

    payload['csrfmiddlewaretoken'] = (None, csrf)
    payload['csrfmiddlewaretoken_jwt'] = (None, csrf_jwt)
    headers = {}
    headers['Sec-Ch-Ua'] = '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"'
    headers['Sec-Ch-Ua-Mobile'] = '?0'
    headers['Sec-Ch-Ua-Platform'] = '"Windows"'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Site'] = 'same-origin'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203'
    headers['Accept'] = '*/*'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7'
    headers['Origin'] = 'https://developers.vkplay.ru'
    headers['Referer'] = url

    r = requests.post(url, files=payload, headers=headers, cookies=cookies, allow_redirects=True)
    iconfileobj.close()
    icongrayfileobj.close()
    r.raise_for_status()
    # print(r.content.decode())
    print(f'Done, added {idx}!')

def stm2vk(achs, game_id, csrf, csrf_jwt, cookies):
    appid = list(achs.keys())[0]
    urlpixprefix = f"https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{appid}/"
    stats = achs[appid]
    achid = 1 # must start at 1 for priority to work...
    for k__, v__ in stats.items():
        if not isinstance(v__, dict):
            break
        for k_, v_ in v__.items():
            v_t = v_['type']
            if v_t != 'ACHIEVEMENTS':
                continue
            for k, v in v_["bits"].items():
                stm2vk2(v, achid, urlpixprefix, game_id, csrf, csrf_jwt, cookies)
                achid += 1
    print(f"Parsed {achid - 1} achievements...")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A tool to autoimport Stats from Steamworks into VK Play")
    parser.add_argument('--game_id', help="Internal game id on VK dashboard")
    parser.add_argument('--vdf', help="Path to the Stats VDF file from Steamworks")
    parser.add_argument('--csrf', help="CSRF token")
    parser.add_argument('--csrf_jwt', help="CSRF JWT token from multipart")
    parser.add_argument('--cookies', help="Cookie string from Headers")
    args = parser.parse_args()
    achievements = vdf2json(file2lines(args.vdf))
    cookies = cookies2dict(args.cookies)
    stm2vk(achievements, args.game_id, args.csrf, args.csrf_jwt, args.cookies)
