# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pelisdeverosbauer
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
__title__ = "pelisdeverosbauer"
__channel__ = "pelisdeverosbauer"
__language__ = "ES"
__creationdate__ = "20160404"

host = "http://pelisdeverosbauer.blogspot.mx/"


DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"] )

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="portada", title="Portada", url=host))
    itemlist.append(Item(channel=__channel__, action="pais", title="Por País", url=host))
    itemlist.append(Item(channel=__channel__, action="ano", title="Por Año", url=host))
    itemlist.append(Item(channel=__channel__, action="generos", title=" Por Genero", url=host))
    itemlist.append(Item(channel=__channel__, action="actor", title=" Actor - Director", url=host))	
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url=urlparse.urljoin(host, "search?q=")))

    return itemlist

def portada(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer Portada")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')

    patron = "<h2 class='post-title entry-title'><a href='(.+?)'>(.+?)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle,  in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist	

	
	
def pagina_(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer letras" + item.url)
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    patron = "<h2 class='post-title entry-title'><a href='(.+?)'>(.+?)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle,   in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        plot = ""
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title))
	
    patron = "<a class='blog-pager-older-link' href='([^']+)'"
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
    logger.info("pelisalacarta.channels.pelisdeverosbauer findvideos")

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

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.folder = False
    return itemlist

def ano(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer ano")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"id='Label3'(.+?)</li></ul>")
    patron = "href='(.+?)'>(.+?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist

def pais(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer pais")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"id='Label2'(.+?)</li></ul>")
    patron = "href='(.+?)'>(.+?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist


def generos(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"id='sidebar-lab'(.+?)</li></ul>")
    patron = "href='(.+?)'>(.+?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist

	
def actor(item):
    logger.info("pelisalacarta.channels.pelisdeverosbauer generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,"id='Label1'(.+?)</li></ul>")
    patron = "href='(.+?)'>(.+?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist

	
def search(item, texto):
    logger.info("pelisalacarta.channels.pelisdeverosbauer search")
    item.url = urlparse.urljoin(host, item.url)
    texto = texto.replace(" ", "+")
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url + texto,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    patron = "class='post-title entry-title'><a href='(.+?)'>(.+?)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
    for scrapedurl, scrapedtitle,  in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = ""
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot="", show=title))
	return itemlist