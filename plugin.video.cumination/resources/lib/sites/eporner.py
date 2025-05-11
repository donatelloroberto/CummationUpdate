import json
from bs4 import BeautifulSoup
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    'eporner',
    '[COLOR hotpink]Eporner - Gay[/COLOR]',
    'https://www.eporner.com/cat/gay/',
    'https://static-eu-cdn.eporner.com/new/logo.png',
    'eporner'
)

# Define sorting filters for Kodi menu
SORT_OPTIONS = [
    ('Most Recent', ''),
    ('Top Rated', 'top-rated/'),
    ('Most Viewed', 'most-viewed/'),
    ('Top Favorites', 'top-favorites/')
]

TAGS = [
    ('Bareback', 'bareback/'),
    ('Twink', 'twink/'),
    ('Muscle', 'muscle/'),
    ('Daddy', 'daddy/'),
    ('Teen', 'teen/'),
    ('Interracial', 'interracial/')
]

@site.register(default_mode=True)
def Main():
    for label, path in SORT_OPTIONS:
        site.add_dir(f'[COLOR lightblue]{label}[/COLOR]', site.url + path, 'List', site.img_list)

    site.add_dir('[COLOR yellow]Filter by Tag[/COLOR]', '', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Gay Pornstars[/COLOR]', site.url.replace('/cat/gay/', '/pornstar-list/'), 'Pornstars', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url.replace('/cat/gay/', '/search/'), 'Search', site.img_search)
    utils.eod()


@site.register()
def Tags():
    for label, path in TAGS:
        tag_url = f"{site.url}{path}"
        site.add_dir(f"[COLOR lightgreen]{label}[/COLOR]", tag_url, 'List', site.img_cat)
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, '')
    except:
        return None

    soup = BeautifulSoup(listhtml, 'html.parser')
    for anchor in soup.find_all('a', href=True):
        img = anchor.find('img')
        quality = anchor.find('span', class_='quality')
        duration = anchor.find('span', class_='duration')
        if img and quality and duration:
            name = utils.cleantext(img['alt'])
            videopage = site.url.rstrip('/') + anchor['href']
            site.add_download_link(name, videopage, 'Playvid', img['src'], name, duration=duration.text, quality=quality.text)

    next_button = soup.find('a', class_='nmnext')
    if next_button and 'href' in next_button.attrs:
        next_url = site.url.rstrip('/') + next_button['href']
        page = next_button['href'].strip('/').split('/')[-1]
        site.add_dir('Next Page ({})'.format(page), next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    try:
        listhtml = utils.getHtml(url, '')
    except:
        return None

    import re
    embed = re.compile("vid = '(.+?)'.+?hash = '(.+?)'", re.DOTALL | re.IGNORECASE).findall(listhtml)[0]
    vid = embed[0]
    s = embed[1]
    hash = ''.join((encode_base_n(int(s[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))
    jsonUrl = f'https://www.eporner.com/xhr/video/{vid}?hash={hash}&domain=www.eporner.com&fallback=false&embed=true&supportedFormats=dash,mp4'

    listJson = utils.getHtml(jsonUrl, '')
    videoJson = json.loads(listJson)
    vp.progress.update(75, "[CR]Loading video page[CR]")
    videoArray = {}
    for (k, v) in videoJson['sources']['mp4'].items():
        videoArray[k] = v['src']
    videourl = utils.prefquality(videoArray, sort_by=lambda x: int(''.join([y for y in x if y.isdigit()])), reverse=True)
    if videourl:
        vp.play_from_direct_link(videourl)
