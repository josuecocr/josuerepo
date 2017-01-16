# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para serieszone
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from core import servertools

DEBUG = config.get_setting("debug")

__category__ = "S"
__type__ = "generic"
__title__ = "serieszone"
__channel__ = "serieszone"
__language__ = "ES"
__creationdate__ = "20160404"

host = "http://serieszone.com"


DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"] )
DEFAULT_HEADERS.append( ["Accept-Encoding", "gzip, deflate, sdch"] )
DEFAULT_HEADERS.append( ["Connection","keep-alive"])
DEFAULT_HEADERS.append( ["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"] )
DEFAULT_HEADERS.append( ["Accept-Language","es"] )
DEFAULT_HEADERS.append( ["Cache-Control","max-age=0"] )	


def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.serieszone mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="series_", title="Lista de Series", url="http://serieszone.com/"))
    itemlist.append(Item(channel=__channel__, action="ultimos_c", title="Ultimos Capítulos Agregados", url="http://serieszone.com/"))
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url=urlparse.urljoin(host, "/?s=")))


    return itemlist


	
def series_(item):
    logger.info("pelisalacarta.channels.serieszone generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.anti_cloudflare(item.url, headers=headers, host=host)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    #data = scrapertools.get_match(data,"id='PopularPosts1'>(.+?)</div></div>")
    patron = 'href="(.+?)".+?>(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="capitulos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def capitulos(item):
    logger.info("pelisalacarta.channels.estrenosdoramas capitulos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, 'class="addthis_native_toolbox"(.+?)class="addthis_native_toolbox"')
    patron  = 'href="(http://serieszone.com.+?)" target="_blank">(.+?)<.+?>(.+?)<'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl,scrapedtitle, nombre in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip() + nombre
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        show = item.show
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, show=show))		
    return itemlist



def ultimos_c(item):
    logger.info("pelisalacarta.channels.estrenosdoramas ultimos_c")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, "class='switch'(.+?)class='pages'")
    patron  = "class='post-title entry-title'><a href='(.+?)'>(.+?)<"
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        show = item.show
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, show=show))		

	patron = 'rel="next" href="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="ultimos_c", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

		
def findvideos(item):
    logger.info("pelisalacarta.channels.serieszone findvideos")

    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    patron = '<iframe.*?src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    data1 = ''
    for match in matches:
		data1 += match + '\n'
    
    itemlist = []

    from servers import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.folder = False
    return itemlist
	
	
	
def search(item, texto):
    logger.info("pelisalacarta.channels.serieszone search")
    item.url = urlparse.urljoin(host, item.url)
    texto = texto.replace(" ", "+")
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url + texto,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, "id='Blog1'(.+?)id='sidebar-wrapper'")
    patron  = "class='post-title entry-title'><a href='(.+?)'>(.+?)<"
    matches = re.compile(patron,re.DOTALL).findall(data1)	
    itemlist = []
    for scrapedurl, scrapedtitle, in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        itemlist.append( Item(channel=__channel__, action="series_" , title=title , url=url, thumbnail="", plot="", folder=True))
    return itemlist	