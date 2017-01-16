# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para doramastv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

DEBUG = config.get_setting("debug")
host = "http://doramastv.com/"
DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"] )


def mainlist(item):
    logger.info("pelisalacarta.channels.doramatv mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=item.channel, action="pagina_", title="En emision", url=urlparse.urljoin(host, "drama/emision")))
    itemlist.append(Item(channel=item.channel, action="letras", title="Listado alfabetico", url=urlparse.urljoin(host, "lista-numeros")))
    itemlist.append(Item(channel=item.channel, action="generos", title="Generos", url=urlparse.urljoin(host, "genero/accion")))
    itemlist.append(Item(channel=item.channel, action="pagina_", title="Ultimos agregados", url=urlparse.urljoin(host, "dramas/ultimos")))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", url=urlparse.urljoin(host, "buscar/anime/ajax/?title=")))

    return itemlist

def letras(item):
    logger.info("pelisalacarta.channels.daramatv letras")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)

    patron = ' <a href="(\/lista-.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist
	
def pagina_(item):
    logger.info("pelisalacarta.channels.daramatv letras" + item.url)
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data1 = scrapertools.get_match(data, '<div class="animes-bot">(.+?)<!-- fin -->')
    data1 = data1.replace('\n','')
    data1 = data1.replace('\r','')
    patron = 'href="(\/drama.+?)".+?<\/div>(.+?)<\/div>.+?src="(.+?)".+?titulo">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data1)
    for scrapedurl, scrapedplot, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        plot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append( Item(channel=item.channel, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title))
	
    patron = 'href="([^"]+)" class="next"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            show = item.show			
            fanart=item.fanart			
            itemlist.append(Item(channel=item.channel, action="pagina_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, fulltitle=title, show=show, fanart =fanart))
    return itemlist
	
def episodios(item):
    logger.info("pelisalacarta.channels.doramatv episodios")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, '<ul id="lcholder">(.+?)</ul>')
    patron  = '<a href="(.+?)".+?>(.+?)<'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = ""
        plot = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        show = item.show
        fanart=item.fanart		
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fulltitle=title, show=show, fanart =fanart))		
    return itemlist
	
def findvideos(item):
    logger.info("pelisalacarta.channels.doramatv findvideos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data = data.replace('%26','&')
    data = data.replace('http://zet.videosxd.org/repro-d/mvk?v=','http://vk.com/video_ext.php?oid=')
    data = data.replace('http://zet.videosxd.org/repro-d/vk?v=','http://vk.com/video_ext.php?oid=')	
    data = data.replace('http://zet.videosxd.org/repro-d/send?v=','http://sendvid.com/embed/')
    data = data.replace('http://zet.videosxd.org/repro-d/msend?v=','http://sendvid.com/embed/')
    data = data.replace('http://zet.videosxd.org/repro-d/vidweed?v=','http://www.videoweed.es/file/')
    data = data.replace('http://zet.videosxd.org/repro-d/nowv?v=','http://www.nowvideo.sx/video/')
    data = data.replace('http://zet.videosxd.org/repro-d/nov?v=','http://www.novamov.com/video/')
    patron = '<iframe src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    #for match in matches:
       
        #if match.startswith("http://zet.videosxd.org/repro-d/docsgo?v="):

             #headers = DEFAULT_HEADERS[:]
             #data1 = scrapertools.cache_page(match,headers=headers)
             #patronr ='<iframe src="(.+?)"'
             #matchesr = re.compile(patronr,re.DOTALL).findall(data1)            
			
             #for links in matchesr:
               #if len(links) > 0:			
                 #josue = links
                 #headers = DEFAULT_HEADERS[:]
                 #data2 = scrapertools.cache_page(links,headers=headers)
                 #data2 = data2.replace('\/','/') 
                 #data2 = data2.replace('\n','')
                 #data2 = data2.replace('\r','')			
                 #patront ='[file|src].*?(http[^\'\"]+?)[\'|\"].*?label.*?([^\'\"]+p)[\'|\"]'
                 #matchest = re.compile(patront,re.DOTALL).findall(data2)            
			
             #for scrapedurl, scrapedcalidad in matchest:
                    #if len(scrapedurl) > 0:
                        #print scrapedurl +' '+scrapedcalidad
                        #url = scrapedurl
                        #title = scrapertools.unescape("Opcion LINK DIRECTO " + scrapedcalidad).strip()
                        #thumbnail = ""
                        #fanart=item.fanart
                        #plot = "WEB:["+josue+"]                            LINK:["+scrapedurl+"]"
                        #if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                        #itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle="", thumbnail=thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))


    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = item.channel
        videoitem.folder = False
    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.doramatv generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')

    data = scrapertools.get_match(data,'<!-- Lista de Generos -->(.+?)<\/div>')
    patron = '<a href="(.+?)".+?>(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=item.channel, action="pagina_", title=title, url=url, thumbnail=thumbnail, plot=plot))

    return itemlist	


def search(item,texto):
    logger.info("pelisalacarta.channels.doramatv search")
    texto = texto.replace(" ","+")
    item.url = urlparse.urljoin(host, item.url + texto)	

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
    item.url = urlparse.urljoin(host, item.url)
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url ,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')		
    patron = '<a href="(.+?)".+?src="(.+?)".+?titulo">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
	
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=item.channel, action="pagina_" , title=title , url=url, thumbnail=thumbnail, folder=folder, show=title))
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