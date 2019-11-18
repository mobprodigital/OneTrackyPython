#!/usr/bin/python
print('Content-type: text/html\r\n\r')
import cgi,cgitb
cgitb.enable()

import json
from urlparse  import urlparse
import hashlib
import time
from random import randint
import cgi,cgitb
from cgi import parse_qs, escape
import os



def renderad():
	d = parse_qs(os.environ['QUERY_STRING'])
	zoneid = d.get('zoneid',[''])[0]
	
	
	protocol			= ''
	dfpClickUrl			= ''
	ip					= ''
	iframe				= ''
	
	myFile				= "../cache/"+"delivery_ad_zone_"+str(zoneid)+".py"
	f					= open(myFile,"r")
	jsonString			= f.read()
	zonedata  			= json.loads(jsonString)
	f.close();
	
	adId				= zonedata['ad_id'];
	myFile				= "../cache/"+"delivery_ad_"+str(adId)+".py"
	f					= open(myFile,"r")
	jsonString			= f.read()
	bannerdata  		= json.loads(jsonString)
	f.close();
	#print(bannerdata)
	
	
	renderdata		= html5CreativeCode(bannerdata,zoneid,protocol,dfpClickUrl,ip,iframe)
	#print(renderdata)
	varString 	= 	hashlib.md5(str(randint(100, 999)).encode())
	var			= varString.hexdigest()
	var			= var[0:8]
	return MAX_javascriptToHTML(renderdata, 'MS_'+var)


def html5CreativeCode(banner, zoneid, protocol, dfpClickUrl, ip,iframe):
	src			= "https://api.onetracky.com/cgi-bin/delivery/"
	mediaUrl 	= "https://onetracky.com/pydelivery/"
	parsed_uri 	= urlparse('https://stackoverflow.com')
	if(parsed_uri.scheme == 'https'):
		src	= src.replace('https','http')
	
	cbString 	= 	hashlib.md5(str(randint(100, 999)).encode())
	cb			= cbString.hexdigest()
	cb			= cb[0:8]
	#print(banner)
	
	if banner['url']:
		if dfpClickUrl:
			clickurl					= dfpClickUrl;
		else:
			clickurl					= src+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
		
	else:
		clickurl					= src()+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
	
	
	if(banner['htmltemplate']):
		width 			= banner['width']
		if(not(dfpClickUrl  and width == '1' )):
			
			player		= banner['htmltemplate']
			
			player 		= player.replace("{clickurl}", clickurl)
			
			player	   +="<img src='"+src+"core/lgimpr.py?bannerid="+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb+"' width='1' height='1' alt=''>";
			if(banner['tracking_pixel']):
				buster			= cb;
				trackingPixel 	= banner['tracking_pixel'].replace("{cache}","$buster")
				player			+="<img src='"+trackingPixel+"' width='1' height='1' alt=''>";
			
			return player;
		else:
			creativeCode = richMediaCode(banner,zoneid,src, dfpClickUrl,cb);
			return creativeCode;
		
		
	else:
		return ""

		
# def richMediaCode(banner, zoneid, src, dfpClickUrl,cb):
	# type 		= banner['rich_media_type']		
	# if(type == 1):
		# fileName = 'expandorightleft';
		
	# elif(type ==2):
		# fileName = 'expandotopbottom';
		
	# elif(type == 3):
		# fileName  = 'pagepusher';
	
	# elif(type == 4):
		# fileName  = 'overlay';
	
	
	# ext 			= '.js';
	# fileNameExt 	= fileName+ext;
	# filePath 		= GLOBALS['deliveryPath']+'buster/'+fileNameExt;
	
	# creativeImage1					= GLOBALS['deliveryPath']+'banners/images/'+banner['filename'];
	# creativeImage2					= GLOBALS['deliveryPath']+'banners/images/'+banner['filename2'];
	# lgimprTracker					= src+"core/lgimpr.php?bannerid="+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;

	# thirdParyTracker	= '';
	# if(banner['tracking_pixel']):
		# buster					= cb;
		# trackingPixel  			= str_replace("{cache}","buster",banner['tracking_pixel']);
		# thirdParyTracker		= '<img src="'+trackingPixel+'" width="1" height="1" alt="">';
	
	
	# busterFileName 					= filePath;
	# busterContent   	    		= file_get_contents(busterFileName);
	# busterContent 					= str_replace("{imagePath1}", "creativeImage1", busterContent);
	# busterContent 					= str_replace("{imagePath2}", "creativeImage2", busterContent);
	# busterContent 					= str_replace("{clickurl}", "dfpClickUrl", busterContent);
	# busterContent 					= str_replace("{lgimprTracker}", lgimprTracker, busterContent);
	# busterContent 					= str_replace("{thirdParyTracker}", thirdParyTracker, busterContent);
	# busterPath						= GLOBALS['includePathDelivery']+'buster/'+fileNameExt;
	# bannerid						= banner['bannerid'];
	# putFilePath 					= GLOBALS['includePathDelivery']+'bustercache/'+str(bannerid)+'_'+fileNameExt;
	# file_put_contents(putFilePath, busterContent);
	# getFilePath					= GLOBALS['deliveryPath']+'bustercache/'+str(bannerid)+'_'+fileNameExt
	
	# coreJs		    	= '<script src="'+GLOBALS['deliveryPath']+'assets/js/jQuery-2.1.4.min.js'+'" type="text/javascript"></script>'
	# scriptFile 			= '<script src='+getFilePath+'></script>'
	# ifm 				= "<script type='text/javascript'>var referenceabc	= '"+dfpClickUrl+"'</script>"
	# return coreJs+scriptFile+ifm;


def MAX_javascriptToHTML(string, varName, output = True, localScope = True):
	jsLines = []
	buffer	= ""
	
	
	string 		= string.replace("\\","\\\\")
	string 		= string.replace("\r",'')
	
	string 		= string.replace('"','\\"')
	
	string 		= string.replace("'","\\'")
	string 		= string.replace('<','<"+"')
	lines 		= string.split("\n")
	for line in lines:
		if(line.strip() != '') :
			jsLines.append(varName + ' += "' + line.strip() + '\\n";')
			
	buffer	+= 'var ' if localScope else ''
	buffer	+= varName +" = '';\n"
	buffer  += jsLines[0]#"\n".join(jsLines)
	if (output == True):
		buffer += "\ndocument.write("+varName+");\n";
	
	return buffer;
	
	
	

print(renderad())
		
