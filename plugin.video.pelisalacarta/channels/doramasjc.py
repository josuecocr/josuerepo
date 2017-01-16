# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para doramasjc
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
__title__ = "doramasjc"
__channel__ = "doramasjc"
__language__ = "ES"
__creationdate__ = "20160216"

host = "http://doramasjc.com/"


DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"] )

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.channels.doramatv mainlist")
	
    itemlist = list([])
    itemlist.append(Item(channel=__channel__, action="ultimos", title="Ultimos Episodios", url=host))
    itemlist.append(Item(channel=__channel__, action="letras", title="Listado alfabetico", url=urlparse.urljoin(host, "doramas/")))
    itemlist.append(Item(channel=__channel__, action="generos", title="Generos", url=urlparse.urljoin(host, "doramas/")))
    itemlist.append(Item(channel=__channel__, action="pagina_", title="En Emision", url=urlparse.urljoin(host, "en-emision/")))
    itemlist.append(Item(channel=__channel__, action="search", title="Buscar", url=urlparse.urljoin(host, "buscar/")))

    return itemlist

def ultimos(item):
    logger.info("pelisalacarta.channels.doramasjc Ultimos")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data = scrapertools.get_match(data,'class="ultimos_epis"(.+?)<!-- ultimos episodios -->')	
    patron = '<a href="(.+?)".*?img.*?src="(.+?)".*?class="">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="findvideos", title=title, url=url, thumbnail=item.thumbnail, plot=plot))

    return itemlist	

	
def letras(item):
    logger.info("pelisalacarta.channels.doramasjc letras")

    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data = scrapertools.get_match(data,'<div class="alfabeto_box"(.+?)</div>')	
    patron = '<a href="(.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=item.thumbnail, plot=plot))

    return itemlist
	
def pagina_(item):
    logger.info("pelisalacarta.channels.doramasjc letras" + item.url)
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')	
    data = data.replace('http://www.doramasjc.com/favicon.ico','')	
    detalle = scrapertools.find_single_match(data, 'class="sinopsis">(.*?)<')	
    year = scrapertools.find_single_match(data, 'Fecha de Inicio:</b>(.*?)</')		
    genre = scrapertools.find_single_match(data, 'http://www.doramasjc.com/genero/(.*?)"')			
    patron = '<div class="aboxy_lista"><a href="(.+?)".*?title="(.+?)".*?<img.*?src="(.+?)".*?class="sinopsis">(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedsinopsis in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot="[COLOR yellow]Año: "+year+"[/COLOR]\n [COLOR red]Genero: "+genre+"\n[/COLOR] SINOPSIS: "+scrapedsinopsis+"", contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))
	
    patron = " href='([^']+)'>Siguiente"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            scrapedurl = urlparse.urljoin(item.url, match)
            scrapedtitle = "Pagina Siguiente >>"
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(Item(channel=__channel__, action="pagina_", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist
	
def episodios(item):
    logger.info("pelisalacarta.channels.doramasjc episodios")

    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    data = data.replace('<spam>','')	
    #data1 = scrapertools.get_match(data, 'id="listado_epis"(.+?)</div>')
    patron  = '<li><a href="(http://www.doramasjc.com/ver/.+?)">(.+?)</'
    matches = re.compile(patron,re.DOTALL).findall(data)
    itemlist = []    
    for scrapedurl,scrapedtitle in matches:
        title = scrapertools.htmlclean(scrapedtitle).strip()
        thumbnail = ""
        plot = item.plot
        url = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=item.thumbnail, plot=plot, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))		
    return itemlist
	
def findvideos(item):
    logger.info("pelisalacarta.channels.doramasjc findvideos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    patron = '<iframe.*?src="(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
       
        if scrapedurl.startswith("http://www.doramasjc.com/gkphp/mega.php?") or scrapedurl.startswith("http://www.doramasjc.com/gkphp/adrive.php"):

            josue = scrapedurl
            headers = DEFAULT_HEADERS[:]
            data1 = scrapertools.cache_page(scrapedurl,headers=headers)
            data1 = data1.replace('\/','/') 
            data1 = data1.replace('\n','')
            data1 = data1.replace('\r','')			
            #data1 = data1.replace('https://goo.gl/klcbWi"','') 			
            #data1 = scrapertools.get_match(data1,'center>(.+?)center>')					
            patronr ='[file|src].*?[\'\"](https://redirector[^\'\"]+?)[\'\"].*?type.*?(video/mp4+?)[\'\"]'
            sub1 = scrapertools.find_single_match(josue, 'cod=(.+?)\&')
            sub2 = scrapertools.find_single_match(josue, 'ep=(.+?)')
            matches = re.compile(patronr,re.DOTALL).findall(data1)            
            
            for scrapedurl, scrapedcalidad in matches:
            
               #if len(scrapedurl) > 0:
                 print scrapedurl +' '+scrapedcalidad
                 url = scrapedurl
                 title = scrapertools.unescape("Opcion mega y adrive calidad " + scrapedcalidad).strip()
                 thumbnail = ""
                 fanart=item.fanart
                 detalle = item.plot				 
                 plot = "WEB:["+josue+"]                            LINK:["+scrapedurl+"]\n DESCRIPCION"+detalle+""
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle="http://www.doramasjc.com/subtitulos/doramas/"+sub1+"/"+sub2+".vtt", thumbnail=item.thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))
   
        if scrapedurl.startswith("http://www.doramasjc.com/gkphp/html5.php"):

            josue = scrapedurl
            headers = DEFAULT_HEADERS[:]
            data1 = scrapertools.cache_page(scrapedurl,headers=headers)
            data1 = data1.replace('\/','/') 
            data1 = data1.replace('\n','')
            data1 = data1.replace('\r','')			
            #data1 = data1.replace('https://goo.gl/klcbWi"','') 			
            #data1 = scrapertools.get_match(data1,'center>(.+?)center>')					
            patronr ='[file|src].*?[\'\"](http://www.doramasjc.com/gkphp/html5tmp.php[^\'\"]+?)[\'\"].*?type.*?(video/mp4+?)[\'\"]'
            sub1 = scrapertools.find_single_match(josue, 'cod=(.+?)\&')
            sub2 = scrapertools.find_single_match(josue, 'ep=(.+?)')
            matches = re.compile(patronr,re.DOTALL).findall(data1)            
            
            for scrapedurl, scrapedcalidad in matches:
            
               #if len(scrapedurl) > 0:
                 print scrapedurl +' '+scrapedcalidad
                 url = scrapedurl
                 title = scrapertools.unescape("Opcion html5 calidad " + scrapedcalidad).strip()
                 thumbnail = ""
                 fanart=item.fanart
                 detalle = item.plot				 
                 plot = "WEB:["+josue+"]\nLINK:["+scrapedurl+"]\nSUBTITULOS:http://www.doramasjc.com/subtitulos/doramas/["+sub1+"]/["+sub2+"].vtt\n DESCRIPCION"+detalle+""
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle="http://www.doramasjc.com/subtitulos/doramas/"+sub1+"/"+sub2+".vtt", thumbnail=item.thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))
   			
        if scrapedurl.startswith("http://www.doramasjc.com/gkphp/ucloud.php"): 

            josue = scrapedurl
            headers = DEFAULT_HEADERS[:]
            data1 = scrapertools.cache_page(scrapedurl,headers=headers)
            data1 = data1.replace('\/','/') 
            data1 = data1.replace('\n','')
            data1 = data1.replace('\r','')			
            #data1 = data1.replace('https://goo.gl/klcbWi"','') 			
            #data1 = scrapertools.get_match(data1,'center>(.+?)center>')					
            patronr ='[file|src].*?[\'\"](http://userscloud.com[^\'\"]+?)[\'\"].*?type.*?(video/mp4+?)[\'\"]'		
            sub1 = scrapertools.find_single_match(josue, 'cod=(.+?)\&')
            sub2 = scrapertools.find_single_match(josue, 'ep=(.+?)')
            matches = re.compile(patronr,re.DOTALL).findall(data1)            
            
            for scrapedurl, scrapedcalidad in matches:
            
               #if len(scrapedurl) > 0:
                 print scrapedurl +' '+scrapedcalidad
                 url = scrapedurl
                 title = scrapertools.unescape("Opcion ucloud calidad " + scrapedcalidad).strip()
                 thumbnail = ""
                 fanart=item.fanart
                 detalle = item.plot
                 plot = "WEB:["+josue+"]                            LINK:["+scrapedurl+"]\nSUBTITULOS:http://www.doramasjc.com/subtitulos/doramas/["+sub1+"]/["+sub2+"].vtt\n DESCRIPCION"+detalle+""
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle="http://www.doramasjc.com/subtitulos/doramas/"+sub1+"/"+sub2+".vtt", thumbnail=item.thumbnail,plot=plot, fulltitle=title, show="", fanart =fanart, server="directo", folder=True,))

   			
        if scrapedurl.startswith("http://www.doramasjc.com/gkphp/viki/index.php"): 

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
                 title = scrapertools.unescape("Opcion VIKI calidad " + scrapedcalidad).strip()
                 thumbnail = ""
                 detalle = item.plot
                 plot = "WEB:["+josue+"]\nLINK:["+scrapedurl+"]\nSUBTITULOS:["+sub1+"]\n DESCRIPCION"+detalle+""
                 if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"])")
                 itemlist.append( Item(channel=__channel__, action="play" , title=title , url=scrapedurl, subtitle=""+sub1+"", thumbnail=item.thumbnail,plot=plot, fulltitle=title, show=plot, server="directo", folder=True,))
				 
   						

    # Opción "Añadir esta pelicula a la biblioteca de XBMC"
    if item.extra == "movies" and config.get_library_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=__channel__, title="Añadir esta película a la biblioteca de XBMC", url=item.url,
                             infoLabels= item.infoLabels, action="add_pelicula_to_library", extra="findvideos",
                             fulltitle=item.title, text_color= color2))

    from core import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.folder = False
    return itemlist

def generos(item):
    logger.info("pelisalacarta.channels.doramasjc generos")
    itemlist = []
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
	
    data = scrapertools.get_match(data,'<div class="generos_box"(.+?)</div>')
    patron = '<a href="(.+?)">(.+?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.entityunescape(scrapedtitle)
        url = urlparse.urljoin(host, scrapedurl)
        thumbnail = ""
        plot = ""
        if DEBUG:
            logger.info("title=[{0}], url=[{1}], thumbnail=[{2}]".format(title, url, thumbnail))

        itemlist.append(Item(channel=__channel__, action="pagina_", title=title, url=url, thumbnail=item.thumbnail, plot=plot))

    return itemlist
	
		   
def search(item,texto):
    logger.info("pelisalacarta.channels.doramasjc search")
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
    itemlist = [] 
    headers = DEFAULT_HEADERS[:]
    data = scrapertools.cache_page(item.url ,headers=headers)
    data = data.replace('\n','')
    data = data.replace('\r','')
    detalle = scrapertools.find_single_match(data, 'class="sinopsis">(.*?)<')	
    year = scrapertools.find_single_match(data, 'Fecha de Inicio:</b>(.*?)</')		
    genre = scrapertools.find_single_match(data, 'http://www.doramasjc.com/genero/(.*?)"')			
    patron = '<div class="aboxy_lista"><a href="(.+?)".*?title="(.+?)".*?<img.*?src="(.+?)".*?class="sinopsis">(.+?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedsinopsis in matches:
        title = scrapertools.unescape(scrapedtitle).strip()
        url = scrapedurl
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
#        if (DEBUG): logger.info("url=["+url+"], title=["+title+"])
        if "/dorama/" in scrapedurl:
           itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot="[COLOR yellow]Año: "+year+"[/COLOR]\n [COLOR red]Genero: "+genre+"\n[/COLOR] SINOPSIS: "+scrapedsinopsis+"", folder=True, contentType="tvshow", fulltitle=title, contentTitle=title, context=["buscar_trailer"], show=title))        
        thumbnail = urlparse.urljoin(host, scrapedthumbnail)
        show = item.show
	# páginación
#    patron = "href='(.+?)'>Siguiente &raquo;"
    #matches = re.compile(patron, re.DOTALL).findall(data)
    #for match in matches:
     #   if len(matches) > 0:
      #      scrapedurl = urlparse.urljoin(item.url, match)
       #     scrapedtitle = "Pagina Siguiente >>"
        #    scrapedthumbnail = ""
         #   scrapedplot = ""
#            itemlist.append(Item(channel=__channel__, action="scraper", title=scrapedtitle, url="http://www.doramasjc.com/"+scrapedurl+", thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True))
    return itemlist