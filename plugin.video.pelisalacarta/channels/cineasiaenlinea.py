# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cineasiaenlinea
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
__title__ = "cineasiaenlinea"
__channel__ = "cineasiaenlinea"
__language__ = "ES"
__creationdate__ = "20160216"

host = "http://cineasiaenlinea.com/"

DEFAULT_HEADERS = [
    ["User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"],
    ["Accept-Encoding: gzip, deflate, sdch"],
    ["Proxy-Connection: keep-alive"],
    ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
    ["Referer: http://www.cineasiaenlinea.com"],	
	

]


def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="ultimos", title="Ultimos Proyectos", url="http://cineasiaenlinea.com/archivos/estrenos/"))
    itemlist.append(Item(channel=__channel__, action="pais", title="Por País", url=host))
    itemlist.append(Item(channel=__channel__, action="ano", title="Por Año", url=host))
    itemlist.append(Item(channel=__channel__, action="generos", title=" Por Genero", url=host))
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url="http://www.cineasiaenlinea.com/?s="))

    return itemlist

def ultimos(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea ESTRENOS")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url)
    #data = data.replace('\n','')
    #data = data.replace('\r','')
    #data = scrapertools.get_match(data,'id="content-post"(.+?)id="sidebar"')	
    patron = '<h3><a href="(http://www.cineasiaenlinea.com/.*?)".*?title="(.*?)">.*?img.*?src="(.*?)".*?rel="tag">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot, in matches:
       #if len(matches) > 0:	
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        plot = urlparse.urljoin(host, scrapedplot)
        #if (DEBUG): logger.info(url=["+url+"], "title=["+title+"], thumbnail=["+thumbnail+"], plot=["+plot+"]").format(url, title, thumbnail, plot)
        itemlist.append(Item(channel=__channel__, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot, contentType="movie", fulltitle=title, contentTitle=scrapedtitle.decode('cp1252'), context=["buscar_trailer"], show=title))
		
    patron = 'class="nextpostslink" href="([^\'].*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "[COLOR deepskyblue]Pagina Siguiente >>[/COLOR]"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="ultimos", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

	
	
def pagina_(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea letras" + item.url)
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)

    patron = 'document.write\(thumbnails\("(.+?)","(.+?)","(.+?)",.*?\)\);</script>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail,  in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        plot = ""
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, contentType="movie", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))
	
    patron = "<a class='blog-pager-older-link' href='([^']+)' id='Blog1_blog-pager-older-link'"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="pagina_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist
	

	
def findvideos(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea findvideos")
    itemlist = []
    data = scrapertools.cache_page(item.url)
    detalle = scrapertools.find_single_match(data, 'SINOPSIS DE:(.*?)</p>')	
    detalle = scrapertools.htmlclean(detalle)
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.folder = False
        videoitem.plot = detalle + item.contentTitle
		
    return itemlist

def ano(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea ano")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"id='fecha-estreno'(.+?)id=\"sideindex\"")
    patron = '<option value="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, "http://www.cineasiaenlinea.com/fecha-estreno/"+title+"")
        thumbnail = item.thumbnail		
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="ultimos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist
	

def pais(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea pais")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"Peliculas por Pais(.+?)</ul>")
    patron = 'href="(.+?)" title="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = item.thumbnail
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="ultimos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.cineasiaenlinea generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'Peliculas por genero(.+?)id="sideindex"')
    patron = 'href="(.+?)" title="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = item.thumbnail
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="ultimos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def search(item,texto):
    logger.info("pelisalacarta.channels.cineasiaenlinea search")
    texto = texto.replace(" ","+")
    item.url = urlparse.urljoin(host, "http://www.cineasiaenlinea.com/?s=" + texto)	

    try:
        return scraper(item)    
	# Se captura la excepciÛn, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def scraper(item):	
    # Descarga la página	
    data = scrapertools.cache_page(item.url)
    data = data.replace('\n','')
    data = data.replace('\r','')		
    patron = '<h3><a href="(http://www.cineasiaenlinea.com/.*?)".*?title="(.*?)">.*?img.*?src="(.*?)".*?rel="tag">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []		
	
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot, in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        fanart = thumbnail
        item.infoLabels = {'year':scrapedplot}
        plot = scrapedplot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title , url=url, thumbnail=thumbnail, folder=True, fanart=fanart, plot = plot, contentType="movie", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))
	# páginación
    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="scraper", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist	