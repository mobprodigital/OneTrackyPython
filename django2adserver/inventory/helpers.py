from django.db import connection
from inventory.models import rv_ad_zone_assoc
from inventory.serializers import rv_ad_zone_assocSerializer
from datetime import datetime,timedelta
import json


deliveryCorePath		= 'https://api.onetracky.com/cgi-bin/delivery/core/';
deliveryCachePath		= '../public_html/django2adserver/cgi-bin/delivery/cache/'



def getAssocOrderDetails(bannerid):
	with connection.cursor() as (cursor):
		sql = "SELECT c.clientid,c.clientname,m.campaignid,m.campaignname, b.bannerid, b.storagetype, b.width, b.height, b.description, b.status as banner_status, m.status as campaign_status, activate_time,expire_time, contenttype,b.weight as banner_weight, m.priority as campaign_priority, m.weight as campaign_weight FROM inventory_clients AS c, inventory_campaigns AS m, inventory_banners AS b WHERE c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid ='"+bannerid+"'"
		#print(sql)
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
		return result
		
		
def updateCampaignCacheData(campaignid,campaignData):
	with connection.cursor() as (cursor):
		sql = """
			SELECT 
				bannerid
			FROM
				inventory_banners AS b
			WHERE 
				b.campaignid ={campaignid}""".format(campaignid=campaignid)
				
		cursor.execute(sql)
		field_names 	= [item[0] for item in cursor.description]
		rawData 		= cursor.fetchall()
		result 			= []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
					
			updateDeliveryAd(objDict['bannerid'])
		return True
			
			


def getCampaignBannerCacheData(bannerid):
	with connection.cursor() as (cursor):
		sql = """
			SELECT 
				c.clientid as client_id,
				m.campaignid as campaign_id,
				m.status as campaign_status,
				activate_time,
				expire_time,
				views,
				target_impression	,
				capping_amount,
				capping_period_value,
				capping_period_type,
				m.priority as campagin_priority,
				m.weight as campagin_weight,
				
				bannerid,
				contenttype,
				storagetype,
				ext_bannertype,
				filename, 
				filename2,
				imageurl,
				htmltemplate,
				url,
				rich_media_type, 
				htmlcache	, 
				width,
				height,
				tracking_pixel,
				description, 
				compiledlimitation, 
				acl_plugins,
				b.updated as updated,
				acls_updated,
				multiple_banner_existence
			FROM
				inventory_clients AS c,
				inventory_campaigns AS m,
				inventory_banners AS b
			WHERE 
				c.clientid = m.clientid
				AND m.campaignid = b.campaignid
				AND b.bannerid ={bannerid}""".format(bannerid=bannerid)
				
	
			
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
		return result
		

def getVideoCacheData(bannerid):
	with connection.cursor() as (cursor):
		sql = """
			SELECT 
				banner_vast_element_id,
				banner_id,
				status active,
				vast_element_type,
				vast_video_id,
				skip, 
				skip_time,
				mute,
				autoplay ,
				impression_pixel ,
				start_pixel ,
				quater_pixel ,
				mid_pixel ,
				third_quater_pixel ,
				end_pixel ,
				third_party_click ,
				creative_view ,
				vast_tag ,
				vast_video_duration,
				vast_video_delivery,
				vast_video_type,
				vast_video_bitrate ,
				vast_video_height,
				vast_video_width,
				vast_video_outgoing_filename,
				vast_companion_banner_id ,
				vast_overlay_height ,
				vast_overlay_width ,
				vast_video_clickthrough_url,
				vast_overlay_action,
				vast_overlay_format,
				vast_overlay_text_title,
				vast_overlay_text_description,
				vast_overlay_text_call,
				vast_creative_type,
				vast_thirdparty_impression,
				vast_thirdparty_erorr 
			FROM
				inventory_banner_vast_element AS b
			WHERE 
				b.banner_id ={bannerid}""".format(bannerid=bannerid)
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		videoCacheData	={}
		if rawData:
			for row in rawData:
				data = {}
				for index, value in enumerate(row):
					data[field_names[index]] = value
			videoCacheData	= {
				"banner_vast_element_id": data.get('banner_vast_element_id'),
				"banner_id": data.get('banner_id'),
				"status": "active",
				"vast_element_type": data.get('vast_element_type'),
				"vast_video_id": data.get('vast_video_id'),
				"skip": data.get('skip'), 
				"skip_time": data.get('skip_time'),
				"mute": data.get('mute'),
				"autoplay": data.get('autoplay'),
				"impression_pixel": data.get('impression_pixel'),
				"start_pixel": data.get('start_pixel'),
				"quater_pixel": data.get('quater_pixel'),
				"mid_pixel": data.get('mid_pixel'),
				"third_quater_pixel": data.get('third_quater_pixel'),
				"end_pixel": data.get('end_pixel'),
				"third_party_click": data.get('third_party_click'),
				"creative_view": data.get('creative_view'),
				"vast_tag": data.get('vast_tag'),
				"vast_video_duration":data.get('vast_video_duration'),
				"vast_video_delivery": data.get('vast_video_delivery'),
				"vast_video_type": data.get('vast_video_type'),
				"vast_video_bitrate": data.get('vast_video_bitrate'),
				"vast_video_height": data.get('vast_video_height'),
				"vast_video_width": data.get('vast_video_width'),
				"vast_video_outgoing_filename": data.get('vast_video_outgoing_filename'),
				"vast_companion_banner_id": data.get('vast_companion_banner_id'),
				"vast_overlay_height": data.get('vast_overlay_height'),
				"vast_overlay_width": data.get('vast_overlay_width'),
				"vast_video_clickthrough_url": data.get('vast_video_clickthrough_url'),
				"vast_overlay_action": data.get('vast_overlay_action'),
				"vast_overlay_format": data.get('vast_overlay_format'),
				"vast_overlay_text_title": data.get('vast_overlay_text_title'),
				"vast_overlay_text_description": data.get('vast_overlay_text_description'),
				"vast_overlay_text_call": data.get('vast_overlay_text_call'),
				"vast_creative_type": data.get('vast_creative_type'),
				"vast_thirdparty_impression": data.get('vast_thirdparty_impression'),
				"vast_thirdparty_erorr": data.get('vast_thirdparty_erorr')
			}
		return videoCacheData
		
def updateDeliveryAd(bannerid):
	response		= getCampaignBannerCacheData(bannerid)
	data			= response[0]
	storagetype		= data.get('storagetype')
	cacheData		= {
		'client_id' 				: data.get('client_id'),
		
		'campaign_id'   			: data.get('campaign_id'),
		'campaign_status'			: data.get('campaign_status'),
		'activate_time'				: data.get('activate_time'),
		'expire_time'				: data.get('expire_time'),
		'views'						: data.get('views'),
		'target_impression'			: data.get('target_impression'),
		'capping_amount'			: data.get('capping_amount'),
		'capping_period_value'		: data.get('capping_period_value'),
		'capping_period_type'		: data.get('capping_period_type'),
		'campagin_priority'			: data.get('campagin_priority'),
		'campagin_weight'			: data.get('campagin_weight'),
		
		'bannerid' 					: data.get('bannerid'),
		'contenttype' 				: data.get('contenttype'),
		"storagetype"				: data.get('storagetype'),
		'ext_bannertype'			: data.get('ext_bannertype'),

		'filename'					: data.get('filename'), 
		'filename2'					: data.get('filename2'),
		'imageurl'					: data.get('imageurl'),
		'htmltemplate'				: data.get('htmltemplate'),
		'url'						: data.get('url'),
		'rich_media_type'			: data.get('rich_media_type'), 
		'htmlcache'					: data.get('htmlcache'), 
		'width' 					: data.get('width'),
		'height' 					: data.get('height'),
		'tracking_pixel'			: data.get('tracking_pixel'),
		'description'				: data.get('description'), 
		'compiledlimitation'		: data.get('compiledlimitation'), 
		'acl_plugins'				: data.get('acl_plugins'),
		'updated'					: data.get('updated'),
		'acls_updated'				: data.get('acls_updated'),
		'multiple_banner_existence'	: data.get('multiple_banner_existence')
	}
	
	bannerCache = 'delivery_ad_' + str(bannerid) + '.py'
	print(bannerCache)
	f 			= open(deliveryCachePath + bannerCache, 'w+')
	if storagetype == 'html':
		videoCacheData	= getVideoCacheData(bannerid)
		jsonArr 	= [cacheData,videoCacheData]
	else:
		jsonArr 	= cacheData
	#jsonString 	= json.dumps(jsonArr, indent=4, sort_keys=True, default=str)
	jsonString 		= json.dumps(jsonArr, indent=4, default=str)

	f.write(jsonString)
	f.close()




#def updateDeliveryZone():
#def updateDeliveryAdZoneAssoc():



def checkCampaignExpireStatus(campaigns,newExpireTime):
	with connection.cursor() as (cursor):
		now 			= datetime.now();
		oNowDateString 	= now.strftime('%Y-%m-%d');
		oNowDate		= datetime.strptime(oNowDateString,'%Y-%m-%d').date()
		
		newExpireTime		= datetime.strptime(newExpireTime,'%Y-%m-%d').date()

		
		
		
		sql = """
				SELECT
					campaignid,status,expire_time
				FROM
					inventory_campaigns AS c
				WHERE
					c.campaignid = {campaignid}""".format(campaignid=campaigns.campaignid)
		cursor.execute(sql,)
		fieldNames = [item[0] for item in cursor.description]
		rows 		= cursor.fetchall()
		if rows:
			for row in rows:
				singleCampaignResult = {}
				for ind, value in enumerate(row):
					singleCampaignResult[fieldNames[ind]] = value
				
				print(singleCampaignResult['expire_time'])
				if(campaigns.status == 2):
					if (newExpireTime > singleCampaignResult['expire_time'] and newExpireTime >= oNowDate):
						return 1
					else:
						return campaigns.status
				else:
					return campaigns.status
		else:	
			return campaigns.status


def checkCampaignDailyLimitStatus(campaigns,newTargetImpr):
	with connection.cursor() as (cursor):
		now 			= datetime.now();
		oNowDateString 	= now.strftime('%Y-%m-%d');
		oNowDate		= datetime.strptime(oNowDateString,'%Y-%m-%d').date()
		sql = """
				SELECT
					SUM(s.impressions) AS impressions,
					SUM(s.clicks) AS clicks,
					SUM(s.requests) AS requests
				FROM
					inventory_banners AS b,
					inventory_rv_data_summary_ad_hourly AS s
				WHERE
					b.bannerid = s.creative_id
					AND b.campaignid ="""+ str(campaigns.campaignid)+"""
					AND DATE(s.date_time)    = '"""+str(oNowDate)+"""' ::date"""

				
		cursor.execute(sql,)
		fieldNames = [item[0] for item in cursor.description]
		rows 		= cursor.fetchall()
		if rows:
			for row in rows:
				singleCampaignResult = {}
				for ind, value in enumerate(row):
					singleCampaignResult[fieldNames[ind]] = value
				
				print(singleCampaignResult['impressions'])
				if(campaigns.status == 4):
					if (newTargetImpr > singleCampaignResult['impressions']):
						return 1
					else:
						return campaigns.status
				else:
					return campaigns.status
		else:	
			return campaigns.status


def checkCampaignTotalLimitStatus(campaigns,newViews):
	print('ss')
	
	with connection.cursor() as (cursor):
		sql = """
				SELECT
					SUM(s.impressions) AS impressions,
					SUM(s.clicks) AS clicks,
					SUM(s.requests) AS requests
				FROM
					inventory_banners AS b,
					inventory_rv_data_summary_ad_hourly AS s
				WHERE
					b.bannerid = s.creative_id
					AND b.campaignid ="""+ str(campaigns.campaignid)
				
		cursor.execute(sql,)
		fieldNames = [item[0] for item in cursor.description]
		rows 		= cursor.fetchall()
		if rows:
			for row in rows:
				singleCampaignResult = {}
				for ind, value in enumerate(row):
					singleCampaignResult[fieldNames[ind]] = value
				
				print(singleCampaignResult['impressions'])
				if(campaigns.status == 3):
					if (newViews > singleCampaignResult['impressions']):
						return 1
					else:
						return campaigns.status
				else:
					return campaigns.status
		else:	
			return campaigns.status



def getLinkedAdvertrisers(zoneType,width,height):
	with connection.cursor() as (cursor):
		sql 				="SELECT DISTINCT inventory_clients.clientid, inventory_clients.clientname FROM inventory_clients JOIN inventory_campaigns ON inventory_campaigns.clientid=inventory_clients.clientid JOIN inventory_banners ON inventory_banners.campaignid=inventory_campaigns.campaignid WHERE inventory_banners.storagetype = 'web'" 
		if zoneType != 'html':
			sql +="AND inventory_banners.width = '"+str(width)+"' AND inventory_banners.height = '"+str(height)+"'"
	
		print(sql)
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
				
		return result
				
				
def getLinkedCampaigns(clientid,zoneType,width,height):
	with connection.cursor() as (cursor):
		sql 				="SELECT DISTINCT inventory_campaigns.campaignid, inventory_campaigns.campaignname FROM inventory_campaigns JOIN inventory_banners ON inventory_banners.campaignid=inventory_campaigns.campaignid WHERE inventory_campaigns.clientid = '"+str(clientid)+"'"
		if zoneType != 'html':
			sql +="AND inventory_banners.width = '"+str(width)+"' AND inventory_banners.height = '"+str(height)+"'"
	
	
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
				
		return result


def getLinkedBanners(clientid,campaginid,zoneType, width,height):
	with connection.cursor() as (cursor):
		sql 				="SELECT inventory_banners.bannerid,inventory_banners.description FROM inventory_banners WHERE inventory_banners.campaignid = '"+str(campaginid)+"' AND inventory_banners.storagetype = '"+zoneType+"'"
		if zoneType != 'html':
			sql +="AND inventory_banners.width = '"+str(width)+"' AND inventory_banners.height = '"+str(height)+"'"
		
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
				
		return result
def updateAdZoneAssoc(bannerid,zoneid):
	try:
		adZoneAssoc  = rv_ad_zone_assoc.objects.get(zone_id=zoneid,ad_id=bannerid)
	except rv_ad_zone_assoc.DoesNotExist:
		data		= {"zone_id":zoneid, "ad_id":bannerid}
		serializer  = rv_ad_zone_assocSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
		return True

		



def getLinkedBannersByZones(zoneid):
	with connection.cursor() as (cursor):
		sql = "SELECT ad_zone_assoc_id, zone_id, ad_id, bannerid, storagetype, campaignid,width,height,filename, description FROM inventory_rv_ad_zone_assoc JOIN inventory_banners ON inventory_banners.bannerid = inventory_rv_ad_zone_assoc.ad_id WHERE inventory_rv_ad_zone_assoc.zone_id = '"+zoneid+"'"
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData = cursor.fetchall()
		result = []
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				result.append(objDict)
		return result
	


# function generateVideoZoneInvocationCode($zoneid=null,$campaignid =null, $bannerid =null,$clickTag=null, $thirdPartyServer=null){
		# $ssrc	 = $GLOBALS['deliveryCorePath'].preroll.php;


		# $src	 = str_replace('https','http',$ssrc);
		# $buffer	 = '';
        # $buffer .= <script type='text/javascript'><!--//<![CDATA[\n;
        # $buffer .=   var url=window.location.host; var m3_u = (location.protocol=='https:'?'.$ssrc.?domain='+url:'.$src.?domain='+url);\n;
		# $buffer .=   var m3_r = Math.floor(Math.random()*99999999999);\n;

		# if(!is_null($thirdPartyServer)){
			# if($thirdPartyServer == 'doubleclick'){
				# //$buffer .=    m3_r  = '%%CACHEBUSTER%%'\n;
			# }
		# }
        
        # $buffer .=    if (!document.MAX_used) document.MAX_used = ',';\n;
        # $buffer .=    document.write (\<scr\+\ipt type='text/javascript' src='\+m3_u);\n;
		# $buffer .=    document.write (\&zoneid=.$zoneid.\);\n;
		
		# if(!is_null($thirdPartyServer)){
			# if($thirdPartyServer == 'revive'){
				# $buffer .=    document.write ('&amp;clickTag=.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;cb=' + m3_r);\n;

			# }elseif($thirdPartyServer == 'newdoubleclick'){
				# $buffer .=    document.write ('&amp;click=%%VIEW_URL_UNESC%%.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;ord=' + m3_r);\n;
				
			# }elseif($thirdPartyServer == 'doubleclick'){
				
				# $buffer .=    document.write ('&click=%%CLICK_URL_UNESC%%.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;ord=' + m3_r);\n;
				 
			# }elseif($thirdPartyServer == 'zedo'){
				# $buffer .=    document.write ('&amp;l=.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;z=' + m3_r);\n;


				
			# }elseif($thirdPartyServer == 'adtech'){
				# $buffer .=    document.write ('&amp;rdclick=.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;misc=' + m3_r);\n;


				
			# }else{
				# $buffer .=    document.write ('&amp;clickTag=.$clickTag.');\n;
				# $buffer .=    document.write ('&amp;cb=' + m3_r);\n;
			# }
		# }
		
		
		# $buffer .=  document.write (\&amp;loc=\ + escape(window.location));\n;
		# $buffer .=  document.write ('&cb=' + m3_r);\n;

		# $buffer .=    document.write (\'><\\/scr\+\ipt>\);\n;
        # $buffer .= //]]>--></script>;
		# $buffer .= <noscript><a href='.$GLOBALS['deliveryCorePath'].' target='_blank'><img src='.$GLOBALS['deliveryCorePath'].setdefaultimage?bannerid=.$bannerid.' border='0' alt=''/></a></noscript>\n;
        # return $buffer;
		
	# }
def generateVastTag(zoneId, thirdPartyServer, clickTag):
	return True
	
	
	
def generateHtml5ZoneInvocationCode(zoneId,thirdPartyServer,clickTag):
	ssrc	 = deliveryCorePath+"rendercreativead.py"
	src	 	 = ssrc.replace('https','http')
	
	buffer	 = ''
	buffer += "<script type='text/javascript'><!--//<![CDATA[\n"
	buffer +="   var url=window.location.host; var m3_u = (location.protocol=='https:'?'"+ssrc+"?domain='+url:'"+src+"?domain='+url);\n"
	buffer +="   var m3_r = Math.floor(Math.random()*99999999999);\n"
	if not (thirdPartyServer is None):
		if(thirdPartyServer == 'doubleclick'):
			buffer +="    m3_r  = '%%CACHEBUSTER%%'\n"
			
	buffer +="    var url=window.location.host;\n"
	buffer +="    if (!document.MAX_used) document.MAX_used = ',';\n"
	buffer +="    document.write (\"<scr\"+\"ipt type='text/javascript' src='\"+m3_u);\n"
	
	buffer +="    document.write (\"&zoneid="+zoneId+"\");\n"

	
	if(thirdPartyServer == 'doubleclick'):
		buffer +="    document.write (\"&click=%%CLICK_URL_UNESC%%"+clickTag+"\");\n"
		buffer +="    document.write ('&ord=' + m3_r);\n"
	else:
		buffer +="    document.write ('&cb=' + m3_r);\n"
		
		
	buffer +="    document.write ('&url=' + url);\n"
	buffer +="    document.write (\"&loc=\" + escape(window.location));\n"
	buffer +="    document.write (\"'><\\/scr\"+\"ipt>\");\n"
	buffer +=" //]]>--></script>"

	buffer +=" <noscript><a href='"+deliveryCorePath+"' target=_blank'><img src='"+deliveryCorePath+"setdefaultimage?zoneid="+str(zoneId)+ "' border='0' alt=''/></a></noscript>\n"
	return buffer
	
	
def generateWebZoneInvocationCode(zoneId,thirdPartyServer,clickTag):
	ssrc	 = deliveryCorePath+"renderad.py"
	src	 	 = ssrc.replace('https','http')
	
	buffer	 = ''
	buffer +=" <script type='text/javascript'><!--//<![CDATA[\n"
	buffer +="   var url=window.location.host; var m3_u = (location.protocol=='https:'?'"+ssrc+"?domain='+url:'"+src+"?domain='+url);\n"
	buffer +="   var m3_r = Math.floor(Math.random()*99999999999);\n"
	
	if not (thirdPartyServer is None):
		if(thirdPartyServer == 'doubleclick'):
			buffer +="    m3_r  = '%%CACHEBUSTER%%'\n"
			
	buffer +="    var url=window.location.host;\n"
	buffer +="    if (!document.MAX_used) document.MAX_used = ',';\n"
	buffer +="    document.write (\"<scr\"+\"ipt type='text/javascript' src='\"+m3_u);\n"
	
	buffer +="    document.write (\"&zoneid="+zoneId+"\");\n"
	#buffer .= "   document.write (\"&amp;zoneid=".$zoneId."\");\n";

	
	if(thirdPartyServer == 'doubleclick'):
		buffer +="    document.write (\"&click=%%CLICK_URL_UNESC%%"+clickTag+"\");\n"
		buffer +="    document.write ('&ord=' + m3_r);\n"
	else:
		buffer +="    document.write ('&cb=' + m3_r);\n"
		
		
	buffer +="    document.write ('&url=' + url);\n"
	buffer +="    document.write (\"&loc=\" + escape(window.location));\n"
	buffer +="    document.write (\"'><\\/scr\"+\"ipt>\");\n"
	buffer +=" //]]>--></script>"

	buffer +=" <noscript><a href='"+deliveryCorePath+"' target=_blank'><img src='"+deliveryCorePath+"setdefaultimage?zoneid="+str(zoneId)+ "' border='0' alt=''/></a></noscript>\n"
	
	
	return buffer
	
def getlinkedZone(zoneId):
	with connection.cursor() as (cursor):
		sql = """
			SELECT 
				ad_id
				
			FROM
				inventory_rv_ad_zone_assoc AS r
			WHERE 
				r.zone_id ={zoneid}""".format(zoneid=zoneId)
				
		cursor.execute(sql)
		field_names = [item[0] for item in cursor.description]
		rawData 	= cursor.fetchall()
		if rawData:
			for row in rawData:
				objDict = {}
				for index, value in enumerate(row):
					objDict[field_names[index]] = value
				return objDict
		else:
			return {}
		



	
	
	
	
	
	
	
	
	
	
	