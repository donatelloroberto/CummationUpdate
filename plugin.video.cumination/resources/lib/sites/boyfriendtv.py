'''
    Cumination
    Copyright (C) 2022 mrowliver

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import json
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.customsite import CustomSite

site = CustomSite('mrowliver', 'boyfriend')

BASE_URL = 'https://www.boyfriendtv.com/'


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', BASE_URL + 'tags/json/', 'Categories', site.img_cat)
    List(BASE_URL)
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, site.url)
    except:
        return None
    listhtml = listhtml.split('class="adblock tab-videos-commented"')[0]
    match = re.compile(r'<li\s*class="js-pop.+?src="([^"]+).+?class="fs11(.+?)<span>\s*([\d:]+).+?href="([^"]+).+?>([^<]+)', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for img, info, duration, videopage, name in match:
        name = utils.cleantext(name)
        quality = ''
        if '720p' in info:
            quality = 'HD'
        if 'member-only' in info:
            name += ' [COLOR limegreen][I]Members Only[/I][/COLOR]'
        site.add_download_link(name, urllib_parse.urljoin(BASE_URL, videopage), 'Playvid', img, name, duration=duration, quality=quality)

    nextp = re.compile(r'<a\s*class="rightKey"\s*href="([^"]+)">Next').search(listhtml)
    if nextp:
        site.add_dir('[COLOR hotpink]Next Page...[/COLOR]', urllib_parse.urljoin(BASE_URL, nextp.group(1)), 'List', site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    videolink = re.compile(r'<source\s*src="([^"]+)"', re.DOTALL | re.IGNORECASE).search(videopage)
    if videolink:
        vp.play_from_direct_link(videolink.group(1))
    else:
        utils.notify('Oh Oh', 'Can\'t play members only link')
        vp.progress.close()
        return 


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    items = json.loads(cathtml)
    for item in items:
        img = item.get('image')
        catpage = urllib_parse.urljoin(BASE_URL, item.get('link'))
        name = '{0} [COLOR orange]{1} Videos[/COLOR]'.format(item.get('name'), item.get('videos'))
        site.add_dir(name, catpage, 'List', img)
    utils.eod()
