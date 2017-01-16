# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - kodi Plugin
# Canal por josuecocr
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
__title__ = "estrenosdoramas"
__channel__ = "estrenosdoramas"
__language__ = "ES"
__creationdate__ = "20160409"

host = "http://estrenosdoramas.org/"

DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"] )
DEFAULT_HEADERS.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])
DEFAULT_HEADERS.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
DEFAULT_HEADERS.append( ["Referer","http://estrenosdoramas.org"] )

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.estrenosdoramas mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="dramas_", title="Lista Dramas", url=urlparse.urljoin(host, "category/doramas-online")))
    itemlist.append(Item(channel=__channel__, action="letras", title="Listado alfabetico", url="http://estrenosdoramas.org/"))	
    itemlist.append(Item(channel=__channel__, action="generos", title="Listado Género", url="http://estrenosdoramas.org/"))	
    itemlist.append(Item(channel=__channel__, action="ultimos_d", title="Ultimos Capítulos", url="http://estrenosdoramas.org/category/ultimos-capitulos-online"))		
    itemlist.append(Item(channel=__channel__, action="peliculas", title="Películas", url="http://www.estrenosdoramas.org/category/peliculas"))	
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url="http://www.estrenosdoramas.org/?s="))    

    return itemlist

def letras(item):
    logger.info("pelisalacarta.channels.estrenosdoramas letras")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data = scrapertools.get_match(data,'<div class="alfabetosuperior">(.+?)</ul></div>')	
    patron = 'href="(.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="dramas_", title=title, url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow"))

    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="dramas_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.estrenosdoramas generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'id="genuno"(.+?)</div></div>')
    patron = 'href="(.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="dramas_", title=title, url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow"))

    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="dramas_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

def ultimos_d(item):
    logger.info("pelisalacarta.channels.estrenosdoramas ultimos_d")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'class="portadas">(.+?)class="title"')
    patron = '<div class="clearfix"><a href="(.+?)"><img src="(.+?)" alt="(.+?)" class="'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot, contentType="tvshow"))

    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="ultimos_d", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

def dramas_(item):
    logger.info("pelisalacarta.channels.estrenosdoramas dramas_")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data, '<div class="portadas"(.+?)class="title"')
    patron  = '<div class="clearfix"><a href="(.+?)"><img src="(.+?)" alt="(.+?)" class="'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append( Item(channel=__channel__, action="capitulos" , title=title , url=url, thumbnail=thumbnail, plot="INFO PLUS PARA MÁS INFORMACIÓN", show=title, contentType="tvshow" , fulltitle=title, contentTitle=title, context=["buscar_trailer"]))		

    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="dramas_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

def peliculas(item):
    logger.info("pelisalacarta.channels.estrenosdoramas Peliculas")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data,'class="portadas"(.+?)</div><br/><br/>')	
    patron = '<div class="clearfix"><a href="(.+?)"><img src="(.+?)" alt="(.+?)" class="'
    matches = re.compile(patron, re.DOTALL).findall(data1)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        url = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot="INFO PLUS PARA MÁS INFORMACIÓN DE LA PELICULA", show=title, contentType="movie" , fulltitle=title, contentSerieName=title, context=["buscar_trailer"]))

    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="peliculas", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist

def capitulos(item):
    logger.info("pelisalacarta.channels.estrenosdoramas capitulos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    detalle = scrapertools.find_single_match(data, 'Sinopsis:(.*?)</div>')	
    year = scrapertools.find_single_match(data, 'Emisión.*?<b>(.*?)</')		
    genre = scrapertools.find_single_match(data, 'Géneros(.*?)<br')			
    data1 = scrapertools.get_match(data, '<div class="listanime">(.+?)</ul></div>')
    patron  = 'href="(.+?)" title="(.+?)"'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url, scrapedurl)
        fanart=item.fanart		
        show = item.show
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=item.thumbnail, plot="[COLOR yellow]Año: "+year+"[/COLOR]\n [COLOR red]Genero: "+genre+"\n[/COLOR] SINOPSIS: "+detalle+"", fulltitle=title, show=show,))		
		
    if config.get_library_support() and len(itemlist) > 0:
            itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]', url=item.url,
                             action="add_serie_to_library", extra="capitulos", contentSerieName=item.contentTitle ))		
    return itemlist


	
	
#---------------------------------------------------------------------------------------------------------------------------------------	
	
def findvideos(item):
    logger.info("pelisalacarta.channels.estrenosdoramas findvideos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    datas = scrapertools.cache_page(item.url,headers=headers)
    datas = datas.replace('\n','')
    datas = datas.replace('\r','')
    datas = scrapertools.get_match(datas,'#tab1(.+?)</div></div></div>')		
    patron = '<iframe.*?src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(datas)
    
    for scrapedurl in matches:
        if "http://repro.estrenosdoramas.net/repro/index.php" in scrapedurl:

            josue = scrapedurl
            headers = DEFAULT_HEADERS[:]
            data1 = scrapertools.cache_page(scrapedurl,headers=headers)
            data1 = data1.replace('\/','/') 
            data1 = data1.replace('\n','')
            data1 = data1.replace('\r','')			
            #data1 = data1.replace('https://goo.gl/klcbWi"','') 			
            #data1 = scrapertools.get_match(data1,'center>(.+?)center>')					
            patronr ='file.*?(http:.*?480p.*?[^\'\"]+?)[\'\"].*?label.*?[\'\"](.+?)[\'\"]'		
            sub1 = scrapertools.find_single_match(data1, '(http://api.viki.io/.+?es.srt.+?)"')
            matches = re.compile(patronr,re.DOTALL).findall(data1)            
            
            for scrapedurl, scrapedcalidad in matches:
            
               #if len(scrapedurl) > 0:
                 print scrapedurl +' '+scrapedcalidad
                 url = scrapedurl
                 title = scrapertools.unescape("Opcion [COLOR blue]VIKI[/COLOR]  " + scrapedcalidad).strip()
                 thumbnail = ""
                 fanart=item.fanart
                 plot = "WEB:["+josue+"]\nLINK:["+scrapedurl+"]\nSUBTITULOS:["+sub1+"]"
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle=""+sub1+"", thumbnail=item.thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))

        if "php?" in scrapedurl:
            josue = scrapedurl
            headers = DEFAULT_HEADERS[:]
            data1 = scrapertools.cache_page(scrapedurl,headers=headers)
            data1 = data1.replace('\/','/') 
            data1 = data1.replace('https://goo.gl/klcbWi"','') 			
            data1 = data1.replace('http-equiv"','') 						
            patronr ='[file|src].*?(http[^\'\"]+?)[\'|\"].*?label.*?([^\'\"]+p)[\'|\"]'
            matches = re.compile(patronr,re.DOTALL).findall(data1)            
            
            for scrapedurl, scrapedcalidad in matches:
            
               if len(scrapedurl) > 0:
                 print scrapedurl +' '+scrapedcalidad
                 url = scrapedurl
                 title = scrapertools.unescape("Opcion calidad " + "[COLOR yellow]"+scrapedcalidad+"[/COLOR]").strip()
                 thumbnail = ""
                 fanart=item.fanart
                 plot = "WEB:["+josue+"]                            LINK:["+scrapedurl+"]"
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, thumbnail=item.thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))
                 

				 
				 
			   
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=datas))
    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.folder = False

    return itemlist
		

#---------------------------------------------------------------------------------------------------------------------------------------

			   
def search(item,texto):
    logger.info("pelisalacarta.channels.estrenosdoramas search")
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
 
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url ,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data1 = scrapertools.get_match(data,'class="portadas"(.+?)class="title"')		
    patron = '<div class="clearfix"><a href="(.+?)"><img src="(.+?)" alt="(.+?)" class="'
    matches = re.compile(patron, re.DOTALL).findall(data1)
    itemlist = []
	
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        #itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot="", show=title, folder=True))
        if "capitulo" in scrapedurl:
          itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot="", show=title, folder=True, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"]))        
        elif "pelicula" in scrapedurl:
          itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot="", show=title, folder=True, contentType="movie"))        		  
        else:
          itemlist.append( Item(channel=__channel__, action="capitulos" , title=title , url=url, thumbnail=thumbnail, plot="", show=title, folder=True, contentType="tvshow"))			
	# páginación
    patron = 'class="nextpostslink" rel="next" href="(.+?)">'
    matches = re.compile(patron, re.DOTALL).findall(data1)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="scraper", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist