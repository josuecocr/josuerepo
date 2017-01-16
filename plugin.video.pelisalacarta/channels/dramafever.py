# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para dramafever
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
__title__ = "dramafever"
__channel__ = "dramafever"
__language__ = "ES"
__creationdate__ = "20160404"

host = "https://www.dramafever.com"

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
    logger.info("pelisalacarta.channels.dramafever mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="series_", title="Lista de Series", url="https://www.dramafever.com/es/browse/genre/all/popular"))
    itemlist.append(Item(channel=__channel__, action="ultimos_c", title="Ultimos Capítulos Agregados", url="https://www.dramafever.com/es/"))
    itemlist.append(Item(channel=__channel__, action="categorias", title="Categorias", url="https://www.dramafever.com/es/browse/genre/all/popular"))
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url=("https://www.bing.com/search?q=site%3Adramafever.com%2Fes%2Fdrama")))


    return itemlist

def categorias(item):
    logger.info("pelisalacarta.channels.dramafever categorias")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'<dd class="options genre">(.+?)</dd')
    patron = 'data-type="genre" data-slug=".*?" href="(.+?)">(.+?)<'
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

def ultimos_c(item):
    logger.info("pelisalacarta.channels.estrenosdoramas ultimos_c")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, "Últimos Capítulos en DramaFever(.+?)Popular Esta Semana")
    patron  = '<a href="(.+?)" class="pull-left evt-tap">(.+?)</a>.*?"episode-number normal-state">(.+?)<'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl,scrapedtitle, scrapedep in matches:
        title = scrapertools.htmlclean(scrapedtitle)+"  "+scrapedep
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        show = item.show
        itemlist.append( Item(channel=__channel__, action="capitulos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, show=show))		

    return itemlist

	
def series_(item):
    logger.info("pelisalacarta.channels.dramafever generos")
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
            scrapedurl = "https://www.dramafever.com/es/browse/genre/all/popular"+match
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="series_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
        else:
			itemlist.append(Item(channel=__channel__, action="", title="---Fin de la lista---", folder=True))
    return itemlist


def capitulos(item):
    logger.info("pelisalacarta.channels.dramafever capitulos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    id = scrapertools.find_single_match(data, 'data-sid="(.+?)"')		
    patron  = 'data-eid="(.+?)"></i></span>(.+?)</'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedtitle, scrapedplot in matches:

        thumbnail = item.thumbnail
        fanart = item.fanart
        web = "https://www.dramafever.com/amp/episode/feed.json?guid="+id+"."+scrapedtitle+"&hd=False"
        data1 = scrapertools.cache_page(web,headers=headers)		
        url2 = scrapertools.find_single_match(data1, ', {"@attributes": {"url": "(https.*?)"')
        url2 = url2.replace('https','http')		
        sub1 = scrapertools.find_single_match(data1, '"lang": "Spanish", "href": "(.+?)"')				
        url = url2		
        plot = url2
        if len(sub1)>0:
           title = "Capítulo" +scrapedtitle+ "  ESPAÑOL"
           itemlist.append( Item(channel=__channel__, action="resolution", subtitle="https://downsub.com/index.php?title=DramaFever&url="+ sub1, title=title , url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow", fulltitle=item.title, contentTitle=item.title, context=["buscar_trailer"], show=item.title))		
        else:			
           title = "Capítulo" +scrapedtitle+ "  INGLÉS"
           sub1 = scrapertools.find_single_match(data1, '"lang": "English", "href": "(.+?)"')
           sub1 = sub1.replace('https','http')			   
           itemlist.append( Item(channel=__channel__, action="resolution", subtitle="https://downsub.com/index.php?title=DramaFever&url="+ sub1, title=title , url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow", fulltitle=item.title, contentTitle=item.title, context=["buscar_trailer"], show=item.title))
    return itemlist
	
def resolution(item):
    logger.info("pelisalacarta.channels.dramafever resolution")
    itemlist = []	
    headers = DEFAULT_HEADERS[:]	
    data3 = scrapertools.cache_page(item.url, headers=headers)	
    patron = 'RESOLUTION=.*?x(.*?),.*?\n(http.*?)\n'
    matches = re.compile(patron, re.DOTALL).findall(data3)
    for scrapedcalidad, scrapedurl in matches:
        title = "CALIDAD:  "+scrapedcalidad
        thumbnail = item.thumbnail
        plot = scrapedurl
        url = scrapedurl	
        itemlist.append( Item(channel=__channel__, action="repro", subtitle=item.subtitle, title=title , url=url, thumbnail=thumbnail, plot=plot))
    return itemlist

def repro(item):
    logger.info("pelisalacarta.channels.dramafever repro")
    itemlist = []	
    headers = DEFAULT_HEADERS[:]	
    data3 = scrapertools.anti_cloudflare(item.url, headers=headers)	
    title = "LINK DRAMAFEVER"
    thumbnail = item.thumbnail	
    plot = get_cookie_value()
    head = header_string1 + get_cookie_value()
    heade = head + header_string2
    url = item.url + heade		
    itemlist.append( Item(channel=__channel__, action="play", subtitle=item.subtitle, server="directo", title=title , url=url, thumbnail=thumbnail, plot=plot))
    return itemlist		


def get_cookie_value():
    itemlist = []
    cookies = os.path.join(config.get_data_path(), 'cookies', 'dramafever-i.akamaihd.net.dat')
    cookiedatafile = open(cookies, 'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close()
    cfduid = scrapertools.find_single_match(cookiedata, ".dramafever-i.akamaihd.net.*?_alid_\s+(.+)\n")
    cfduid = "_alid_=" + cfduid + ";"
    cookies_value = cfduid
 
    return cookies_value
	
	

def search(item,texto):
    logger.info("pelisalacarta.channels.dramafever search")
    texto = texto.replace(" ","+")
    item.url = ("https://www.bing.com/search?q=site%3Adramafever.com%2Fes%2Fdrama+" + texto)	
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
    patron = '"https://www.dramafever.com/es/drama/(.+?)/(.+?)/.*?"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedid, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle)
        url = "https://www.dramafever.com/es/drama/"+scrapedid
        thumbnail = ""
        plot = ""
        fanart = ""
        itemlist.append(Item(channel=__channel__, action="capitulos", title=title, url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title, folder=True,))		

    return itemlist	
