from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from rest_framework.parsers import JSONParser
from inventory.models import Clients
from inventory.serializers import ClientsSerializer
from inventory.models import Campaigns,rv_data_summary_ad_hourly
from inventory.serializers import CampaignsSerializer
from inventory.models import Banners
from inventory.serializers import BannersSerializer
from inventory.models import Zones
from inventory.serializers import ZonesSerializer
from inventory.models import Affiliates
from inventory.models import Client_access
from inventory.models import Publisher_access
from inventory.serializers import AffiliatesSerializer,User_assocSerializer
from inventory.models import Users,LoginToken,banner_vast_element,rv_ad_zone_assoc
from inventory.serializers import UsersSerializer,UsersCustomizeSerializer,LoginTokenSerializer,BannervastSerializer,Client_accessSerializer,rv_ad_zone_assocSerializer
from inventory.pubexecutive_serializers import Publisher_accessSerializer
from inventory.executive_serializers import Client_accessSerializer
from inventory.helpers import MAX_displayAcls,getLimitationComponent

import json
import os
import sys
import secrets
import base64
import hashlib 
from datetime import datetime,timedelta
from itertools import chain
from random import randint
from django.core.mail import send_mail
from django.conf import settings


from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from django.core.files.storage import FileSystemStorage
from django.db import connection

from inventory.helpers import generateWebZoneInvocationCode,generateHtml5ZoneInvocationCode,getLinkedAdvertrisers,checkCampaignTotalLimitStatus,checkCampaignDailyLimitStatus,checkCampaignExpireStatus
from inventory.helpers import getLinkedAdvertrisers,getLinkedCampaigns,getLinkedBanners,updateAdZoneAssoc,getAssocOrderDetails,getLinkedBannersByZones
from inventory.helpers import updateDeliveryAd,getlinkedZone,updateCampaignCacheData
from inventory.html5creative import html5CreativeUpdate



deliveryCachePath		= '../public_html/django2adserver/cgi-bin/delivery/cache/'
deliveryUrl				= 'https://api.onetracky.com/cgi-bin/delivery/'

def getComponents(request):
    bannerid				= request.GET.get('bannerid')
    campaignid				= request.GET.get('campaignid')
    clientid				= request.GET.get('clientid')
    bannerData				= Banners.objects.get(bannerid=bannerid)
    componentName 			= JSONParser().parse(request)
    token 					= componentName['token']
    response				= {}
    #acls                    = ''

    

    if request.method == 'POST':
        if(token == 'save component'):
            acls 				= componentName['acl']
            aclPlugins			= ''
            compiledLimitPrefix	= 'Max_check'
            loopCount			= 0
            compiledLimit		= ''
            
            for acl in acls:
                if(acl['data']):
                    if(loopCount >= 1):
                        compiledLimit		= compiledLimit+' '+acl['logical']+' '
                    
                    pluginsName		= acl['type'];
                    pluginsNameArr	= pluginsName.split(':')
                    compiledLimit 	= compiledLimit+'Max_check'+pluginsNameArr[1]+'_'+pluginsNameArr[2]	
                    aclPlugins		+= pluginsName+','
                
                    
                        
                    if(acl['type'] == 'deliveryLimitations:Mobile:ISP' or  acl['type'] == 'deliveryLimitations:Client:Domain' or acl['type']=='deliveryLimitations:Client:IP' or acl['type']=='deliveryLimitations:Time:Date'):
                        if(acl['type']=='deliveryLimitations:Time:Date'):
                            
                            dateformat	 	= acl['data']['date']
                            dateformatArr	= dateformat.split('-')
                            timestamp		= dateformatArr[2]+dateformatArr[1]+dateformatArr[0]
                            limitVariables	= timestamp
                            
                        else:
                            limitVariables	 = acl['data']
                        
                        
                    else:
                        if(len(acl['data']) > 1):
                            limitVariables	 = ",".join(acl['data'])
                        else:
                            limitVariables	 = acl['data'][0]
                    
                    compiledLimit 	 = compiledLimit+"('"+limitVariables+"','"+acl['comparison']+"')"
                    #compiledLimit 	 = compiledLimit+"("+limitVariables+","+acl['comparison']+")"

                    loopCount = loopCount+1
            if(loopCount==0):
                compiledLimit	= ''
                
            aclPlugins						= aclPlugins[0:len(aclPlugins)-1]
            #aclPlugins						= addslashes(aclPlugins)
            #compiledLimit					= compiledLimit.replace("'","''")
            
            
            bannerData.acl_plugins				= aclPlugins
            bannerData.compiledlimitation		= compiledLimit
            now 								= datetime.now()
            dateTime							= now.strftime('%Y-%m-%d %H:%M:%S')
            
            
            

            
            
            bannerData.acls_updated				= dateTime
            bannerData.save();
            
            assocData		= Banners.objects.get(pk=bannerid)
            serializer 		= BannersSerializer(assocData)
            jsonArr2		= serializer.data
            
            bannerCampaginCacheData							= getAssocOrderDetails(bannerid)
            
            
            #print(bannerCampaginCacheData)
            
            
            if(assocData):
                filename		= deliveryCachePath+''+str(bannerid)+'.py'
                f				= open(filename,"w+")
                jsonArr 		= bannerCampaginCacheData
                jsonString 		= json.dumps(jsonArr, indent=4, sort_keys=True, default=str)
                f.write(jsonString)
                f.close()
        
        elif(token == 'new component'):
        
            acls						= {}
            limitationDetails			= Banners.objects.get(pk=bannerid)
            
            if(len(limitationDetails.acl_plugins)):
                acl_plugins 				= limitationDetails.compiledlimitation.split('and')
                pluginData				    = limitationDetails.acl_plugins.split(',')
                
                key 			= 0
                for acl_plugin in acl_plugins:
                    if(limitationDetails.compiledlimitation):
                        limitations 		= acl_plugins[key]
                        start				= limitations.find('(')+2
                        end					= limitations.find(')')-6
                        length				= end - start
                        strlen				= len(limitations)
                        compStart			= strlen-4
                                    
                        limitValue			= limitations[start:length]
                        comp				= limitations[compStart:2]
                        acl			= {
                            "ad_id"				: bannerid,
                            "comparison" 		: comp,
                            "data" 				: limitValue,
                            "executionorder" 	: key,
                            "logical" 			: 'and',
                            "type" 				: pluginData[key]
                        }
                        
                    
                        if(pluginData[key] == 'deliveryLimitations:Geo:City'):
                            cCode 					= limitValue.split(',')
                            acl['state']			= cCode[1]
                            
                        
                        limitValueArr		= limitValue.split(',')
                        
                    key	= key +1
                    acls[key]	= acl
            
            
                        

            if (len(acls) == 0) :
                acls[0]								= {
                    "comparison" : '',
                    "data" : 		'',
                    "executionorder" : 0,
                    "logical" : '',
                    "type" : componentName['type']
                }
                if(componentName['type'] == 'deliveryLimitations:Geo:City'):
                    if(componentName['country']):
                        acls[0]['data']	= componentName['country']
                    if componentName['state']:
                        acls[0]['state']	= componentName['state']
                if(componentName['type'] == 'deliveryLimitations:Geo:Region'):
                    if(componentName['country']):
                        acls[0]['data']	= componentName['country']
                        
            else:
                typeCount		= len(acls)
                acls[typeCount]	= {
                    "comparison" : '',
                    "data" :'',
                    "executionorder" : typeCount,
                    "logical" : '',
                    "type" : componentName['type']
                }
                
                if(componentName['type'] == 'deliveryLimitations:Geo:City'):
                    if(componentName['country']):
                        acls[key]['data']	= componentName['country']
                    if componentName['state']:
                        acls[key]['state']	= componentName['state']
                if(componentName['type'] == 'deliveryLimitations:Geo:Region'):
                    if(componentName['country']):
                        acls[key]['data']	= componentName['country']
                        
                    
                    
                
    elif request.method == 'DELETE':
        bannerData.acl_plugins	= ''
        bannerData.compiledlimitation=''
        bannerData.save()
        assocData		= Banners.objects.get(pk=bannerid)
        serializer 		= BannersSerializer(assocData)
        jsonArr2		= serializer.data

        if(assocData):
            #print(deliveryCachePath)
            filename		= deliveryCachePath+''+str(bannerid)+'.py'
            f				= open(filename,"w+")
            jsonArr 		= jsonArr2
            jsonString 		= json.dumps(jsonArr)
            f.write(jsonString)
            f.close()
        
        
        acls	= {}
    ############ finally check all limitation and retrun
    
    if (token == 'save component') or (token == 'delete component') or 	(token == 'get component'):
        acls						= {}
        limitationDetails			= Banners.objects.get(pk=bannerid)
        if(len(limitationDetails.acl_plugins)):
            acl_plugins 				= limitationDetails.compiledlimitation.split('and')
            pluginData				    = limitationDetails.acl_plugins.split(',')
            
            key 			= 0
            for acl_plugin in acl_plugins:
                #print(limitationDetails.compiledlimitation)
                if(limitationDetails.compiledlimitation):
                    limitations 		= acl_plugins[key]
                    limitations			= limitations.strip()
                    start				= limitations.find('(')+2
                    end					= limitations.find(')')-6
                    length				= end - start
                    strlen				= len(limitations)
                    compStart			= strlen-4
                                
                    limitValue			= limitations[start:end]
                    comp				= limitations[compStart:compStart+2]
                    
                    acl			= {
                        "ad_id"				: bannerid,
                        "comparison" 		: comp,
                        "data" 				: limitValue,
                        "executionorder" 	: key,
                        "logical" 			: 'and',
                        "type" 				: pluginData[key]
                    }
                    
                
                    if(pluginData[key] == 'deliveryLimitations:Geo:City'):
                        cCode 					= limitValue.split(',')
                        acl['state']			= cCode[1]
                        
                    
                    limitValueArr		= limitValue.split(',')
                
                acls[key]	= acl
                key	= key +1
            response.update({"acls":acls})


    
    
    # print(acls[0]['type'])
    # print(acls)

    #print('hellllo')
    components		= getLimitationComponent()
    aParams			= {'clientid':clientid,'campaignid':campaignid,'bannerid':bannerid}
    input			= MAX_displayAcls(acls, aParams)
    response.update({"plugins":components})
    response.update({"input":input})
    



    responseObject 	= {"message":"Delivery Limitation Components","data":response,'status':True}
    #responseObject = {"message":"Delivery Limitation Components","data":"sss",'status':True}

    return JsonResponse(responseObject, safe=False, status=200)



def videoBannChk(clientId,cmapaignId='',bannerId=''):
    if clientId:
        clientIdString 		    = str(clientId)
        #print(bannerId)
        bannerWhere	= ''
        campaignWhere= ''
        bannerId = str(bannerId)
        cmapaignId = str(cmapaignId)
        if(bannerId):
            #print('hshdasjh')
            bannerWhere 				= ' b.bannerid ='+bannerId+' AND '
            #print(cmapaignId)
        elif(cmapaignId):
            campaignWhere 				=  ' m.campaignid ='+cmapaignId+' AND ' 
        with connection.cursor() as cursor:
            sql = "SELECT m.campaignname, b.storagetype, m.clientid FROM inventory_campaigns AS m JOIN inventory_banners AS b ON b.campaignid = m.campaignid WHERE m.clientid = " +clientIdString+" AND " +campaignWhere+"" +bannerWhere+ " b.storagetype='html'"
            #print(sql)
            cursor.execute(sql)
            field_names = [item[0] for item in cursor.description]
            rawData = cursor.fetchall()
            if rawData:
                if not bannerId:
                    rawData 	= {'checkVideoAdvtStatus':'true','expansionType': 'Ad','clientid':clientId,'campaignid':cmapaignId,'bannerid':bannerId}
                    
                elif(cmapaignId):
                    rawData 	= {'checkVideoAdvtStatus':'true','expansionType': 'Campaign','clientid':clientId,'campaignid':cmapaignId}
                else:
                    if not clientId:
                        rawData 	= {'checkVideoAdvtStatus':'true','expansionType': 'Advertiser','clientid':clientId}
            else:
                rawData 	= {'checkVideoAdvtStatus':'false'}
            return rawData
    else:
        rawData 	= {'checkVideoAdvtStatus':'false'}
        return rawData



def zonesInclude(request):
    zoneType 		= ''
    width 			= 0
    height 			= 0
    zoneid			=request.GET.get('zoneid')
    if zoneid:
        affiliateid			= request.GET.get('affiliateid')
        zoneData			= Zones.objects.get(zoneid=zoneid)
        #print(zoneData)
        if zoneData:
            zoneType = zoneData.delivery
            width	= zoneData.width
            height	= zoneData.height
            
            advertiser 		   = getLinkedAdvertrisers(zoneType,width,height)
            print(advertiser)
            responseObject		= {"advtdata":advertiser}

                
            
            if request.GET.get('clientid'):
                clientid					= request.GET.get('clientid')
                campaigns					= getLinkedCampaigns(clientid,zoneType,width,height)
                
                responseObject.update({"cmpdata":campaigns})

                #print(campaigns)
                if request.GET.get('campaignid'):
                    campaginid				= request.GET.get('campaignid')
                    banners					= getLinkedBanners(clientid,campaginid,zoneType, width,height)
                    #print(banners)
                
                    responseObject.update({"bannerdata":banners})
                

                    if request.GET.get('bannerid'):
                        bannerid 				= request.GET.get('bannerid')
                        msg			        	= updateAdZoneAssoc(bannerid,zoneid)
                        bannerData1             = getAssocOrderDetails(bannerid)
                        bannerData				= bannerData1[0] 
                        print(bannerData.get('bannerid'))
                        #"activate_time":bannerData.get('activate_time'),
                        #"expire_time":bannerData.get('expire_time'),
                        assocData		= {
                            'ad_id' : bannerData.get('bannerid'),
                            "banner_status":bannerData.get('banner_status'),
                            "campaign_status":bannerData.get('campaign_status'),
                            
                            'width' : zoneData.width,
                            'height' :  zoneData.height,
                            'type' : zoneData.delivery,
                            'contenttype' : bannerData.get('contenttype'),
                            'weight' : bannerData.get('banner_weight'),
                            'block_ad' : '0',
                            'cap_ad' : '0',
                            'session_cap_ad' : '0',
                            'compiledlimitation' : '',
                            #'acl_plugins' : NULL,
                            'alt_filename' : '',
                            'priority' : '0',
                            'priority_factor' : '1',
                            'to_be_delivered' : '1',
                            'campaign_id' : bannerData.get('campaignid'),
                            'campaign_priority' : bannerData.get('campaign_priority'),
                            'campaign_weight' : bannerData.get('campaign_weight'),
                            'campaign_companion' : '0',
                            'block_campaign' : '0',
                            'cap_campaign' : '0',
                            'session_cap_campaign' : '0',
                            'show_capped_no_cookie' : '0',
                            'client_id' : bannerData.get('clientid'),
                        }
                        #print(assocData)
                        bannerCache 	= 'delivery_ad_zone_' + str(zoneid) + '.py'
                        print(bannerCache)
                        f 				= open(deliveryCachePath + bannerCache, 'w+')

                        jsonArr 		= assocData
                        jsonString 		= json.dumps(jsonArr)
                        f.write(jsonString)
                        f.close()
                
                    

    linkedBanner		= getLinkedBannersByZones(zoneid)
    responseObject.update({"linkedBanner":linkedBanner})

    responseObject12 	= {"message":"Linking Banner","data":responseObject,'status':True}
    return JsonResponse(responseObject12, safe=False, status=200,)

def getuserIDByToken(loginToken):
    try:
        tokens 			= LoginToken.objects.get(token=loginToken)
        if tokens:
            users 	= Users.objects.get(user_id=tokens.user_id)
            if users:
                return tokens.user_id
            else :
                return tokens.user_id
        
    except LoginToken.DoesNotExist:
        return False


    
        



def getDate(period_preset,request=None):
    if period_preset:
        if period_preset=='today':
            oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
            oEndDate	=	datetime.today().strftime('%Y-%m-%d')
            responseObject		= {"period_start":oStartDate,"period_end":oEndDate}
            return responseObject
        elif period_preset=='yesterday':
            oStartDate	= 	datetime.strftime(datetime.today() - timedelta(1), '%Y-%m-%d')
            oEndDate	=	datetime.strftime(datetime.today() - timedelta(1), '%Y-%m-%d')
            responseObject		= {"period_start":oStartDate,"period_end":oEndDate}
            return responseObject
        elif period_preset=='this_month':
            stdate	= 	datetime.today().strftime('%Y-%m-%d')
            date = datetime.today().strptime(stdate, "%Y-%m-%d")
            oStartDate	= 	str(date.year)+"-"+str(date.month)+"-01"
            oEndDate	=	datetime.today().strftime('%Y-%m-%d')	
            responseObject		= {"period_start":oStartDate,"period_end":oEndDate}
            return responseObject
        elif period_preset=='specific':
            oStartDate	= request.GET.get('period_start')
            oEndDate	= request.GET.get('period_end')
            responseObject		= {"period_start":oStartDate,"period_end":oEndDate}
            return responseObject	
        elif period_preset=='all_stats':
            oStartDate	= None
            oEndDate	= None
            responseObject		= {"period_start":oStartDate,"period_end":oEndDate}
            return responseObject




def zonesInvocationVast(request):
    zoneId = request.GET.get('zoneid')
    if zoneId:
        affiliateId = request.GET.get('affiliateid')
        zoneData 	= Zones.objects.get(zoneid=zoneId)
        print(zoneData.delivery)
        if zoneData:
            zoneType = zoneData.delivery
            if 'thirdpartytrack' in request.POST:
                thirdPartyServer = request.POST.post('thirdpartytrack')
            else:
                thirdPartyServer = None
            
            
            if zoneType == 'html':
                varString 			= hashlib.md5(str(randint(100, 999)).encode())
                var					= varString.hexdigest()
                var					= var[0:8]
                zoneInvocation		= deliveryUrl+'core/rendervast.py?zoneid='+zoneId+'&cb='+var+'&vast=3'

        invocationCode 	= zoneInvocation
        data       		= {'code': invocationCode,'zoneid':zoneId,'affiliateid':affiliateId,'zonetype':zoneType,'thirdpartytrack':''}
        responseObject = {'message':'Invocation Code','data':data,  'status':True}
        return JsonResponse(responseObject,safe=False)
    else:
        data 			= {'code': 'zone doesnot exist'}
        responseObject = {'message':'Invocation Code','data':data,  'status':False}
        return JsonResponse(responseObject, safe=False, status=204)


def zonesInvocation(request):
    if request.method == 'POST':
        data12 = JSONParser().parse(request)
        thirdPartyServer = data12['thirdpartytrack']
    else:
        thirdPartyServer = None

    zoneId = request.GET.get('zoneid')
    if zoneId:
        affiliateId = request.GET.get('affiliateid')
        zoneData 	= Zones.objects.get(zoneid=zoneId)
        AdId = 7
        if zoneData:
            
            zoneType = zoneData.delivery
            
            linkedZoneData     = getlinkedZone(zoneId)
            print(linkedZoneData)
           
            if(linkedZoneData):
                AdId		= linkedZoneData	.get('ad_id') 
            else:
                AdId       = 0
            
            clickTag 			= deliveryUrl+'core/ckvast.py?zoneid=' + str(zoneId) + '&bannerid=' + str(AdId)

                
            if zoneType == 'html':
                zoneInvocation = 'it is will generate vast tag'
            elif zoneType == 'html5':
                zoneInvocation = generateHtml5ZoneInvocationCode(zoneId, thirdPartyServer, clickTag)
            else:
                zoneInvocation = generateWebZoneInvocationCode(zoneId, thirdPartyServer, clickTag)
                
        invocationCode 	= zoneInvocation
        data       		= {'code': invocationCode,'zoneid':zoneId,'affiliateid':affiliateId,'zonetype':zoneType,'thirdpartytrack':thirdPartyServer}
        responseObject = {'message':'Invocation Code','data':data,  'status':True}
        return JsonResponse(responseObject,safe=False)
    else:
        data 			= {'code': 'zone doesnot exist'}
        responseObject = {'message':'Invocation Code','data':data,  'status':False}
        return JsonResponse(responseObject, safe=False, status=204)
        



def ebannerDailyStats(request,bannerid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        banneridStr 	= 'b.bannerid = '+str(bannerid)+' AND'
        with connection.cursor() as cursor:
            sql 			= "SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue,DATE(s.date_time) AS day FROM inventory_banners AS b, inventory_rv_data_summary_ad_hourly AS s WHERE "+banneridStr+" b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day"
            cursor.execute(sql)
            field_names 	= [item[0] for item in cursor.description]
            rawData 		= cursor.fetchall()
            
            result = []
            if rawData:
                for row in rawData:
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                        VideoChkRes        = videoBannChk(bannerid)
                        VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                    result.append(objDict)
                
            
        if result:
            finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
            responseObject 		= {'message': 'Banners List', 'data': finalData, 'status':True}
            return JsonResponse(responseObject, safe=False,status=200)
        else:
            responseObject 		= {'message': 'Banners List', 'data': {}, 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)

    
def ebannerStats(request,campaignid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidStr 	= 'b.campaignid = '+str(campaignid)+' AND'
        with connection.cursor() as cursor:
            sql 			= "SELECT b.bannerid AS bannerID, b.description AS bannerName, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue FROM inventory_banners AS b, inventory_rv_data_summary_ad_hourly AS s WHERE "+campaignidStr+" b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY b.bannerid "
            cursor.execute(sql)
            field_names 	= [item[0] for item in cursor.description]
            rawData 		= cursor.fetchall()
            
            result = []
            if rawData:
                for row in rawData:
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                    result.append(objDict)
                
            
        if result:
            responseObject 		= {'message': 'Banners List', 'data': result, 'status':True}
            return JsonResponse(responseObject, safe=False,status=200)
        else:
            responseObject 		= {'message': 'Banners List', 'data': {}, 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)

    
def ecampaignsDailyStats(request,campaignid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidStr 	= 'm.campaignid = '+str(campaignid)+' AND'
        with connection.cursor() as cursor:
            sql 			= "SELECT SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue, DATE(s.date_time) AS day FROM inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE  "+campaignidStr+" m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day"
            print(sql)
            cursor.execute(sql)
            field_names 	= [item[0] for item in cursor.description]
            rawData 		= cursor.fetchall()
            
            result = []
            if rawData:
                for row in rawData:
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                        VideoChkRes        = videoBannChk(campaignid)
                        VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                    result.append(objDict)
                
            
        if result:
            finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
            responseObject 		= {'message': 'Campaign List', 'data': finalData, 'status':True}
            return JsonResponse(responseObject, safe=False,status=200)
        else:
            responseObject 		= {'message': 'Campaign List', 'data': {}, 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)

        
def ecampaignsStats(request,clientid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidStr 	= 'c.clientid = '+str(clientid)+' AND'
        with connection.cursor() as cursor:
        
            sql 			= "SELECT m.campaignid,m.campaignname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE  "+clientidStr+" c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY m.campaignid,m.campaignname"
                    
            cursor.execute(sql)
            field_names 	= [item[0] for item in cursor.description]
            rawData 		= cursor.fetchall()
            
            result = []
            if rawData:
                for row in rawData:
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                    result.append(objDict)
                
            
        if result:
            responseObject 		= {'message': 'Campaign List', 'data': result, 'status':True}
            return JsonResponse(responseObject, safe=False,status=200)
        else:
            responseObject 		= {'message': 'Campaign List', 'data': {}, 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)


def advertiserStats(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        with connection.cursor() as cursor:
            sql = "SELECT c.clientid,clientname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id "+getWhereDate(oStartDate, oEndDate)+" GROUP BY c.clientid"
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
                responseObject = {'message': 'Advertisers Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def advertiserDailyStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
    clientidString 		= str(pk)
    whereStr = 'c.clientid = '+clientidString+' AND '
    with connection.cursor() as cursor:
        # add day in group by condition by sunil
        sql ="SELECT DATE(s.date_time) AS day,c.clientid,clientname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+"c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY c.clientid,day "
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
                    VideoChkRes        = videoBannChk(pk)
                    VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                
                result.append(objDict)
            #result.append({'checkVideoAdvtStatus' :VideoChk })
            finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
            responseObject = {'message': 'Advertiser Stats', 'data': finalData, 'status':True}
            return JsonResponse(responseObject, safe=False)	
        
        else:
            responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)
            
        # if clientStats:
        # 	data = {
        # 		"clientid":clientStats[0],
        # 		"clientname":clientStats[1],
        # 		"impressions":clientStats[2],
        # 		"clicks":clientStats[3],
        # 		"requests":clientStats[4],
        # 		"revenue":clientStats[5]
        # 	}
        # 	print("hi")ban
        # 	#print(data);
        # 	responseObject = {'message': 'Advertisers Stats', 'data': data, 'status':True}
        # 	return JsonResponse(responseObject, safe=False)
        # else:
        # 	responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
        # 	return JsonResponse(responseObject, safe=False)
        
def bannersStats(request,clientid,campaignid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidString 		= str(campaignid)
        whereStr 				= 'b.campaignid = '+campaignidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT b.bannerid,b.description,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE  "+whereStr+" b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY b.bannerid,b.description"
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
                
                #clients 	= Clients.objects.get(pk=pk)
                #print(clients)
                
                responseObject = {'message': 'Banners Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)


def bannersDailyStats(request,clientid,campaignid,bannerid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        #print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        # print(clientid)
        # print(campaignid)
        # print(bannerid)
        banneridString 		= str(bannerid)
        whereStr = 'b.bannerid = '+banneridString+' AND '
        with connection.cursor() as cursor:
            # add banner name in group by condition by sunil 
            sql = "SELECT b.description AS bannerName,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue,DATE(s.date_time) AS day FROM inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+" b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day,bannerName"
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
                    VideoChkRes        = videoBannChk(clientid,campaignid,bannerid)
                    VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                #objDict.update({'checkVideoAdvtStatus' :VideoChk })
                result.append(objDict)
                finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
                responseObject = {'message': 'Banners Stats', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
            


def campaignsStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidString 		= str(pk)
        whereStr 			= 'm.clientid = '+clientidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT m.campaignid,m.campaignname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE  "+whereStr+" m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY m.campaignid,m.campaignname"
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
                
                # clients 	= Clients.objects.get(pk=pk)
                # print(clients)
                
                responseObject = {'message': 'Campaigns Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
                    
def campaignsDailyStats(request,pk,id):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidString 		= str(id)
        whereStr = 'm.campaignid = '+campaignidString+' AND '
        with connection.cursor() as cursor:
            # add campaignname in group by condition by sunil
            sql = "SELECT m.campaignname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue,DATE(s.date_time) AS day FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+" c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id "+getWhereDate(oStartDate, oEndDate)+"  GROUP BY day,m.campaignname"
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
                    VideoChkRes        = videoBannChk(pk,id)
                    VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                #objDict.update({'checkVideoAdvtStatus' :VideoChk })
                result.append(objDict)
                finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
                responseObject = {'message': 'Campaigns Stats', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def websiteStats(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        with connection.cursor() as cursor:
            
            sql = "SELECT p.affiliateid,p.name, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue FROM inventory_zones AS z, inventory_affiliates AS p, inventory_rv_data_summary_ad_hourly AS s WHERE p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id "+getWhereDate(oStartDate, oEndDate)+" GROUP BY p.affiliateid"
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
                responseObject = {'message': 'Affiliates Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)	
        
def websiteDailyStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
    clientidString 		= str(pk)
    whereStr = ' p.affiliateid = '+clientidString+' AND '
    print(whereStr)
    with connection.cursor() as cursor:
        cursor.execute("SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue,date(s.date_time) AS day FROM inventory_zones AS z, inventory_affiliates AS p, inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+" p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day")
        field_names = [item[0] for item in cursor.description]

        rawData  = cursor.fetchall()
        result = []
        if rawData:
            for row in rawData:
                objDict = {}
                for index, value in enumerate(row):
                    objDict[field_names[index]] = value
                    VideoChkRes        = videoBannChk(pk)
                    VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                result.append(objDict)
            finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}
            responseObject = {'message': 'Website Stats', 'data': finalData, 'status':True}
            return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)

def zoneStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        affiliateidString 		= str(pk)
        whereStr 			= 'p.affiliateid = '+affiliateidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT z.zonename,z.zoneid, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue, z.zoneid AS zoneID, z.zonename AS zoneName FROM inventory_zones AS z,inventory_affiliates AS p, inventory_rv_data_summary_ad_hourly AS s WHERE " +whereStr+ " p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id " +getWhereDate(oStartDate, oEndDate)+ " GROUP BY z.zoneid, z.zonename"
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
                
                # clients 	= Clients.objects.get(pk=pk)
                # print(clients)
                
                responseObject = {'message': 'Zones Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def zoneDailyStats(request,pk,id):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        zoneidString 		= str(id)
        whereStr = ' s.zone_id = ' +zoneidString
        with connection.cursor() as cursor:
            sql = "SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue, DATE(s.date_time) AS day FROM inventory_rv_data_summary_ad_hourly AS s WHERE " +whereStr+ "  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day"
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
                        VideoChkRes        = videoBannChk(pk)
                        VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                    result.append(objDict)
                finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}    
                responseObject = {'message': 'Zones Stats', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)



def webcampaignsStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        affiliateidString 		= str(pk)
        whereStr 			= 'AND p.affiliateid = '+affiliateidString
        with connection.cursor() as cursor:
            sql = "SELECT SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue,SUM(s.conversions) AS conversions,m.campaignid AS campaignID, m.campaignname AS campaignName, c.clientid AS advertiserID, c.clientname AS advertiserName FROM inventory_zones AS z, inventory_affiliates AS p, inventory_clients AS c, inventory_campaigns AS m, inventory_banners AS b, inventory_rv_data_summary_ad_hourly AS s WHERE c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id AND p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id " +whereStr+ "  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY m.campaignid, m.campaignname, c.clientid, c.clientname"
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
                
                # clients 	= Clients.objects.get(pk=pk)
                # print(clients)
                
                responseObject = {'message': 'Campaign Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)



def webcampaignsDailyStats(request,pk,id):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        zoneidString 		= str(id)
        whereStr = 'AND p.affiliateid = ' +zoneidString
        with connection.cursor() as cursor:
            sql = "SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue, SUM(s.conversions) AS conversions, DATE(s.date_time) AS day FROM inventory_zones AS z, inventory_affiliates AS p, inventory_clients AS c, inventory_campaigns AS m, inventory_banners AS b, inventory_rv_data_summary_ad_hourly AS s WHERE  c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id AND p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id " +whereStr+ "  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day"
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
                        VideoChkRes        = videoBannChk(pk)
                        VideoChk           = VideoChkRes['checkVideoAdvtStatus']
                    result.append(objDict)
                finalData       = {'checkVideoAdvtStatus' :VideoChk, 'reportData':result}    
                responseObject = {'message': 'Campaign Stats', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
        




def getWhereDate(oStartDate, oEndDate, dateField = 's.date_time'):
    where = '';
    if (oStartDate and oStartDate):
        oStart = "'"+oStartDate+" 00:00:00 '"
        where += 'AND ' + dateField +' >= '+oStart
        


    if (oEndDate and oEndDate):
        oEnd = "'"+oEndDate+" 23:59:59 '"
        
        where += 'AND ' + dateField +' <= '+oEnd
        
    #print(where)
    return where;

def AgetWhereDate(oStartDate, oEndDate, dateField = 'interval_start'):
    where = '';
    if (oStartDate and oStartDate):
        oStart = "'"+oStartDate+" 00:00:00 '"
        where += 'AND ' + dateField +' >= '+oStart
        


    if (oEndDate and oEndDate):
        oEnd = "'"+oEndDate+" 23:59:59 '"
        
        where += ' AND ' + dateField +' <= '+oEnd
        
    #print(where)
    return where;
    



            

def getAdvtAllCampaigns(request,pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            if request.method == 'GET':
                campaigns = Campaigns.objects.filter(clientid=pk)
                serializer = CampaignsSerializer(campaigns, many=True)
                # print(serializer)
                responseObject = {'message': 'Campaigns Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def getCmpsAllBanners(request,pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            if request.method == 'GET':
                banners = Banners.objects.filter(campaignid=pk)
                serializer = BannersSerializer(banners, many=True)
                # print(serializer)
                responseObject = {'message': 'Banners Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def getAffltAllZones(request,pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            if request.method == 'GET':
                zones = Zones.objects.filter(affiliateid=pk)
                serializer = ZonesSerializer(zones, many=True)
                # print(serializer)
                responseObject = {'message': 'Zones Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)			











        
def logout(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            try:
                loginToken = LoginToken.objects.get(token=request.META['HTTP_AUTHORIZATION'])
            except Clients.DoesNotExist:
                return HttpResponse(status=204)
            
            
            loginToken.delete()
            responseObject = {'message': 'Successfully Logout', 'data': [], 'status':True}
            return JsonResponse(responseObject,status=200)
        
        else:
            responseObject = {'message': 'Invalid Token', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)		
    



def validateToken(loginToken):
    try:
        tokens 			= LoginToken.objects.get(token=loginToken)
        if tokens:
            users 	= Users.objects.get(user_id=tokens.user_id)
            if users:
                return True
            else :
                return False
        
    except LoginToken.DoesNotExist:
        return False

def tokenEmpCheck(loginToken):

    if loginToken:
        return True
    else :
        return False		
    
# def CustomAuthToken(request):
# 	if request.method == 'POST':
# 		data = JSONParser().parse(request)
# 		string 			 = data['password']
# 		role1            = data['role']
# 		roleCheck        = tokenEmpCheck(role1)
# 		if roleCheck:
# 			result 			= hashlib.md5(string.encode()) 
# 			passord			= result.hexdigest()
# 			#print(passord)
            
# 			try:
# 				users = Users.objects.filter(username=data['username'], password=passord)
# 				print(users.count())
# 				if users.count() == 1:
# 					print('------ single user ----->')
# 					user_id   = users[0].user_id
# 					username  = users[0].username
# 					email     = users[0].email
# 					firstname = users[0].firstname
# 					lastname  = users[0].lastname
# 					role      = users[0].role
# 					change_passwordStatus  = users[0].change_passwordStatus
                    
# 				else:
# 					print('------ multiple user ----->')
# 					if(users[0].role==role1):
# 						user_id   = users[0].user_id
# 						username  = users[0].username
# 						email     = users[0].email
# 						firstname = users[0].firstname
# 						lastname  = users[0].lastname
# 						role      = users[0].role
# 						change_passwordStatus  = users[0].change_passwordStatus
# 					else:
# 						user_id   = users[1].user_id
# 						username  = users[1].username
# 						email     = users[1].email
# 						firstname = users[1].firstname
# 						lastname  = users[1].lastname
# 						role      = users[1].role
# 						change_passwordStatus  = users[1].change_passwordStatus
                
# 				token 	= secrets.token_hex(20)
# 				tokenData 	= {'token':token,'user_id':user_id ,'username':username,'email':email,'firstname':firstname,'lastname':lastname,'role':role,'change_passwordStatus':change_passwordStatus}
# 				print(tokenData)
# 				serializer	 = LoginTokenSerializer(data=tokenData)
# 				if serializer.is_valid():
# 					serializer.save()
# 					responseObject = {'message': 'Login Successful', 'data': tokenData, 'status':True}
# 					return JsonResponse(responseObject, safe=False)
# 			except Users.DoesNotExist:
# 				responseObject = {'message': 'Login UnSuccessful Username and password not matches', 'data':{}, 'status':False}
# 				return JsonResponse(responseObject, safe=False)
# 		else:	
# 			responseObject = {'message': 'User Role Required', 'data': [], 'status':False}
# 			return JsonResponse(responseObject, safe=False)
        

def CustomAuthToken(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        string 			= data['password']
        #role1            = data['role']
        user_type        = int(data['user_type'])
        roleCheck       = tokenEmpCheck(user_type)
        print(roleCheck)
        if roleCheck:
            result 			= hashlib.md5(string.encode()) 
            passord			= result.hexdigest()
            print(data['username'])
            print(passord)
            print(int(user_type))
            try:
                users = Users.objects.get(username=data['username'], password=passord, user_type=int(user_type))
                print(users)
                print(users)
                if users:
                    token 	= secrets.token_hex(20)
                    #print(users.user_id)
                    u_id = users.user_id
                    #print(u_id)
                    #adv_executive = Client_access.objects.get(userid=u_id)
                    #print(adv_executive.clientid)
                    if(users.role==4):
                        #print('hell')
                        adv_executive = Client_access.objects.get(userid=u_id)
                        clientAff_id =adv_executive.clientid
                    elif(users.role==5):
                        #print('hell22')
                        pub_executive = Publisher_access.objects.get(userid=u_id)
                        clientAff_id =pub_executive.affiliateid
                    else:
                        clientAff_id =''
                    tokenData 	= {'token':token,'user_id': users.user_id,'username':users.username,'email':users.email,'firstname':users.firstname,'lastname':users.lastname,'role':users.role,'clientAff_id':clientAff_id}
                    print(tokenData)
                    serializer	 = LoginTokenSerializer(data=tokenData)
                    if serializer.is_valid():
                        serializer.save()
                        responseObject = {'message': 'Login Successful', 'data': tokenData, 'status':True}
                        return JsonResponse(responseObject, safe=False)
            except Users.DoesNotExist:
                print("hi")
                responseObject = {'message': 'Login UnSuccessful Username and password not matches', 'data':{}, 'status':False}
                return JsonResponse(responseObject, safe=False)
        else:	
            responseObject = {'message': 'User Type Required', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)


@csrf_exempt
def clients_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            if request.method == 'GET':
                clients = Clients.objects.all()
                serializer = ClientsSerializer(clients, many=True)
                #print(serializer)
                responseObject = {'message': 'Advertiser Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                serializer = ClientsSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    #return JsonResponse(serializer.data, status=201)
                    responseObject = {'message': 'Advertiser Added successfully', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)			


def campaigns_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            if request.method == 'GET':
                campaigns = Campaigns.objects.all()
                print(campaigns)
                serializer = CampaignsSerializer(campaigns, many=True)
                #print(serializer)
                responseObject = {'message': 'Campaigns Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                serializer = CampaignsSerializer(data=data)
                print('abcd')
                #print(serializer)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Campaigns Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)



def clients_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                clients = Clients.objects.get(pk=pk)
            except Clients.DoesNotExist:
                responseObject = {'message': 'Advertiser not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = ClientsSerializer(clients)
                #print(serializer.data['clientid'])

                jsonData		= serializer.data
                responseObject = {'message': 'Advertiser Details', 'data':jsonData , 'status':True}
                return JsonResponse(responseObject, safe=False)

            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = ClientsSerializer(clients, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Advertiser Updated successfully', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, status=200)

            elif request.method == 'DELETE':
                try:
                    clients = Clients.objects.get(pk=pk)
                    clients.delete()
                    responseObject = {'message': 'Advertiser delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Clients.DoesNotExist:
                    responseObject = {'message': 'Advertiser not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
        
         




# def campaigns_list(request):
#     tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
#     if tokenempChk:
#         tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
#         if tokenStatus:	
#             if request.method == 'GET':
#                 campaigns = Campaigns.objects.all()
#                 serializer = CampaignsSerializer(campaigns, many=True)
#                 # return JsonResponse(serializer.data, safe=False)
#                 #tokenData 	= {'token':token,'user_id': users.user_id,'username':users.username,'email':users.email,'firstname':users.firstname,'lastname':users.lastname}
#                 responseObject = {'message': 'Campaigns Lists', 'data': serializer.data, 'status':True}
#                 return JsonResponse(responseObject, safe=False)
                
#             elif request.method == 'POST':
#                 data = JSONParser().parse(request)
#                 serializer = CampaignsSerializer(data=data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     responseObject = {'message': 'Campaigns Added successfully', 'data': serializer.data, 'status':True}
#                 return JsonResponse(responseObject, status=201)
#         else:
#             responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
#             return JsonResponse(responseObject, safe=False,status=204)
#     else:	
#         responseObject = {'message': 'Token Required', 'data': [], 'status':False}
#         return JsonResponse(responseObject, safe=False)					
        
        
def campaigns_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                campaigns = Campaigns.objects.get(pk=pk)
            except Campaigns.DoesNotExist:
                responseObject = {'message': 'Campaigns not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = CampaignsSerializer(campaigns)
                responseObject = {'message': 'Campaigns Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                # return JsonResponse(serializer.data)

            elif request.method == 'PUT':
                data 		= JSONParser().parse(request)

                
                if(campaigns.views != data['views']):
                    data['status']	= checkCampaignTotalLimitStatus(campaigns,data['views'])
                    
                if(campaigns.target_impression != data['target_impression']):
                    data['status']	= checkCampaignDailyLimitStatus(campaigns,data['target_impression'])
                    
                if(campaigns.expire_time != data['expire_time']):
                    data['status']	= checkCampaignExpireStatus(campaigns,data['expire_time'])

                serializer 	= CampaignsSerializer(campaigns, data=data)

                
                if serializer.is_valid():
                    serializer.save()
                    updateCampaignCacheData(pk,data)
                    responseObject = {'message': 'Campaigns Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            elif request.method == 'DELETE':
                try:
                    campaigns = Campaigns.objects.get(pk=pk)
                    campaigns.delete()
                    responseObject = {'message': 'Campaigns delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Campaigns.DoesNotExist:
                    responseObject = {'message': 'Campaigns not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)
        
def bannersupdate(request,pk):

    if request.method == 'POST':
        banners = Banners.objects.get(pk=pk)
        
        storagetype				= request.POST['storagetype']
        postData	={
            "campaignid":request.POST['campaignid'],
            "storagetype":request.POST['storagetype'],
            "description":request.POST['description'],
            "width":request.POST['width'],
            "height":request.POST['height'],
            "tracking_pixel":request.POST['tracking_pixel'],
            "comments":request.POST['comments'],
            "keyword":request.POST['keyword'],
            "url":request.POST['url'],
            "pluginversion":1,
            "updated":"2019-08-01 12:12:12",
            "acl_updated":"2019-08-01 12:12:12",
            "transparent":0,
            "iframe_friendly":1,
        }

        if storagetype == 'web':
            filename				= request.FILES['filename']
            fs						= FileSystemStorage()
            filename		 		= fs.save(filename.name, filename)
            uploaded_file_url 		= fs.url(filename)
            imageName				= filename
            postData.update({'filename' : imageName})
            postData.update({'contenttype' : 'gif'})


        
        if storagetype == 'html5':
            postData	= html5CreativeUpdate(request,postData)

            

        if storagetype == 'html':
     
            adtype		= request.POST['ext_bannertype']
            postData.update({'contenttype' : 'html'})
            postVideoData = {}

            
            if adtype 	== 'create_video':
                postData.update({'ext_bannertype' : adtype})
                if request.FILES['video_upload']:
                    filename				= request.FILES['video_upload']
                    fs						= FileSystemStorage()
                    filename		 		= fs.save(filename.name, filename)
                    uploaded_file_url 		= fs.url(filename)
                    videoName				= filename
                    postData.update({'filename' : videoName})
                    postVideoData.update({'vast_video_outgoing_filename' : videoName})
                

                
                skip			= 1 if request.POST['skip'] else 0
                postVideoData.update({'skip' : skip})

                if skip:
                    skip_time = request.POST['skip_time']
                    postVideoData.update({'skip_time' : skip_time})

                else:
                    postVideoData.update({'skip_time' : 0})
                
                postVideoData.update({'vast_video_bitrate' : request.POST['vast_video_bitrate']})
                postVideoData.update({'vast_video_width' : request.POST['width']})
                postVideoData.update({'vast_video_height' : request.POST['height']})
                vastVideoType		= request.POST['vast_video_type']
                postVideoData.update({'vast_video_type' : 'video'+vastVideoType})
                postVideoData.update({'vast_video_delivery' : request.POST['vast_video_delivery']})
                postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})

                mute			= 1 if request.POST['mute'] else 0
                postVideoData.update({'mute' : mute})
                
                postVideoData.update({'impression_pixel' : request.POST['impression_pixel']})
                postVideoData.update({'start_pixel' : request.POST['start_pixel']})
                postVideoData.update({'quater_pixel' : request.POST['quater_pixel']})
                postVideoData.update({'mid_pixel' : request.POST['mid_pixel']})
                postVideoData.update({'third_quater_pixel' : request.POST['third_quater_pixel']})
                postVideoData.update({'end_pixel' : request.POST['end_pixel']})
                postVideoData.update({'third_party_click' : request.POST['third_party_click']})
                postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})
                postVideoData.update({'status' : 'active'})
                
            else:
                tag						= request.POST['vast_tag']
                
                trimTag 				= tag.strip()
                postVideoData.update({'vast_tag' : trimTag})
        serializer = BannersSerializer(banners, data=postData)
        #serializer 			= BannersSerializer(data=postData)
        
        if serializer.is_valid():
            serializer.save()
        
        if storagetype == 'html':
            print('5')
            bannerObj 			= Banners.objects.latest('updated')
            banner_id			= bannerObj.bannerid
            postVideoData.update({'banner_id' : banner_id})
            
            vastBanner = banner_vast_element.objects.get(banner_id=banner_id)
            videoserializer 			= BannervastSerializer(vastBanner, data=postVideoData,)
            if videoserializer.is_valid():
                videoserializer.save() 
        
        updateDeliveryAd(pk)    


        # bannerCache = 'delivery_ad_' + str(pk) + '.py'
        # print(bannerCache)
        # f 			= open(deliveryCachePath + bannerCache, 'w+')
        # if storagetype == 'html':
            # jsonArr 	= [serializer.data,videoserializer.data]
        # else:
            # jsonArr 	= serializer.data


        # jsonString 	= json.dumps(jsonArr)
        # f.write(jsonString)
        # f.close()
            
            
        if storagetype == 'html':
            responseObject = {'message': 'Banners Added successfully', 'data': serializer.data, 'videoData':videoserializer.data, 'status':True}

        else:
            responseObject = {'message': 'Banners Added successfully', 'data': serializer.data, 'status':True}


        return JsonResponse(responseObject, status=200)

def banners_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                banners 	= Banners.objects.all().order_by('-bannerid')
                serializer 	= BannersSerializer(banners, many=True)
                # return JsonResponse(serializer.data, safe=False)
                responseObject = {'message': 'Banners Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                
                
                storagetype				= request.POST['storagetype']
                postData	={
                    "campaignid":request.POST['campaignid'],
                    "storagetype":request.POST['storagetype'],
                    "description":request.POST['description'],
                    "width":request.POST['width'],
                    "height":request.POST['height'],
                    "tracking_pixel":request.POST['tracking_pixel'],
                    "comments":request.POST['comments'],
                    "keyword":request.POST['keyword'],
                    "url":request.POST['url'],
                    "pluginversion":1,
                    "updated":"2019-08-01 12:12:12",
                    "acl_updated":"2019-08-01 12:12:12",
                    "transparent":0,
                    "iframe_friendly":1,
                }

                if storagetype == 'web':
                    filename				= request.FILES['filename']
                    fs						= FileSystemStorage()
                    filename		 		= fs.save(filename.name, filename)
                    uploaded_file_url 		= fs.url(filename)
                    imageName				= filename
                    postData.update({'filename' : imageName})
                    postData.update({'contenttype' : 'gif'})


                
                if storagetype == 'html5':
                   postData	= html5CreativeUpdate(request,postData)

                    

                if storagetype == 'html':
                    adtype		= request.POST['ext_bannertype']
                    postData.update({'contenttype' : 'html'})
                    postVideoData = {}

                    
                    if adtype 	== 'create_video':
                        postData.update({'ext_bannertype' : adtype})
                        if request.FILES['video_upload']:
                            filename				= request.FILES['video_upload']
                            fs						= FileSystemStorage()
                            filename		 		= fs.save(filename.name, filename)
                            uploaded_file_url 		= fs.url(filename)
                            videoName				= filename
                            postData.update({'filename' : videoName})
                            postVideoData.update({'vast_video_outgoing_filename' : videoName})
                        
                        if request.POST['skip'] == 'false':
                            skip			= 0
                        else:
                            skip			= 1
                        postVideoData.update({'skip' : skip})
                        

                        if skip:
                            skip_time = request.POST['skip_time']
                            postVideoData.update({'skip_time' : skip_time})

                        else:
                            postVideoData.update({'skip_time' : 0})
                        
                        postVideoData.update({'vast_video_bitrate' : request.POST['vast_video_bitrate']})
                        postVideoData.update({'vast_video_width' : request.POST['width']})
                        postVideoData.update({'vast_video_height' : request.POST['height']})
                        vastVideoType		= request.POST['vast_video_type']
                        postVideoData.update({'vast_video_type' : 'video'+vastVideoType})
                        postVideoData.update({'vast_video_delivery' : request.POST['vast_video_delivery']})
                        postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})

                        mute			= 1 if request.POST['mute'] else 0
                        postVideoData.update({'mute' : mute})
                        
                        postVideoData.update({'impression_pixel' : request.POST['impression_pixel']})
                        postVideoData.update({'start_pixel' : request.POST['start_pixel']})
                        postVideoData.update({'quater_pixel' : request.POST['quater_pixel']})
                        postVideoData.update({'mid_pixel' : request.POST['mid_pixel']})
                        postVideoData.update({'third_quater_pixel' : request.POST['third_quater_pixel']})
                        postVideoData.update({'end_pixel' : request.POST['end_pixel']})
                        postVideoData.update({'third_party_click' : request.POST['third_party_click']})
                        postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})
                        postVideoData.update({'status' : 'active'})
                        
                    else:
                        tag						= request.POST['vast_tag']
                        trimTag 				= tag.strip()
                        postVideoData.update({'vast_tag' : trimTag})
                
                serializer 			= BannersSerializer(data=postData)
                if serializer.is_valid():
                    serializer.save()
                    
                    
                if storagetype == 'html':
                    bannerObj 			= Banners.objects.latest('updated')
                    banner_id			= bannerObj.bannerid
                    postVideoData.update({'banner_id' : banner_id})
                    print(postVideoData);
                    videoserializer 			= BannervastSerializer(data=postVideoData)
                    if videoserializer.is_valid():
                        videoserializer.save()
                        
                banner 		= Banners.objects.latest('bannerid')
                
                updateDeliveryAd(banner.bannerid)
                        
                    
                    
                if storagetype == 'html':
                    responseObject = {'message': 'Banners Added successfully', 'data': serializer.data, 'videoData':videoserializer.data, 'status':True}

                else:
                    responseObject = {'message': 'Banners Added successfully', 'data': serializer.data, 'status':True}


                return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
             
def banners_detail(request, pk):
    print("sdfkcsad")
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                banners = Banners.objects.get(pk=pk)
            except Banners.DoesNotExist:
                responseObject = {'message': 'Banners not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer 		= BannersSerializer(banners)
                bannerData		= serializer.data
                storagetype		= serializer.data.get('storagetype')
                print(storagetype)
                
                if storagetype == 'html':
                    videobanners 			= banner_vast_element.objects.get(banner_id=pk)
                    videoserializer 		= BannervastSerializer(videobanners)
                    videodata				= videoserializer.data
                    
                    for (key,value) in videodata.items():
                        bannerData.update({key : value})
                    
                    responseObject 			= {'message': 'Banners Details', 'data':bannerData, 'status':True}

                else:
                    responseObject = {'message': 'Banners Details', 'data':bannerData, 'status':True}
                    
                return JsonResponse(responseObject, safe=False)
                # return JsonResponse(serializer.data)

            elif request.method == 'PUT':
                data = request
                print(data)
                storagetype				= 'kk'#request.PUT['storagetype']
                # postData	={
                    # "campaignid":request.POST['campaignid'],
                    # "storagetype":request.POST['storagetype'],
                    # "description":request.POST['description'],
                    # "width":request.POST['width'],
                    # "height":request.POST['height'],
                    # "tracking_pixel":request.POST['tracking_pixel'],
                    # "comments":request.POST['comments'],
                    # "keyword":request.POST['keyword'],
                    # "url":request.POST['url'],
                    # "pluginversion":1,
                    # "updated":"2019-08-01 12:12:12",
                    # "acl_updated":"2019-08-01 12:12:12",
                    # "transparent":0,
                    # "iframe_friendly":1,
                # }

                if storagetype == 'web':
                    filename				= request.FILES['filename']
                    fs						= FileSystemStorage()
                    filename		 		= fs.save(filename.name, filename)
                    uploaded_file_url 		= fs.url(filename)
                    imageName				= filename
                    postData.update({'filename' : imageName})
                    postData.update({'contenttype' : 'gif'})


                
                # if storagetype == 'html5':
                    # htmltemplate		= request.POST['htmltemplate']
                    # postData.update({'contenttype' : 'html5'})
                    # postData.update({'htmltemplate' : htmltemplate})
                    

                # if storagetype == 'html':
                    # adtype		= request.POST['ext_bannertype']
                    # postData.update({'contenttype' : 'html'})
                    # postVideoData = {}

                    
                    # if adtype 	== 'create_video':
                        # postData.update({'ext_bannertype' : adtype})
                        # if request.FILES['video_upload']:
                            # filename				= request.FILES['video_upload']
                            # fs						= FileSystemStorage()
                            # filename		 		= fs.save(filename.name, filename)
                            # uploaded_file_url 		= fs.url(filename)
                            # videoName				= filename
                            # postData.update({'filename' : videoName})
                            # postVideoData.update({'vast_video_outgoing_filename' : videoName})
                        

                        
                        # skip			= 1 if request.POST['skip'] else 0
                        # postVideoData.update({'skip' : skip})

                        # if skip:
                            # skip_time = request.POST['skip_time']
                            # postVideoData.update({'skip_time' : skip_time})

                        # else:
                            # postVideoData.update({'skip_time' : 0})
                        
                        # postVideoData.update({'vast_video_bitrate' : request.POST['vast_video_bitrate']})
                        # postVideoData.update({'vast_video_width' : request.POST['width']})
                        # postVideoData.update({'vast_video_height' : request.POST['height']})
                        # vastVideoType		= request.POST['vast_video_type']
                        # postVideoData.update({'vast_video_type' : 'video'+vastVideoType})
                        # postVideoData.update({'vast_video_delivery' : request.POST['vast_video_delivery']})
                        # postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})

                        # mute			= 1 if request.POST['mute'] else 0
                        # postVideoData.update({'mute' : mute})
                        
                        # postVideoData.update({'impression_pixel' : request.POST['impression_pixel']})
                        # postVideoData.update({'start_pixel' : request.POST['start_pixel']})
                        # postVideoData.update({'quater_pixel' : request.POST['quater_pixel']})
                        # postVideoData.update({'mid_pixel' : request.POST['mid_pixel']})
                        # postVideoData.update({'third_quater_pixel' : request.POST['third_quater_pixel']})
                        # postVideoData.update({'end_pixel' : request.POST['end_pixel']})
                        # postVideoData.update({'third_party_click' : request.POST['third_party_click']})
                        # postVideoData.update({'vast_video_duration' : request.POST['vast_video_duration']})
                        # postVideoData.update({'status' : 'active'})
                        
                    # else:
                        # tag						= request.POST['vast_tag']
                        # trimTag 				= tag.strip()
                        # postVideoData.update({'vast_tag' : trimTag})
                
                # serializer 			= BannersSerializer(data=postData)
                # if serializer.is_valid():
                    # serializer.save()
                
                # if storagetype == 'html':
                    # bannerObj 			= Banners.objects.latest('updated')
                    # banner_id			= bannerObj.bannerid
                    # postVideoData.update({'banner_id' : banner_id})
                    # videoserializer 			= BannervastSerializer(data=postVideoData)
                    # if videoserializer.is_valid():
                        # videoserializer.save()
                    
                    
                if storagetype == 'html':
                    responseObject = {'message': 'Banners Updated successfully', 'data': {},'status':True}

                else:
                    responseObject = {'message': 'Banners Updated successfully', 'data': {}, 'status':True}


                return JsonResponse(responseObject, status=201)	
                
            elif request.method == 'DELETE':
                try:
                    banners = Banners.objects.get(pk=pk)
                    banners.delete()
                    responseObject = {'message': 'Banners delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Banners.DoesNotExist:
                    responseObject = {'message': 'Banners not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)				    

def zones_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                zones = Zones.objects.all().order_by('-zoneid')
                serializer = ZonesSerializer(zones, many=True)
                # return JsonResponse(serializer.data, safe=False)
                responseObject = {'message': 'Zones Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data 		= JSONParser().parse(request)
                serializer 	= ZonesSerializer(data=data)                                                                                                                                                                             
                if serializer.is_valid():
                    serializer.save()
                    zone 		= Zones.objects.latest('zoneid')
                    zoneCache 	= 'delivery_zone_' + str(zone.zoneid) + '.py'
               
                    f 			= open(deliveryCachePath + zoneCache, 'w+')
                    
                    jsonArr 	= serializer.data
                    jsonString 	= json.dumps(jsonArr)
                    f.write(jsonString)
                    f.close()
                    
                    
                    
                    responseObject = {'message': 'Zones Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
        
def zones_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                zones = Zones.objects.get(pk=pk)
            except Zones.DoesNotExist:
                responseObject = {'message': 'Zones not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = ZonesSerializer(zones)
                # return JsonResponse(serializer.data)
                responseObject = {'message': 'Zones Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)

            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = ZonesSerializer(zones, data=data)
                if serializer.is_valid():
                    serializer.save()
                    
                    zone 		= Zones.objects.latest('zoneid')
                    zoneCache 	= 'delivery_zone_' + str(pk) + '.py'
                    f 			= open(deliveryCachePath + zoneCache, 'w+')
                    jsonArr 	= data
                    jsonString 	= json.dumps(jsonArr)
                    f.write(jsonString)
                    f.close()
                    
                    responseObject = {'message': 'Zones Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            elif request.method == 'DELETE':
                try:
                    zones = Zones.objects.get(pk=pk)
                    zones.delete()
                    responseObject = {'message': 'Zones delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Zones.DoesNotExist:
                    responseObject = {'message': 'Zones not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)				             

def affiliates_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                affiliates = Affiliates.objects.all().order_by('-affiliateid')
                serializer = AffiliatesSerializer(affiliates, many=True)
                # return JsonResponse(serializer.data, safe=False)
                responseObject = {'message': 'Affiliates Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                serializer = AffiliatesSerializer(data=data)                                                                                                                                                                             
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Affiliates Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
        
def affiliates_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                affiliates = Affiliates.objects.get(pk=pk)
            except Affiliates.DoesNotExist:
                responseObject = {'message': 'Affiliates not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = AffiliatesSerializer(affiliates)
                responseObject = {'message': 'Affiliates Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)


            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = AffiliatesSerializer(affiliates, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Affiliates Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            elif request.method == 'DELETE':
                try:
                    affiliates = Affiliates.objects.get(pk=pk)
                    affiliates.delete()
                    responseObject = {'message': 'Affiliates delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Affiliates.DoesNotExist:
                    responseObject = {'message': 'Affiliates not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)				    





# def users_list(request):
# 			if request.method == 'GET':
# 							tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
# 							if tokenempChk:
# 								tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
# 								if tokenStatus:

# 									users = Users.objects.all()
# 									#print(users)
# 									serializer = UsersCustomizeSerializer(users, many=True)
# 									# return JsonResponse(serializer.data, safe=False)
# 									responseObject = {'message': 'Users Lists', 'data': serializer.data, 'status':True}
# 									return JsonResponse(responseObject, safe=False)
# 								else:
# 									responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
# 									return JsonResponse(responseObject, safe=False,status=204)
# 							else:	
# 								responseObject = {'message': 'Token Required', 'data': [], 'status':False}
# 								return JsonResponse(responseObject, safe=False)				
                        
# 			elif request.method == 'POST':
# 				data 			= JSONParser().parse(request)
# 				string 			= data['password']
# 				roleGiven 		= int(data['role'])
# 				result 			= hashlib.md5(string.encode()) 
# 				passord			= result.hexdigest()
# 				data.update({'password' :passord })
# 				print(data)
            
# 				users = Users.objects.filter(username=data['username'])
# 				#print(users.count())

# 				if users.count() != 0:
# 					#print(users.count())
# 					if users.count() < 2:
# 						saveRole =users[0].role
# 						# print(saveRole)
# 						# print(roleGiven)
# 						if (saveRole != roleGiven) and (roleGiven ==2 or roleGiven ==3) and saveRole < 4:
# 							serializer = UsersSerializer(data=data)                                                                                                                                                                             
# 							if serializer.is_valid():
# 								serializer.save()
# 								responseObject = {'message': 'Users Added successfully', 'data': serializer.data, 'status':True}

# 						else:
# 							responseObject = {'message': 'user of same email id will not register for other roles', 'data': [], 'status':True}
# 					else:
# 						responseObject = {'message': 'both role users of same email id have registerd', 'data': [], 'status':True}
                                
# 					#responseObject = {'message': 'user of same email id will not register for other roles', 'data': [], 'status':True}
# 					return JsonResponse(responseObject, safe=False,status=200)

# 				else:		
# 					serializer = UsersSerializer(data=data)                                                                                                                                                                             
# 					if serializer.is_valid():
# 						serializer.save()
# 					responseObject = {'message': 'Users Added successfully', 'data': serializer.data, 'status':True}
# 					return JsonResponse(responseObject, safe=False,status=200)
# 					


def users_list(request):
            if request.method == 'GET':
                            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
                            if tokenempChk:
                                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                                if tokenStatus:

                                    users = Users.objects.all()
                                    #print(users)
                                    serializer = UsersCustomizeSerializer(users, many=True)
                                    # return JsonResponse(serializer.data, safe=False)
                                    responseObject = {'message': 'Users Lists', 'data': serializer.data, 'status':True}
                                    return JsonResponse(responseObject, safe=False)
                                else:
                                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                                    return JsonResponse(responseObject, safe=False,status=204)
                            else:	
                                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                                return JsonResponse(responseObject, safe=False)				
                        
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                string 			= data['password']
                #role 			= data['role']
                user_type 		= data['user_type']
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                data.update({'role' :user_type })
                print(data)
                try:
                    users = Users.objects.get(username=data['username'], user_type=int(user_type))
                    responseObject = {'message': 'Username Already Exist!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)	
                except Users.DoesNotExist:
                    serializer = UsersSerializer(data=data)                                                                                                                                                                             
                    if serializer.is_valid():
                        serializer.save()
                        subject = "User Registration"
                        message = "User Register successfully"
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = ['sunil@morrisdigital.mobi',]
                        send_mail( subject, message, email_from, recipient_list )						
                        responseObject = {'message': 'Users Added successfully', 'data': serializer.data, 'status':True}
                        return JsonResponse(responseObject, status=201)		

def users_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                users = Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = UsersSerializer(users)
                responseObject = {'message': 'Users Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)


            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = UsersSerializer(users, data=data)
                string 			= data['password']
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Users Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            elif request.method == 'DELETE':
                try:
                    users = Users.objects.get(pk=pk)
                    users.delete()
                    responseObject = {'message': 'Users delete successfully!', 'data': [], 'status':True}
                    return JsonResponse(responseObject,status=200)
                except Users.DoesNotExist:
                    responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
                    return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)				

def home_data(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:

        with connection.cursor() as cursor:
            # sql = "SELECT  SUM(s.requests) AS requests, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day  FROM inventory_clients as a, inventory_campaigns as b, inventory_banners as c, inventory_rv_data_summary_ad_hourly as s WHERE a.clientid=b.clientid AND b.campaignid=c.campaignid AND c.bannerid=s.creative_id "+getWhereDate(oStartDate, oEndDate)+" group by day"
            sql = "SELECT  SUM(s.requests) AS requests, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day  FROM inventory_clients as a, inventory_campaigns as b, inventory_banners as c, inventory_rv_data_summary_ad_hourly as s WHERE a.clientid=b.clientid AND b.campaignid=c.campaignid  "+getWhereDate(oStartDate, oEndDate)+" group by day"
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
                responseObject = {'message': 'Home Data', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'Data Not Found!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def notification_data(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:

        with connection.cursor() as cursor:
            # sql = "SELECT  SUM(s.requests) AS requests, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day  FROM inventory_clients as a, inventory_campaigns as b, inventory_banners as c, inventory_rv_data_summary_ad_hourly as s WHERE a.clientid=b.clientid AND b.campaignid=c.campaignid AND c.bannerid=s.creative_id "+getWhereDate(oStartDate, oEndDate)+" group by day"
            sql = "SELECT campaignid,clientid,campaignname,views,expire_time,activate_time,status FROM inventory_campaigns"
            #print(sql)
            cursor.execute(sql)
            field_names = [item[0] for item in cursor.description]
            rawData = cursor.fetchall()
            arrlen = len(rawData)
            result = []
            if rawData:
                for row in rawData:
                    #print(len(row))
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                         
                    campStatus = objDict['status']
                    #print(campStatus)
                    if campStatus==0:
                        campStatus1 = 'inactive'
                    elif campStatus==1:
                        campStatus1 = 'active'
                    elif campStatus==2:
                        campStatus1 = 'expired'
                    elif campStatus==3:
                        campStatus1 = 'completed'
                    elif campStatus==4:
                        campStatus1 = 'delevering'                        
                    # else:
                    #     campStatus1 ="inactive"    
                    #print(objDict)
                    #print(len(objDict))
                    
                    objDict1      = {'campaignid' :objDict['campaignid'], 'campaignname':objDict['campaignname'], 'clientid':objDict['clientid'],'views':objDict['views'],'campaignStatus':campStatus1,'expire_time':objDict['expire_time'],'activate_time':objDict['activate_time']}        
                    result.append(objDict1)
                    finalData       = {'notificationCount' :arrlen, 'reportData':result}
                responseObject = {'message': 'Notifications Data', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'Data Not Found!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def anotification_data(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    userId 		= str(userId)
    if tokenStatus:

        with connection.cursor() as cursor:
            # sql = "SELECT  SUM(s.requests) AS requests, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day  FROM inventory_clients as a, inventory_campaigns as b, inventory_banners as c, inventory_rv_data_summary_ad_hourly as s WHERE a.clientid=b.clientid AND b.campaignid=c.campaignid AND c.bannerid=s.creative_id "+getWhereDate(oStartDate, oEndDate)+" group by day"
            sql = "SELECT c.campaignid,c.clientid,c.campaignname,c.views,c.expire_time,c.activate_time,c.status FROM inventory_campaigns as c,inventory_clients as a WHERE a.clientid=c.clientid AND a.userid="+userId
            print(sql)
            cursor.execute(sql)
            field_names = [item[0] for item in cursor.description]
            rawData = cursor.fetchall()
            arrlen = len(rawData)
            result = []
            if rawData:
                for row in rawData:
                    #print(len(row))
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                         
                    campStatus = objDict['status']
                    #print(campStatus)
                    if campStatus==0:
                        campStatus1 = 'inactive'
                    elif campStatus==1:
                        campStatus1 = 'active'
                    elif campStatus==2:
                        campStatus1 = 'expired'
                    elif campStatus==3:
                        campStatus1 = 'completed'
                    elif campStatus==4:
                        campStatus1 = 'delevering'                        
                    # else:
                    #     campStatus1 ="inactive"    
                    #print(objDict)
                    #print(len(objDict))
                    
                    objDict1      = {'campaignid' :objDict['campaignid'], 'campaignname':objDict['campaignname'], 'clientid':objDict['clientid'],'views':objDict['views'],'campaignStatus':campStatus1,'expire_time':objDict['expire_time'],'activate_time':objDict['activate_time']}        
                    result.append(objDict1)
                    finalData       = {'notificationCount' :arrlen, 'reportData':result}
                responseObject = {'message': 'Notifications Data', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'Data Not Found!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def pnotification_data(request):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    userId 		= str(userId)
    if tokenStatus:

        with connection.cursor() as cursor:
            # sql = "SELECT  SUM(s.requests) AS requests, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day  FROM inventory_clients as a, inventory_campaigns as b, inventory_banners as c, inventory_rv_data_summary_ad_hourly as s WHERE a.clientid=b.clientid AND b.campaignid=c.campaignid AND c.bannerid=s.creative_id "+getWhereDate(oStartDate, oEndDate)+" group by day"
            #sql = "SELECT c.campaignid,c.clientid,c.campaignname,c.views,c.expire_time,c.activate_time,c.status FROM inventory_campaigns as c,inventory_clients as a WHERE a.clientid=c.clientid AND a.userid="+userId
            sql = "SELECT c.campaignid,c.clientid,c.campaignname,c.views,c.expire_time,c.activate_time,c.status FROM inventory_campaigns as c,inventory_zones as z,inventory_banners as d,inventory_affiliates as f,inventory_rv_ad_zone_assoc as rva WHERE f.affiliateid=z.affiliateid AND rva.zone_id=z.zoneid AND rva.ad_id=d.bannerid AND c.campaignid=d.campaignid AND f.userid="+userId +" GROUP BY c.campaignid" 
            print(sql)
            cursor.execute(sql)
            field_names = [item[0] for item in cursor.description]
            rawData = cursor.fetchall()
            arrlen = len(rawData)
            result = []
            if rawData:
                for row in rawData:
                    #print(len(row))
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                         
                    campStatus = objDict['status']
                    #print(campStatus)
                    if campStatus==0:
                        campStatus1 = 'inactive'
                    elif campStatus==1:
                        campStatus1 = 'active'
                    elif campStatus==2:
                        campStatus1 = 'expired'
                    elif campStatus==3:
                        campStatus1 = 'completed'
                    elif campStatus==4:
                        campStatus1 = 'delevering'                        
                    # else:
                    #     campStatus1 ="inactive"    
                    #print(objDict)
                    #print(len(objDict))
                    
                    objDict1      = {'campaignid' :objDict['campaignid'], 'campaignname':objDict['campaignname'], 'clientid':objDict['clientid'],'views':objDict['views'],'campaignStatus':campStatus1,'expire_time':objDict['expire_time'],'activate_time':objDict['activate_time']}        
                    result.append(objDict1)
                    finalData       = {'notificationCount' :arrlen, 'reportData':result}
                responseObject = {'message': 'Notifications Data', 'data': finalData, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'Data Not Found!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)



# def user_login(request):
# 	if request.method == 'GET':
# 		inventory = inventory.objects.all()
# 		serializer = inventorySerializer(inventory, many=True)
# 		return JsonResponse(serializer.data, safe=False)
        
# 	elif request.method == 'POST':
# 		data = JSONParser().parse(request)
#         print(data)
# 		serializer = UsersSerializer(data=data)                                                                                                                                                                             
# 		if serializer.is_valid():
# 			serializer.save()
# 			return JsonResponse(serializer.data, status=201)
# 		return JsonResponse(serializer.errors, status=400) 

def changePassword(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                #users = Users.objects.get(pk=pk)
                data 			= JSONParser().parse(request)
                old_password    = data['old_password']
                result 			= hashlib.md5(old_password.encode())
                old_password	= result.hexdigest()
                users           = Users.objects.get(user_id=str(pk), password=old_password)
            
            except Users.DoesNotExist:
                responseObject = {'message': 'Old Password did not match!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'PUT':
                    new_password    = data['new_password']
                    result 			= hashlib.md5(new_password.encode())
                    new_password	= result.hexdigest()
                    data.update({'password' :new_password })
                    serializer = UsersSerializer(users, data=data)
                    if serializer.is_valid():
                        serializer.save()
                        responseObject = {'message': 'Password Changed successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)

        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def forgotPassword(request):
    # tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    # if tokenempChk:
    # 	tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    # 	if tokenStatus:	
            try:
                #users = Users.objects.get(pk=pk)
                data 			= JSONParser().parse(request)
                email_id        = data['email_id']
                user_role       = data['user_role']
                # print(data)
                #result 		    = hashlib.md5(old_password.encode())
                #old_password	= result.hexdigest()



                users           = Users.objects.get(username=email_id, role=int(user_role))
                #print(users)
            except Users.DoesNotExist:
                responseObject = {'message': 'Email did not match!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=200)

            if request.method == 'PUT':
                    varString 	= 	hashlib.md5(str(randint(100, 999)).encode())
                    var			= varString.hexdigest()
                    var			= var[0:8]
                    print(var)
                    data2={}
                    subject = "Forgot Password"
                    message = "Your New Password Is " +var
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = ['sunil@morrisdigital.mobi',]
                    send_mail( subject, message, email_from, recipient_list )
                    responseObject = {'message':'New password Sent successfully on your mail id',  'data':{},  'status':True}
                    #return JsonResponse(responseObject, safe=False)
                    result 			= hashlib.md5(var.encode())
                    new_password	= result.hexdigest()
                    data2.update({'password' :new_password })
                    data2.update({'change_passwordStatus' :1 })
                    serializer = UsersSerializer(users, data=data2)
                    if serializer.is_valid():
                         serializer.save()
                    responseObject = {'message': 'Password Sent successfully', 'data': [], 'status':True}
                    return JsonResponse(responseObject, status=200)

    # 	else:
    # 		responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
    # 		return JsonResponse(responseObject, safe=False,status=204)
    # else:	
    # 	responseObject = {'message': 'Token Required', 'data': [], 'status':False}
    # 	return JsonResponse(responseObject, safe=False)

def advertiserDelete(request):				
            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
            if tokenempChk:
                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                if tokenStatus:
                    if request.method == 'POST':
                        data 			= JSONParser().parse(request)			
                        for rowiddd in data['ids']:
                            rowida = str(rowiddd)
                            #print(rowida)
                            client =  Clients.objects.get(pk=rowida)
                            client.delete()
                            campaign_all = Campaigns.objects.filter(clientid=rowida)
                            #print(campaign_all)
                            for rowid in campaign_all:
                                #print(rowid.campaignid)
                                rowid = rowid.campaignid
                                rowid = str(rowid)
                                print(rowid)
                                campaigns =  Campaigns.objects.get(pk=rowid)
                                campaigns.delete()
                                #rowid = str(rowid)
                                #print(campaigns)
                                banner_all = Banners.objects.filter(campaignid=rowid)
                                 #print(banner_all)
                                for banner in banner_all:
                                    banner_id = banner.bannerid
                                    print(banner_id)
                                    rowidd = str(banner_id)
                                    with connection.cursor() as cursor:

                                            cursor.execute("DELETE FROM inventory_rv_data_summary_ad_hourly WHERE creative_id ="+rowidd)
                                            cursor.execute("DELETE FROM inventory_rv_ad_zone_assoc WHERE ad_id = "+rowidd)
                                            cursor.execute("DELETE FROM inventory_banners WHERE bannerid ="+rowidd)
                                

                        responseObject = {'message': 'Advertiser delete successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)
            else:	
                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def campaignDelete(request):				
            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
            if tokenempChk:
                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                if tokenStatus:
                    if request.method == 'POST':
                        data 			= JSONParser().parse(request)
                        for rowid in data['ids']:
                            campaigns =  Campaigns.objects.get(pk=rowid)
                            campaigns.delete()
                            rowid = str(rowid)
                            banner_all = Banners.objects.filter(campaignid=rowid)
                            for banner in banner_all:
                                banner_id = banner.bannerid
                                #print(banner_id)
                                rowidd = str(banner_id)
                                with connection.cursor() as cursor:

                                        cursor.execute("DELETE FROM inventory_rv_data_summary_ad_hourly WHERE creative_id ="+rowidd)
                                        cursor.execute("DELETE FROM inventory_rv_ad_zone_assoc WHERE ad_id = "+rowidd)
                                        cursor.execute("DELETE FROM inventory_banners WHERE bannerid ="+rowidd)
                                

                        responseObject = {'message': 'Campaign delete successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)
            else:	
                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def bannerDelete(request):				
            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
            if tokenempChk:
                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                if tokenStatus:
                    if request.method == 'POST':
                        data 			= JSONParser().parse(request)
                        for rowid in data['ids']:
                                    rowid = str(rowid)
                                    with connection.cursor() as cursor:
                                        cursor.execute("DELETE FROM inventory_banners WHERE bannerid ="+rowid)
                                        cursor.execute("DELETE FROM inventory_rv_data_summary_ad_hourly WHERE creative_id = "+rowid)
                                        cursor.execute("DELETE FROM inventory_rv_ad_zone_assoc WHERE ad_id = "+rowid)

                            # banners = Banners.objects.get(pk=rowid)
                            # banners.delete()
                        responseObject = {'message': 'Banner delete successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)
            else:	
                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def zonesDelete(request):				
            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
            if tokenempChk:
                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                if tokenStatus:
                    if request.method == 'POST':
                        data 			= JSONParser().parse(request)
                        for rowid in data['ids']:
                                    rowid = str(rowid)
                                    with connection.cursor() as cursor:
                                          cursor.execute("DELETE FROM inventory_zones WHERE zoneid ="+rowid) 
                                          cursor.execute("DELETE FROM inventory_rv_data_summary_ad_hourly WHERE zone_id ="+rowid)
                                          cursor.execute("DELETE FROM inventory_rv_ad_zone_assoc WHERE zone_id ="+rowid)
                        
                        responseObject = {'message': 'Zone delete successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)
            else:	
                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def affiliatesDelete(request):				
            tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
            if tokenempChk:
                tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
                if tokenStatus:
                    if request.method == 'POST':
                        data 			= JSONParser().parse(request)
                        for rowid in data['ids']:
                            affiliates =  Affiliates.objects.get(pk=rowid)
                            affiliates.delete()
                            rowid = str(rowid)
                            zones_all = Zones.objects.filter(affiliateid=rowid)
                            for zones in zones_all:
                                zone_id = zones.zoneid
                                rowidd = str(zone_id)
                                with connection.cursor() as cursor:
                                        #rowid = str(rowid)
                                        cursor.execute("DELETE FROM inventory_rv_data_summary_ad_hourly WHERE zone_id = "+rowidd)
                                        cursor.execute("DELETE FROM inventory_rv_ad_zone_assoc WHERE zone_id = "+rowidd)
                                        cursor.execute("DELETE FROM inventory_zones WHERE zoneid ="+rowidd)
                                

                        responseObject = {'message': 'Affiliates delete successfully', 'data': [], 'status':True}
                        return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)
            else:	
                responseObject = {'message': 'Token Required', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)

def campaignActiveInactive(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                campaigns = Campaigns.objects.get(pk=pk)
            except Campaigns.DoesNotExist:
                responseObject = {'message': 'Campaigns not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = CampaignsSerializer(campaigns, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Campaigns Status Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)		

def pusers_list(request,affiliateid):
    
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                useridString 		= str(affiliateid)
                whereStr 			= 'inventory_publisher_access.affiliateid = '+useridString
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM inventory_users JOIN inventory_publisher_access ON inventory_publisher_access.userid = inventory_users.user_id WHERE "+whereStr
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
                        
                        #clients 	= Clients.objects.get(pk=userId)
                        #print(clients)
                        
                        responseObject = {'message': 'Executive List', 'data': result, 'status':True}
                        return JsonResponse(responseObject, safe=False)	
                    
                    else:
                        responseObject = {'message': 'No Executive Found!', 'data': [], 'status':False}
                        return JsonResponse(responseObject, safe=False)
                
            if request.method == 'POST':
                data = JSONParser().parse(request)
                string 			= data['password']
                role 			= int(data['role'])
                user_type 		= int(data['user_type'])
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                #print(data)
                try:
                    users = Users.objects.get(username=data['username'], user_type=user_type)
                    responseObject = {'message': 'Username Already Exist!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)	
                except Users.DoesNotExist:
                    serializer = UsersSerializer(data=data)                                                                                                                                                                             
                    if serializer.is_valid():
                        serializer.save()
                        if(role==4):
                            userinertid = (serializer.data).get("user_id")
                            #print(userid)
                            clientaccessdata = {'clientid':clientid,'userid': userinertid}
                            executiveserializer = Client_accessSerializer(data=clientaccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        if(role==5):
                            userinertid = (serializer.data).get("user_id")
                            print(affiliateid)
                            print(userid) 
                            publisheraccessdata = {'affiliateid':affiliateid,'userid': userinertid}
                            executiveserializer = Publisher_accessSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        if(role==3):
                            userinertid = (serializer.data).get("user_id")
                            print(userinertid) 
                            publisheraccessdata = {'parent_id':userId,'child_id': userinertid}
                            executiveserializer = User_assocSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save() 		         
                    responseObject = {'message': 'Executive Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid Executive', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def pusers_detail(request, pk):
    
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                users = Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = UsersSerializer(users)
                responseObject = {'message': 'Users Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)


            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                # string 			= data['password']
                # result 			= hashlib.md5(string.encode()) 
                # passord			= result.hexdigest()
                # data.update({'password' :passord })
                #data.update({'userid' :userId })
                serializer = UsersSerializer(users, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Users Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            # elif request.method == 'DELETE':
            # 	try:
            # 		users = Users.objects.get(pk=pk)
            # 		users.delete()
            # 		responseObject = {'message': 'Users delete successfully!', 'data': [], 'status':True}
            # 		return JsonResponse(responseObject,status=200)
            # 	except Users.DoesNotExist:
            # 		responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
            # 		return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def adusers_list(request,clientid):
    
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                useridString 		= str(clientid)
                whereStr 			= 'inventory_client_access.clientid = '+useridString
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM inventory_users JOIN inventory_client_access ON inventory_client_access.userid = inventory_users.user_id WHERE "+whereStr
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
                        
                        #clients 	= Clients.objects.get(pk=userId)
                        #print(clients)
                        
                        responseObject = {'message': 'Executive List', 'data': result, 'status':True}
                        return JsonResponse(responseObject, safe=False)	
                    
                    else:
                        responseObject = {'message': 'No Executive Found!', 'data': [], 'status':False}
                        return JsonResponse(responseObject, safe=False)
                
            if request.method == 'POST':
                data = JSONParser().parse(request)
                string 			= data['password']
                role 			= int(data['role'])
                user_type 		= int(data['user_type'])
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                #print(data)
                try:
                    users = Users.objects.get(username=data['username'], user_type=user_type)
                    responseObject = {'message': 'Username Already Exist!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)	
                except Users.DoesNotExist:
                    serializer = UsersSerializer(data=data)                                                                                                                                                                             
                    if serializer.is_valid():
                        serializer.save()
                        if(role==4):
                            userid = (serializer.data).get("user_id")
                            #print(userid)
                            clientaccessdata = {'clientid':clientid,'userid': userid}
                            executiveserializer = Client_accessSerializer(data=clientaccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        if(role==5):
                            userid = (serializer.data).get("user_id")
                            #print(userid)
                            publisheraccessdata = {'affiliateid':clientid,'userid': userid}
                            executiveserializer = Publisher_accessSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        if(role==2):
                            userinertid = (serializer.data).get("user_id")
                            print(userinertid) 
                            publisheraccessdata = {'parent_id':userId,'child_id': userinertid}
                            executiveserializer = User_assocSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save() 		         								         
                    responseObject = {'message': 'Executive Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid Executive', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def adusers_detail(request, pk):
    print('hello')
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                users = Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = UsersSerializer(users)
                responseObject = {'message': 'Users Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)


            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                # string 			= data['password']
                # result 			= hashlib.md5(string.encode()) 
                # passord			= result.hexdigest()
                # data.update({'password' :passord })
                #data.update({'userid' :userId })
                serializer = UsersSerializer(users, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Users Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            # elif request.method == 'DELETE':
            # 	try:
            # 		users = Users.objects.get(pk=pk)
            # 		users.delete()
            # 		responseObject = {'message': 'Users delete successfully!', 'data': [], 'status':True}
            # 		return JsonResponse(responseObject,status=200)
            # 	except Users.DoesNotExist:
            # 		responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
            # 		return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)		

def publisheradmin_list(request):
    
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                useridString 		= str(userId)
                whereStr 			= 'inventory_user_assoc.parent_id = '+useridString
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM inventory_users JOIN inventory_user_assoc ON inventory_user_assoc.child_id = inventory_users.user_id WHERE "+whereStr
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
                        
                        #clients 	= Clients.objects.get(pk=userId)
                        #print(clients)
                        
                        responseObject = {'message': 'User List', 'data': result, 'status':True}
                        return JsonResponse(responseObject, safe=False)	
                    
                    else:
                        responseObject = {'message': 'No User Found!', 'data': [], 'status':False}
                        return JsonResponse(responseObject, safe=False)
                
            if request.method == 'POST':
                data = JSONParser().parse(request)
                string 			= data['password']
                role 			= int(data['role'])
                print(role)
                user_type 		= int(data['user_type'])
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                #print(data)
                try:
                    users = Users.objects.get(username=data['username'], user_type=user_type)
                    responseObject = {'message': 'Username Already Exist!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)	
                except Users.DoesNotExist:
                    serializer = UsersSerializer(data=data)                                                                                                                                                                             
                    if serializer.is_valid():
                        serializer.save()
                        if(role==4):
                            userinertid = (serializer.data).get("user_id")
                            #print(userid)
                            clientaccessdata = {'clientid':clientid,'userid': userinertid}
                            executiveserializer = Client_accessSerializer(data=clientaccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        if(role==5):
                            userinertid = (serializer.data).get("user_id")
                            print(affiliateid)
                            print(userid) 
                            publisheraccessdata = {'affiliateid':affiliateid,'userid': userinertid}
                            executiveserializer = Publisher_accessSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save()
                        
                        if(role==2 or role==3):
                            userinertid = (serializer.data).get("user_id")
                            print(userinertid) 
                            publisheraccessdata = {'parent_id':userId,'child_id': userinertid}
                            executiveserializer = User_assocSerializer(data=publisheraccessdata)
                            if executiveserializer.is_valid():
                                executiveserializer.save() 		         
                    responseObject = {'message': 'User Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid Executive', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def publisheradmin_detail(request, pk):
    
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                users = Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = UsersSerializer(users)
                responseObject = {'message': 'Users Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)


            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                # string 			= data['password']
                # result 			= hashlib.md5(string.encode()) 
                # passord			= result.hexdigest()
                # data.update({'password' :passord })
                #data.update({'userid' :userId })
                serializer = UsersSerializer(users, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Users Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

            # elif request.method == 'DELETE':
            # 	try:
            # 		users = Users.objects.get(pk=pk)
            # 		users.delete()
            # 		responseObject = {'message': 'Users delete successfully!', 'data': [], 'status':True}
            # 		return JsonResponse(responseObject,status=200)
            # 	except Users.DoesNotExist:
            # 		responseObject = {'message': 'Users not found!!', 'data': [], 'status':False}
            # 		return JsonResponse(responseObject,status=204)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def advertiserVastStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidString 		= str(pk)
        whereStr 			= 'c.clientid = '+clientidString
        with connection.cursor() as cursor:
            sql = "SELECT sum(count) as count, DATE(interval_start) as dimension_id, DATE(interval_start) as dimension_name, vast_event_id as event_id FROM inventory_rv_stats_vast AS s JOIN inventory_banners as b ON s.creative_id = b.bannerid JOIN inventory_campaigns AS c ON b.campaignid = c.campaignid WHERE "+whereStr+" "+AgetWhereDate(oStartDate, oEndDate)+" GROUP BY dimension_id, vast_event_id,s.interval_start ORDER BY s.interval_start, vast_event_id ASC"
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
                responseObject = {'message': 'Advertisers Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def linkedZones(request,pk):
    # if request.GET.get('period_preset'):
    # 	getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
    # 	print(getDateBYFiletr)
    # 	oStartDate	= getDateBYFiletr['period_start']
    # 	oEndDate	= getDateBYFiletr['period_end']
    # else:
    # 	oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
    # 	oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidString 		= str(pk)
        whereStr 			= 'b.campaignid = '+campaignidString+" AND"
        with connection.cursor() as cursor:
            sql = "SELECT z.zoneid,z.zonename FROM inventory_banners as b,inventory_rv_ad_zone_assoc as az,inventory_zones as z WHERE " +whereStr+ " b.bannerid=az.ad_id AND az.zone_id=z.zoneid"
            #print(sql)
            cursor.execute(sql)
            field_names = [item[0] for item in cursor.description]
            rawData = cursor.fetchall()
            #print(rawData)
            result = []
            if rawData:
                for row in rawData:
                    objDict = {}
                    for index, value in enumerate(row):
                        objDict[field_names[index]] = value
                    result.append(objDict)
                responseObject = {'message': 'Linked Campaign Banners', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': "Linked Campaign Banners doesn't Exists!", 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)


def campaignsVastStats(request,pk,id):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidString 		= str(pk)
        campid 		= str(id)
        #whereStr 			= 'm.clientid = '+clientidString+' AND '
        whereStr 			= 'b.campaignid = '+campid
        with connection.cursor() as cursor:
            sql = "SELECT sum(count) as count, DATE(interval_start) as dimension_id, DATE(interval_start) as dimension_name, vast_event_id as event_id FROM inventory_rv_stats_vast AS s JOIN inventory_banners as b ON s.creative_id = b.bannerid WHERE " +whereStr+ " "+ AgetWhereDate(oStartDate, oEndDate)+ " GROUP BY dimension_id, vast_event_id ,interval_start ORDER BY interval_start, vast_event_id ASC"
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
                
                # clients 	= Clients.objects.get(pk=pk)
                # print(clients)
                
                responseObject = {'message': 'Campaigns Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)	

def bannersVastStats(request,clientid,campaignid,bannerid):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        #campaignidString 		= str(campaignid)
        banneridString 		= str(bannerid)
        whereStr 				= 'creative_id = '+banneridString
        with connection.cursor() as cursor:
            sql = "SELECT sum(count) as count, DATE(interval_start) as dimension_id, DATE(interval_start) as dimension_name, vast_event_id as event_id FROM inventory_rv_stats_vast WHERE "+whereStr+" "+ AgetWhereDate(oStartDate, oEndDate)+ " GROUP BY dimension_id, vast_event_id,interval_start ORDER BY interval_start, vast_event_id ASC"
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
                
                #clients 	= Clients.objects.get(pk=pk)
                #print(clients)
                
                responseObject = {'message': 'Banners Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)


def websiteVastStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')

    clientidString 		= str(pk)
    #whereStr = ' p.affiliateid = '+clientidString+' AND '
    whereStr = ' a.affiliateid = '+clientidString
    with connection.cursor() as cursor:
        sql ="SELECT sum(count) as count, DATE(interval_start) as dimension_id, DATE(interval_start) as dimension_name, vast_event_id as event_id FROM inventory_rv_stats_vast AS s JOIN inventory_zones as z ON s.zone_id = z.zoneid JOIN inventory_affiliates as a ON a.affiliateid = z.affiliateid WHERE "+whereStr+" "+ AgetWhereDate(oStartDate, oEndDate)+ " GROUP BY dimension_id, vast_event_id,interval_start ORDER BY interval_start, vast_event_id ASC"
        #print(sql)
        cursor.execute(sql)
        field_names = [item[0] for item in cursor.description]

        rawData  = cursor.fetchall()
        result = []
        if rawData:
            for row in rawData:
                objDict = {}
                for index, value in enumerate(row):
                    objDict[field_names[index]] = value
                result.append(objDict)
            
            responseObject = {'message': 'Website Stats', 'data': result, 'status':True}
            return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)


def zoneVastStats(request,pk,id):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    else:
        oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
        oEndDate	=	datetime.today().strftime('%Y-%m-%d')
        
    tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        zoneidString 		= str(id)
        whereStr = ' zone_id = ' +zoneidString
        with connection.cursor() as cursor:
            sql = "SELECT sum(count) as count, DATE(interval_start) as dimension_id, DATE(interval_start) as dimension_name, vast_event_id as event_id FROM inventory_rv_stats_vast WHERE "+whereStr+" "+ AgetWhereDate(oStartDate, oEndDate)+ " GROUP BY dimension_id, vast_event_id,interval_start ORDER BY interval_start, vast_event_id ASC"
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
                responseObject = {'message': 'Zones Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)


def ExportExcel(request):
    #print(request.GET['period_preset'])
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="Users.xls"'
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    #adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    #column header names, you can use your own headers here
    if request.GET['method_name']=='clientsstats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='clientsdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='campaignsstats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]        
    elif request.GET['method_name']=='campaignsdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='banners':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='bannersdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]                
    #write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    #get your data, from database or from a text file...
    if request.GET['method_name']=='clientsstats':
        advstatsData = advertiserStats(request)
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'clientname'
    elif request.GET['method_name']=='clientsdailystats':
        advstatsData = advertiserDailyStats(request,request.GET['clientid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    elif request.GET['method_name']=='campaignsstats':
        camstatsData = campaignsStats(request,request.GET['clientid'])
        data = (camstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'campaignname'        
    elif request.GET['method_name']=='campaignsdailystats':
        advstatsData = campaignsDailyStats(request,None,request.GET['campaignid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    if request.GET['method_name']=='banners':
        advstatsData = bannersStats(request,None,request.GET['campaignid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'description'
    elif request.GET['method_name']=='bannersdailystats':
        advstatsData = bannersDailyStats(request,None,None,request.GET['bannerid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'        
    for my_row in rows:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row[col], font_style)
        ws.write(row_num, 1, my_row['impressions'], font_style)
        ws.write(row_num, 2, my_row['clicks'], font_style)
        ws.write(row_num, 3, (my_row['clicks']/my_row['impressions'])*100, font_style)
        ws.write(row_num, 4, '64.23', font_style)

    wb.save(response)
    return response
  


def ExportWebExcel(request):
    #print(request.GET['period_preset'])
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="Users.xls"'
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    #adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    #column header names, you can use your own headers here
    if request.GET['method_name']=='websitestats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='websitedailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='zonestats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]        
    elif request.GET['method_name']=='zonedailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='webcampaignsstats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='webcampaignsdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]                
    #write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    #get your data, from database or from a text file...
    if request.GET['method_name']=='websitestats':
        advstatsData = websiteStats(request)
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'name'
    elif request.GET['method_name']=='websitedailystats':
        advstatsData = websiteDailyStats(request,request.GET['affiliateid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    elif request.GET['method_name']=='zonestats':
        camstatsData = zoneStats(request,request.GET['affiliateid'])
        data = (camstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'zonename'        
    elif request.GET['method_name']=='zonedailystats':
        advstatsData = zoneDailyStats(request,None,request.GET['zoneid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    if request.GET['method_name']=='webcampaignsstats':
        advstatsData = webcampaignsStats(request,request.GET['affiliateid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'campaignname'
    elif request.GET['method_name']=='webcampaignsdailystats':
        advstatsData = webcampaignsDailyStats(request,None,request.GET['affiliateid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'        
    for my_row in rows:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row[col], font_style)
        ws.write(row_num, 1, my_row['impressions'], font_style)
        ws.write(row_num, 2, my_row['clicks'], font_style)
        ws.write(row_num, 3, (my_row['clicks']/my_row['impressions'])*100, font_style)
        ws.write(row_num, 4, '64.23', font_style)

    wb.save(response)
    return response  


def ExportexecutiveExcel(request):
    #print(request.GET['period_preset'])
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="Users.xls"'
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    #adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    #column header names, you can use your own headers here
    if request.GET['method_name']=='clientsstats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='clientsdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    if request.GET['method_name']=='campaignsstats':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]        
    elif request.GET['method_name']=='campaignsdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='banners':
        columns = ['Name', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]
    elif request.GET['method_name']=='bannersdailystats':
        columns = ['Day', 'Impressions', 'Clicks', 'CTR', 'Revenue', ]                
    #write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    #get your data, from database or from a text file...
    if request.GET['method_name']=='clientsstats':
        advstatsData = eadvertiserStats(request)
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'clientname'
    elif request.GET['method_name']=='clientsdailystats':
        advstatsData = eadvertiserDailyStats(request,request.GET['clientid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    if request.GET['method_name']=='campaignsstats':
        camstatsData = ecampaignsStats(request,request.GET['clientid'])
        data = (camstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        col = 'campaignname'        
    elif request.GET['method_name']=='campaignsdailystats':
        advstatsData = ecampaignsDailyStats(request,request.GET['campaignid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'
    elif request.GET['method_name']=='banners':
        advstatsData = ebannerStats(request,request.GET['campaignid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        rows = data["data"]
        print(rows)
        col = 'bannername'
    elif request.GET['method_name']=='bannersdailystats':
        advstatsData = ebannerDailyStats(request,request.GET['bannerid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        rows = row['reportData']
        col = 'day'        
    for my_row in rows:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row[col], font_style)
        ws.write(row_num, 1, my_row['impressions'], font_style)
        ws.write(row_num, 2, my_row['clicks'], font_style)
        ws.write(row_num, 3, (my_row['clicks']/my_row['impressions'])*100, font_style)
        ws.write(row_num, 4, '64.23', font_style)

    wb.save(response)
    return response
