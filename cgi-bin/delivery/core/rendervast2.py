#!/usr/bin/python
print('Content-type: text/xml\r\n\r')
import json
import psycopg2
import webbrowser

import time
from random import randint

from datetime import datetime
import os
import pytz
from urlparse  import urlparse
import hashlib

def renderVastOutput():
	# zoneid					= _GET['zoneid']
	# adZoneAssocFile			= GLOBALS['cachePath']."delivery_ad_zone_".zoneid.".php"
	# adZoneAssocData			= json_decode(file_get_contents(adZoneAssocFile), true)

	# bannerid				= adZoneAssocData['ad_id']
	# my_file					= GLOBALS['cachePath']."delivery_ad_".bannerid.".php"
	
	# completeArr 			= json_decode(file_get_contents(my_file), true)
	# banner					= completeArr[0]
	# vast					= completeArr[1]
	
	# adSystem 			= 'media adserver'
	# adName   			= banner['description']
	# vastAdDescription	= 'Inline Video Ad'
	
	
	cbString 		= hashlib.md5(str(randint(100, 999)).encode())
	cb				= cbString.hexdigest()
	rand			= cb[0:10]
	
	zoneid			= 2
	bannerid		= 2
	banner								= {}
	banner['ext_bannertype']			= 'create_video'
	banner['url']						= 'http://localhost/abc/';
	deliveryPath						='http://localhost/abc/';
	
	vast		= {
		'vast_thirdparty_erorr'		:deliveryPath+'core/error/vast-error.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=none&cb="+rand,
		'vast_thirdparty_impression':deliveryPath+'core/lgimpr.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=impression&cb="+rand,
		'third_party_click'			:deliveryPath+'core/ckvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=clicks&cb="+rand,
		'start_pixel'				:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=start",
		'quater_pixel'				:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=firstquartile",
		'mid_pixel'					:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=midpoint",
		'third_quater'				:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=thirdquartile",
		'end_pixel'					:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=complete",
		'generalUrl'				:deliveryPath+'core?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=none", 	
		'mute'						:deliveryPath+'core?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=mute", 	
		'unmute'					:deliveryPath+'core?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=unmute", 	
		'skip'						:deliveryPath+'core/lgvast.py?bannerid='+str(bannerid)+"&zoneid="+str(zoneid)+"&event=skip", 	
	}	
	
	person = {'vast_thirdparty_erorr': 'Eric', 'age': 74}
	

	
	# if banner['ext_bannertype']=='create_video'):
		# vast['vast_video_outgoing_filename']	= deliveryPath+"banners/videos/"+vast['vast_video_outgoing_filename']
	
	
	
	
	# if (array_key_exists('HTTP_ORIGIN', $_SERVER)) {
		# $origin = $_SERVER['HTTP_ORIGIN'];
	# }
	# else if (array_key_exists('HTTP_REFERER', $_SERVER)) {
		# $origin = $_SERVER['HTTP_REFERER'];
	# } else {
		# $origin = $_SERVER['REMOTE_ADDR'];
	# }
	
	player   = "";
	# header("Content-type: text/xml");
	# header("Access-Control-Allow-Credentials: true");
	# header("Access-Control-Allow-Origin: *");
	
	player	  = "<?xml version=\"1.0\"  encoding='UTF-8'?>"
	
	player	  = """<VAST version=\"3.0\">
		<Ad id=\"697200496\">"""
	
	if(banner['ext_bannertype']=='create_video'):
		player	  += "<InLine>"
		player	  += """<AdSystem>MediaConverison</AdSystem>
			<AdTitle>Media Ads</AdTitle>
			<Description>MediaConverison Vast Tag</Description>"""
	else:
		player	  += """<Wrapper>"""
		player	  += """<AdSystem>MediaConverison</AdSystem>
						<AdTitle>Media Ads</AdTitle>
						<Description>MediaConverison Vast Tag</Description>"""
		player	  += """<VASTAdTagURI><![CDATA[${vast['vast_tag']}]]></VASTAdTagURI>"""
		
	player	  +="""
			<Error><![CDATA[{start_pixel}]]></Error>
			<Impression><![CDATA[{vast_thirdparty_impression}]]></Impression>
			<Creatives>
	<Creative id=\"57860459056\" sequence=\"1\">
	<Linear skipoffset=\"00:00:05\">
	<Duration>00:00:30</Duration>
	<TrackingEvents>
	<Tracking event=\"start\"><![CDATA[{start_pixel}]]></Tracking>
	<Tracking event=\"firstQuartile\"><![CDATA[{quater_pixel}]]></Tracking>
	<Tracking event=\"midpoint\"><![CDATA[{mid_pixel}]]></Tracking>
	<Tracking event=\"thirdQuartile\"><![CDATA[{third_quater}]]></Tracking>
	<Tracking event=\"complete\"><![CDATA[{end_pixel}]]></Tracking>
	<Tracking event=\"mute\"><![CDATA[{mute}]]></Tracking>
	<Tracking event=\"unmute\"><![CDATA[{unmute}]]></Tracking>
	<Tracking event=\"rewind\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"pause\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"resume\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"fullscreen\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"creativeView\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"exitFullscreen\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"acceptInvitationLinear\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"closeLinear\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"skip\"><![CDATA[{skip}]]></Tracking>
	<Tracking event=\"progress\" offset=\"00:00:05\"><![CDATA[{generalUrl}]]></Tracking>
	<Tracking event=\"progress\" offset=\"00:00:30\"><![CDATA[{generalUrl}]]></Tracking>
	</TrackingEvents>""".format(**vast)
	
	if(banner['ext_bannertype']=='create_video'):
		player	  +="""<VideoClicks>
			<ClickThrough><![CDATA[{start_pixel}]]></ClickThrough>
			<ClickTracking><![CDATA[{third_party_click}]]></ClickTracking>
		</VideoClicks>		
		<MediaFiles>
			<MediaFile id=\"GDFP\" delivery=\"progressive\" width=\"1280\" height=\"720\" type=\"video/mp4\" bitrate=\"533\" scalable=\"true\" maintainAspectRatio=\"true\">http://localhost/media/video.mp4</MediaFile>
		</MediaFiles>""".format(**vast)
	
	else:
		player	  +="""<VideoClicks>
			<ClickTracking><![CDATA[{third_party_click}]]></ClickTracking>
		</VideoClicks>"""
	
	player	  +="""</Linear>
	</Creative>
	<Creative id=\"57857370976\" sequence=\"1\">
	<CompanionAds>
	<Companion id=\"57857370976\" width=\"300\" height=\"250\">
	<StaticResource creativeType=\"image/png\"></StaticResource>
	<TrackingEvents>
	<Tracking event=\"creativeView\"></Tracking>
	</TrackingEvents>
	<CompanionClickThrough>
	</CompanionClickThrough>
	</Companion>
	</CompanionAds>
	</Creative>
	</Creatives>"""
	
	if(banner['ext_bannertype']=='create_video'):
		player	  += """</InLine>"""
	else:
		player	  += """</Wrapper>"""
	
	player	  += """</Ad>
	</VAST>"""
	
	return player

print(renderVastOutput())
