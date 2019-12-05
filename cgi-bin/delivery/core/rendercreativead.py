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
import sys




def renderad():
	qs = os.environ['QUERY_STRING']
	d = parse_qs(qs)
	zoneid = d.get('zoneid',[''])[0]
	#print(zoneid)
	
	protocol			= ''
	dfpClickUrl			= ''
	if not(d.get('adurl',[''])[0] is None):
		Original_url		= qs#.lower()
		first_index 		= Original_url.find("&click");
		first_string 		= Original_url[first_index:]
		second_index 		= first_string.find("&ord=")
		dfpClickUrl 		= first_string[len("&click")+1:second_index]
	
	#print(dfpClickUrl)
	#sys.exit()
	
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
	deliveryUrl			= "https://api.onetracky.com/cgi-bin/delivery/"
	pydeliveryUrl 		= "https://onetracky.com/pydelivery/"
	
	
	cbString 	= 	hashlib.md5(str(randint(100, 999)).encode())
	cb			= cbString.hexdigest()
	cb			= cb[0:8]
	#print(banner)
	
	if banner['url']:
		if dfpClickUrl:
			clickurl					= dfpClickUrl;
		else:
			clickurl					= deliveryUrl+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
		
	else:
		clickurl					= deliveryUrl()+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
	
	
	if(banner['htmltemplate']):
		width 			= banner['width']
		if(not(dfpClickUrl  and width == 1 )):
			
			
			player		= banner['htmltemplate']
			
			player 		= player.replace("{clickurl}", clickurl)
			
			player	   +="<img deliveryUrl='"+deliveryUrl+"core/lgimpr.py?bannerid="+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb+"' width='1' height='1' alt=''>";
			if(banner['tracking_pixel']):
				buster			= cb;
				trackingPixel 	= banner['tracking_pixel'].replace("{cache}","$buster")
				player			+="<img deliveryUrl='"+trackingPixel+"' width='1' height='1' alt=''>";
			
			return player;
		else:
			
			creativeCode = richMediaCode(banner,zoneid,deliveryUrl, dfpClickUrl,cb,pydeliveryUrl);
			
			return creativeCode;
		
		
	else:
		return ""

		
def richMediaCode(banner, zoneid, deliveryUrl, dfpClickUrl,cb,pydeliveryUrl):
	type 		= banner['rich_media_type']		
	if(type == 1):
		fileName = 'expandorightleft';
		
	elif(type ==2):
		fileName = 'expandotopbottom';
		
	elif(type == 3):
		fileName  = 'pagepusher';
	
	elif(type == 4):
		fileName  = 'overlay';
	
	
	ext 			= '.js';
	fileNameExt 	= fileName+ext;
	deliveryPath	= '/home2/onetrack/public_html/django2adserver/cgi-bin/delivery/'
	pydeliveryPath	= '/home2/onetrack/public_html/pydelivery/'
	filePath 		= deliveryPath+'buster/'+fileNameExt;
	
	creativeImage1					= pydeliveryUrl+'media/'+banner['filename'];
	if(banner['rich_media_type'] != 4):
		creativeImage2					= pydeliveryUrl+'media/'+banner['filename2'];
	lgimprTracker					= deliveryUrl+"core/lgimpr.py?bannerid="+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;

	thirdParyTracker	= '';
	if(banner['tracking_pixel']):
		buster					= cb;
		trackingPixel  			= banner['tracking_pixel'].replace("{cache}",buster);
		thirdParyTracker		= '<img deliveryUrl="'+trackingPixel+'" width="1" height="1" alt="">';
	
	
	
	
	
	
	busterTpl 						= open(filePath,'r')

	busterContent   	    		= busterTpl.read()
	
	busterContent 					= busterContent.replace("{imagePath1}", creativeImage1);
	if(banner['rich_media_type'] != 4):
		busterContent 					= busterContent.replace("{imagePath2}", creativeImage2);
	
	busterContent 					= busterContent.replace("{clickurl}", dfpClickUrl);
	busterContent 					= busterContent.replace("{lgimprTracker}", lgimprTracker);
	busterContent 					= busterContent.replace("{thirdParyTracker}", thirdParyTracker);
	
	bannerid						= banner['bannerid'];
	putFilePath 					= pydeliveryPath+'bustercache/'+str(bannerid)+'_'+fileNameExt;
	#print(putFilePath)
	#print(busterContent)
	#sys.exit()
	
	busterWTpl 						= open(putFilePath,'w+')
	busterWTpl.write(busterContent);
	busterWTpl.close()
	

	getFilePath					= pydeliveryUrl+'bustercache/'+str(bannerid)+'_'+fileNameExt
	
	coreJs		    	= '<script src="'+pydeliveryUrl+'assets/js/jQuery-2.1.4.min.js'+'" type="text/javascript"></script>'
	scriptFile 			= '<script src='+getFilePath+'></script>'
	ifm 				= "<script type='text/javascript'>var referenceabc	= '"+dfpClickUrl+"'</script>"
	return coreJs+scriptFile+ifm;


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
		
