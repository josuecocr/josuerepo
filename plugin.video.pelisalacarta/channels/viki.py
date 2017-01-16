# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para viki
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
__title__ = "viki"
__channel__ = "viki"
__language__ = "ES"
__creationdate__ = "20160404"

host = "https://www.viki.com"

header_string1 = "|Cookie="
header_string2 = "&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"


DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"] )
DEFAULT_HEADERS.append( ["Accept-Encoding", "gzip, deflate, sdch"] )
DEFAULT_HEADERS.append( ["Connection","keep-alive"] )
DEFAULT_HEADERS.append( ["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"] )
DEFAULT_HEADERS.append( ["Accept-Language","es"] )
DEFAULT_HEADERS.append( ["Cache-Control","max-age=0"] )	


def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.viki mainlist")
	
    itemlist = list([])
    #itemlist.append(Item(channel=__channel__, action="series_", title="Lista de Series", url="https://www.viki.com/es/browse/genre/all/popular"))
    itemlist.append(Item(channel=__channel__, action="top", title="Lo más visto", url="https://www.viki.com/explore"))
    #itemlist.append(Item(channel=__channel__, action="categorias", title="Categorias", url="https://www.viki.com/es/browse/genre/all/popular"))
    #itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url=("https://www.bing.com/search?q=site%3Aviki.com%2Fes%2Fdrama")))


    return itemlist

def categorias(item):
    logger.info("pelisalacarta.channels.viki categorias")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'<dd class="options genre">(.+?)</dd')
    patron = '<a href="(\/tv\/.+?)".*?<img alt="(.+?)".*?itemprop="thumbnailUrl" src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="series_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist

def top(item):
    logger.info("pelisalacarta.channels.estrenosdoramas top")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    #data1 = scrapertools.get_match(data, '"popularList"(.+?)"tvPopularMoreLink"')
    patron  = 'href="(\/tv\/(.*?)-(.*?))"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl, scrapedid, scrapedtitle in matches:
        title = scrapedtitle	
        title = title.replace('-',' ')
        thumbnail = ""
        fanart = ""
        plot = ""
        url = "https://www.viki.com//related_videos?container_id="+scrapedid+"&page=1&type=episodes"
        show = item.show
        itemlist.append( Item(channel=__channel__, action="capitulos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, fulltitle=title, show=show))		


    patron = "href='(.+?)'>Siguiente"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = "https://www.viki.com"+match
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="top", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
        else:
			itemlist.append(Item(channel=__channel__, action="", title="---Fin de la lista---", folder=True))
    return itemlist

	
def series_(item):
    logger.info("pelisalacarta.channels.viki generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    josue = data
    data1 = scrapertools.get_match(data,'table class="table">(.+?)</table')
    patron = 'href="(/drama/(.*?)/.*?)".*?<img.*?src="(.+?)".*?class="info">.*?<h3>(.+?)</h3>.*?class="synopsis">.*?<p>(.+?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data1)
    for scrapedurl, scrapediddrama, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapertools.entityunescape(scrapedtitle)		
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = "https://"+scrapedthumbnail
        plot = scrapertools.htmlclean(scrapedplot)
        fanart = thumbnail.replace("200","900")
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="capitulos", title=title, url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))

    patron = '</a>.*<a href="(\?page=.+?)"><i class="icon-caret-right"></i></a>'
    matches = re.compile(patron, re.DOTALL).findall(josue)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = "https://www.viki.com/es/browse/genre/all/popular"+match
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="series_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
        else:
			itemlist.append(Item(channel=__channel__, action="", title="---Fin de la lista---", folder=True))
    return itemlist


def capitulos(item):
    logger.info("pelisalacarta.channels.viki capitulos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')		
    patron  = 'href="(.+?)".*?itemprop="thumbnailUrl" src="(.+?)".*?itemprop="name">(.+?)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        thumbnail = scrapedthumbnail
        fanart = scrapedthumbnail
        url = "http://www.descargavideos.tv/?ajax=1&web=https://www.viki.com"+scrapedurl
        plot = "https://www.viki.com/"+scrapedurl
        web = scrapertools.cache_page( "https://downsub.com/?url=https://www.viki.com"+scrapedurl+"", headers=headers)	
        sub1 = scrapertools.find_single_match(web, 'Spanish.*?a href=".(.+?)"')		
        if len(sub1)>0:
           title = "Capítulo" +scrapedtitle+ "  ESPAÑOL"
           itemlist.append( Item(channel=__channel__, action="resolution", subtitle="https://downsub.com"+ sub1, title=title , url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow", fulltitle=item.title, contentTitle=item.title, context=["buscar_trailer"], show=item.title))		
        else:			
           title = "Capítulo" +scrapedtitle+ "  INGLÉS"
           sub1 = scrapertools.find_single_match(web, 'English.*?a href=".(.+?)"')		   
           itemlist.append( Item(channel=__channel__, action="resolution", subtitle="https://downsub.com"+ sub1, title=title , url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow", fulltitle=item.title, contentTitle=item.title, context=["buscar_trailer"], show=item.title))
    return itemlist
	
def resolution(item):
    logger.info("pelisalacarta.channels.viki resolution")
    itemlist = []	
    headers = DEFAULT_HEADERS[:]	
    data3 = scrapertools.cache_page(item.url, headers=headers)	
    patron = 'class="txt">(.+?)</.*?id="urls.".*?value="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data3)
    for scrapedcalidad, scrapedurl in matches:
        title = "CALIDAD:  "+scrapedcalidad
        thumbnail = item.thumbnail
        plot = scrapedurl
        url = scrapedurl	
        itemlist.append( Item(channel=__channel__, action="play", server="directo",subtitle=item.subtitle, title=title , url=url, thumbnail=thumbnail, plot=plot))
    return itemlist



	

def search(item,texto):
    logger.info("pelisalacarta.channels.viki search")
    texto = texto.replace(" ","+")
    item.url = ("https://www.bing.com/search?q=site%3Aviki.com%2Fes%2Fdrama+" + texto)	
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
    itemlist = [] 
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url ,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')		
    patron = '"https://www.viki.com/es/drama/(.+?)/(.+?)/.*?"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedid, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = "https://www.viki.com/es/drama/"+scrapedid
        thumbnail = ""
        plot = ""
        fanart = ""
        itemlist.append(Item(channel=__channel__, action="capitulos", title=title, url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title, folder=True,))		

    return itemlist	
