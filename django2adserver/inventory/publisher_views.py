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
from inventory.serializers import AffiliatesSerializer
from inventory.models import Users,LoginToken
from inventory.serializers import UsersSerializer,UsersCustomizeSerializer,LoginTokenSerializer
import json
import secrets
import base64
import hashlib 
from datetime import datetime,timedelta


from django.db import connection
from inventory.helpers import generateWebZoneInvocationCode,generateHtml5ZoneInvocationCode,getLinkedAdvertrisers
from inventory.helpers import getLinkedAdvertrisers,getLinkedCampaigns,getLinkedBanners,updateAdZoneAssoc,getAssocOrderDetails,getLinkedBannersByZones



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
    zoneType 		= '';
    width 			= 0;
    height 			= 0;
    zoneid			=request.GET.get('zoneid')
    if zoneid:
        affiliateid			= request.GET.get('affiliateid')
        zoneData			= Zones.objects.get(zoneid=zoneid)
        #print(zoneData)
        if zoneData:
            zoneType = zoneData.delivery;
            width	= zoneData.width;
            height	= zoneData.height;
            
            advertiser 		   = getLinkedAdvertrisers(zoneType,width,height)
            #print(advertiser)
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
                        bannerData              = getAssocOrderDetails(bannerid)
                        #print(zoneData)
                        #print(bannerData)
                    
                    # assocData		= {
                        # 'ad_id' : bannerData.bannerid,
                        # "banner_status":bannerData.banner_status,
                        # "campaign_status":bannerData.campaign_status,
                        # "activate_time":bannerData.activate_time,
                        # "expire_time":bannerData.expire_time,
                        # 'width' : zoneData.width,
                        # 'height' :  zoneData.height,
                        # 'type' : zoneData.delivery,
                        # 'contenttype' : bannerData.contenttype,
                        # 'weight' : bannerData.banner_weight,
                        # 'block_ad' : '0',
                        # 'cap_ad' : '0',
                        # 'session_cap_ad' : '0',
                        # 'compiledlimitation' : '',
                        # 'acl_plugins' : NULL,
                        # 'alt_filename' : '',
                        # 'priority' : '0',
                        # 'priority_factor' : '1',
                        # 'to_be_delivered' : '1',
                        # 'campaign_id' : bannerData.campaignid,
                        # 'campaign_priority' : bannerData.campaign_priority,
                        # 'campaign_weight' : bannerData.campaign_weight,
                        # 'campaign_companion' : '0',
                        # 'block_campaign' : '0',
                        # 'cap_campaign' : '0',
                        # 'session_cap_campaign' : '0',
                        # 'show_capped_no_cookie' : '0',
                        # 'client_id' : bannerData.clientid,

                    # }
                    # bannerCache = 'delivery_ad_zone_' + str(zone) + '.py'
                    # f = open(deliveryCorePath + bannerCache, 'w+')
                    # jsonArr = assocData
                    # jsonString = json.dumps(jsonArr)
                    # f.write(jsonString)
                    # f.close()
                    # myFile 		= deliveryCorePath+'delivery_ad_zone_'+zoneid+'.py';
                    

    linkedBanner		= getLinkedBannersByZones(zoneid)
    responseObject.update({"linkedBanner":linkedBanner})

    responseObject12 	= {"message":"Linking Banner","data":responseObject,'status':True}
    return JsonResponse(responseObject12, safe=False, status=200,)

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
            
            clickTag = 'http://localhost/ckvast.php?zoneid=' + str(zoneId) + '&bannerid=' + str(AdId)
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidString 		= str(userId)
        whereStr 			= 'c.clientid = '+clientidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT c.clientid,clientname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE " +whereStr+ " c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id "+getWhereDate(oStartDate, oEndDate)+" GROUP BY c.clientid"
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
                responseObject = {'message': 'Advertisers Stats', 'data': result, 'status':True}
                return JsonResponse(responseObject, safe=False)	
            
            else:
                responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                return JsonResponse(responseObject, safe=False)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)

def websiteStats(request):
        if 'period_preset' in request.GET:
            oStartDate	= request.GET.get('period_start')
            oEndDate	= request.GET.get('period_end')
        else:
            oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
            oEndDate	=	datetime.today().strftime('%Y-%m-%d')
            
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:
            useridString 		= str(userId)
            whereStr = 'p.userid = '+useridString+' AND '
            with connection.cursor() as cursor:
                sql = "SELECT p.affiliateid,p.name, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue FROM inventory_zones AS z, inventory_affiliates AS p, inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+" p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id "+getWhereDate(oStartDate, oEndDate)+" GROUP BY p.affiliateid"
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        clientidString 		= str(pk)
        whereStr 			= 'm.clientid = '+clientidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT m.campaignid,m.campaignname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE  "+whereStr+" m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY m.campaignid,m.campaignname"
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
                
                clients 	= Clients.objects.get(pk=pk)
                print(clients)
                
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidString 		= str(id)
        whereStr = 'm.campaignid = '+campaignidString+' AND '
        with connection.cursor() as cursor:
            sql = "SELECT SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue,DATE(s.date_time) AS day FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+" c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY day"
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
                responseObject = {'message': 'Campaigns Stats', 'data': result, 'status':True}
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
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
                
                clients 	= Clients.objects.get(pk=pk)
                print(clients)
                
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        zoneidString 		= str(id)
        whereStr = ' s.zone_id = ' +zoneidString
        with connection.cursor() as cursor:
            sql = "SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue, DATE(s.date_time) AS day FROM inventory_rv_data_summary_ad_hourly AS s WHERE " +whereStr+ " "+getWhereDate(oStartDate, oEndDate)+"  GROUP BY day"
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
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
                
                clients 	= Clients.objects.get(pk=pk)
                print(clients)
                
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
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    if tokenStatus:
        campaignidString        = str(id)
        affiliateidString 		= str(pk)
        whereStr = 'AND p.affiliateid = ' +affiliateidString+ ' AND m.campaignid = '+campaignidString
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


                
# def zoneStats(request,pk):
# 	if 'period_preset' in request.GET:
# 		oStartDate	= request.GET.get('period_start')
# 		oEndDate	= request.GET.get('period_end')
# 	else:
# 		oStartDate	= 	datetime.today().strftime('%Y-%m-%d')
# 		oEndDate	=	datetime.today().strftime('%Y-%m-%d')	
# 	clientidString 		= str(pk)
# 	whereStr = 'p.affiliateid = '+clientidString+' AND '
# 	with connection.cursor() as cursor:
# 		cursor.execute("SELECT z.zonename,z.zoneid, SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue, z.zoneid AS zoneID, z.zonename AS zoneName FROM zones AS z,affiliates AS p, rv_data_summary_ad_hourly AS s WHERE " +whereStr+ " p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id " +getWhereDate(oStartDate, oEndDate)+ " GROUP BY z.zoneid, z.zonename")
# 		field_names = [item[0] for item in cursor.description]

# 		rawData  = cursor.fetchall()
# 		result = []
# 		if rawData:
# 			for row in rawData:
# 				objDict = {}
# 				for index, value in enumerate(row):
# 					objDict[field_names[index]] = value
# 				result.append(objDict)
            
# 			responseObject = {'message': 'Zones Stats', 'data': result, 'status':True}
# 			return JsonResponse(responseObject, safe=False)
# 		else:
# 			responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
# 			return JsonResponse(responseObject, safe=False)		
        

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
    

def advertiserDailyStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']	
    clientidString 		= str(pk)
    whereStr = 'c.clientid = '+clientidString+' AND '
    with connection.cursor() as cursor:
        cursor.execute("SELECT c.clientid,clientname,SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks,SUM(s.requests) AS requests,SUM(s.total_revenue) AS revenue FROM inventory_clients AS c,inventory_campaigns AS m,inventory_banners AS b,inventory_rv_data_summary_ad_hourly AS s WHERE "+whereStr+"c.clientid = m.clientid AND m.campaignid = b.campaignid AND b.bannerid = s.creative_id  "+getWhereDate(oStartDate, oEndDate)+" GROUP BY c.clientid")
        clientStats  = cursor.fetchone()
        if clientStats:
            data = {
                "clientid":clientStats[0],
                "clientname":clientStats[1],
                "impressions":clientStats[2],
                "clicks":clientStats[3],
                "requests":clientStats[4],
                "revenue":clientStats[5]
            }
            #print(data);
            responseObject = {'message': 'Advertisers Stats', 'data': data, 'status':True}
            return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False)


# def websiteDailyStats(request,pk):
# 	clientidString 		= str(pk)
# 	whereStr = 'c.clientid = '+clientidString+' AND '
# 	with connection.cursor() as cursor:
# 		cursor.execute("SELECT SUM(s.impressions) AS impressions, SUM(s.clicks) AS clicks, SUM(s.requests) AS requests, SUM(s.total_revenue) AS revenue FROM zones AS z, affiliates AS p, rv_data_summary_ad_hourly AS s WHERE p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id "+whereStr+" GROUP BY day")
# 		clientStats  = cursor.fetchone()
# 		if clientStats:
# 			data = {
# 				"clientid":clientStats[0],
# 				"clientname":clientStats[1],
# 				"impressions":clientStats[2],
# 				"clicks":clientStats[3],
# 				"requests":clientStats[4],
# 				"revenue":clientStats[5]
# 			}
# 			print(data);
# 			responseObject = {'message': 'Advertisers Stats', 'data': data, 'status':True}
# 			return JsonResponse(responseObject, safe=False)
# 		else:
# 			responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
# 			return JsonResponse(responseObject, safe=False)			

def websiteDailyStats(request,pk):
    if request.GET.get('period_preset'):
        getDateBYFiletr = getDate(request.GET.get('period_preset'),request)
        print(getDateBYFiletr)
        oStartDate	= getDateBYFiletr['period_start']
        oEndDate	= getDateBYFiletr['period_end']
    userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
    clientidString 		= str(pk)
    userIdString 		= str(userId)
    whereStr = ' p.affiliateid = '+clientidString+' AND p.userid = '+ userIdString + 'AND '
    #print(whereStr)
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
            responseObject = {'message': 'Affiliates Stats', 'data': finalData, 'status':True}
            return JsonResponse(responseObject, safe=False)
        else:
            responseObject = {'message': 'No Affiliates Stats Exists!', 'data': [], 'status':False}
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
            responseObject = {'message': 'Successful Logout', 'data': [], 'status':True}
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

    
def CustomAuthToken(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        string 			= data['password']
        result 			= hashlib.md5(string.encode()) 
        passord			= result.hexdigest()
        #print(passord)
        
        try:
            users = Users.objects.get(username=data['username'], password=passord)
            if users:
                token 	= secrets.token_hex(20)
                tokenData 	= {'token':token,'user_id': users.user_id,'username':users.username,'email':users.email,'firstname':users.firstname,'lastname':users.lastname}
                print(tokenData);
                serializer	 = LoginTokenSerializer(data=tokenData)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Login Successful', 'data': tokenData, 'status':True}
                    return JsonResponse(responseObject, safe=False)
        except Users.DoesNotExist:
            responseObject = {'message': 'Login UnSuccessful Username and password not matches', 'data':{}, 'status':False}
            return JsonResponse(responseObject, safe=False)




@csrf_exempt
def clients_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        
        if tokenStatus:
            if request.method == 'GET':
                clients = Clients.objects.filter(userid=userId)
                serializer = ClientsSerializer(clients, many=True)
                # print(serializer)
                responseObject = {'message': 'Advertiser Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                data.update({'userid' :userId })
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
        
def clients_detail(request, pk):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            try:
                clients = Clients.objects.get(pk=pk)
            except Clients.DoesNotExist:
                responseObject = {'message': 'Advertiser not found!!', 'data': [], 'status':False}
                return JsonResponse(responseObject,status=204)

            if request.method == 'GET':
                serializer = ClientsSerializer(clients)
                
                responseObject = {'message': 'Advertiser Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)

            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                data.update({'userid' :userId })
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
        
         




def campaigns_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                useridString 		= str(userId)
                whereStr 			= 'c.userid = '+useridString+' AND '
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM inventory_campaigns AS a, inventory_clients AS c,  inventory_users AS u WHERE " +whereStr+ " a.clientid = c.clientid"
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
                        
                        responseObject = {'message': 'Campaigns List', 'data': result, 'status':True}
                        return JsonResponse(responseObject, safe=False)	
                    
                    else:
                        responseObject = {'message': 'No Campaigns Found!', 'data': [], 'status':False}
                        return JsonResponse(responseObject, safe=False)

                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                #if(data['endSet'] == 'f'):
                #	data['expire_time']				= 
                    
                serializer = CampaignsSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    # return JsonResponse(serializer.data, status=201)
                    responseObject = {'message': 'Campaigns Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
        
        
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
                data = JSONParser().parse(request)
                serializer = CampaignsSerializer(campaigns, data=data)
                if serializer.is_valid():
                    serializer.save()
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

  
def banners_list(request):
    tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
    if tokenempChk:
        tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                banners = Banners.objects.all()
                serializer = BannersSerializer(banners, many=True)
                # return JsonResponse(serializer.data, safe=False)
                responseObject = {'message': 'Banners Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                serializer = BannersSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Banners Added successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=201)
        else:
            responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
            return JsonResponse(responseObject, safe=False,status=204)
    else:	
        responseObject = {'message': 'Token Required', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False)					
         
        
def banners_detail(request, pk):
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
                serializer = BannersSerializer(banners)
                responseObject = {'message': 'Banners Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                # return JsonResponse(serializer.data)

            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = BannersSerializer(banners, data=data)
                if serializer.is_valid():
                    serializer.save()
                    responseObject = {'message': 'Banners Updated successfully', 'data': serializer.data, 'status':True}
                    return JsonResponse(responseObject, status=200)

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
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                useridString 		= str(userId)
                whereStr 			= 'a.userid = '+useridString+' AND '
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM inventory_zones AS z, inventory_affiliates AS a WHERE " +whereStr+ " z.affiliateid = a.affiliateid"
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
                        
                        responseObject = {'message': 'Zones List', 'data': result, 'status':True}
                        return JsonResponse(responseObject, safe=False)	
                    
                    else:
                        responseObject = {'message': 'No Zones Found!', 'data': [], 'status':False}
                        return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                serializer = ZonesSerializer(data=data)                                                                                                                                                                             
                if serializer.is_valid():
                    serializer.save()
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
                print(serializer.data)
                # return JsonResponse(serializer.data)
                responseObject = {'message': 'Zones Details', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)

            elif request.method == 'PUT':
                data = JSONParser().parse(request)
                serializer = ZonesSerializer(zones, data=data)
                if serializer.is_valid():
                    serializer.save()
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
        userId              = getuserIDByToken(request.META['HTTP_AUTHORIZATION'])
        if tokenStatus:	
            if request.method == 'GET':
                affiliates = Affiliates.objects.filter(userid=userId)
                serializer = AffiliatesSerializer(affiliates, many=True)
                # return JsonResponse(serializer.data, safe=False)
                responseObject = {'message': 'Affiliates Lists', 'data': serializer.data, 'status':True}
                return JsonResponse(responseObject, safe=False)
                
            elif request.method == 'POST':
                data = JSONParser().parse(request)
                data.update({'userid' :userId })
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
                data.update({'userid' :userId })
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
# 	tokenempChk         = tokenEmpCheck(request.META['HTTP_AUTHORIZATION'])
# 	if tokenempChk:
# 		tokenStatus 		= validateToken(request.META['HTTP_AUTHORIZATION'])
# 		if tokenStatus:	
# 			# if request.method == 'GET':
# 			# 	users = Users.objects.all()
# 			# 	#print(users)
# 			# 	serializer = UsersCustomizeSerializer(users, many=True)
# 			# 	# return JsonResponse(serializer.data, safe=False)
# 			# 	responseObject = {'message': 'Users Lists', 'data': serializer.data, 'status':True}
# 			# 	return JsonResponse(responseObject, safe=False)
                
# 			if request.method == 'POST':
# 				data = JSONParser().parse(request)
# 				print(data)
# 				string 			= data['password']
# 				result 			= hashlib.md5(string.encode()) 
# 				passord			= result.hexdigest()
# 				data.update({'password' :passord })
# 				serializer = UsersSerializer(data=data)                                                                                                                                                                             
# 				if serializer.is_valid():
# 					serializer.save()
# 					responseObject = {'message': 'Users Added successfully', 'data': serializer.data, 'status':True}
# 					return JsonResponse(responseObject, status=201)
# 		else:
# 			responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
# 			return JsonResponse(responseObject, safe=False,status=204)
# 	else:	
# 		responseObject = {'message': 'Token Required', 'data': [], 'status':False}
# 		return JsonResponse(responseObject, safe=False)					
        

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
                role 			= data['role']
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
                print(data)
                try:
                    users = Users.objects.get(username=data['username'], role=int(role))
                    responseObject = {'message': 'Username Already Exist!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False,status=204)	
                except Users.DoesNotExist:
                    serializer = UsersSerializer(data=data)                                                                                                                                                                             
                    if serializer.is_valid():
                        serializer.save()
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
                string 			= data['password']
                result 			= hashlib.md5(string.encode()) 
                passord			= result.hexdigest()
                data.update({'password' :passord })
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

def home_data(request):
    #print("hhh")
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
    print(tokenStatus)
    data2={}
    users           = Users.objects.get(user_id=userId)
    data2.update({'change_passwordStatus' :0 })
    serializer = UsersSerializer(users, data=data2)
    if serializer.is_valid():
        serializer.save()
        if tokenStatus:
            userId1 		= str(userId)
            whereStr 			= 'p.userid = '+userId1+' AND '
            #whereStr 			= ' AND '
            with connection.cursor() as cursor:
                sql = "SELECT SUM(s.impressions) AS impressions,SUM(s.clicks) AS clicks, SUM(s.total_revenue) AS revenue,  DATE(s.date_time) AS day FROM inventory_zones AS z, inventory_affiliates AS p, inventory_rv_data_summary_ad_hourly AS s WHERE " +whereStr+ " p.affiliateid = z.affiliateid AND z.zoneid = s.zone_id "+getWhereDate(oStartDate, oEndDate)+ " group by day"
                print(sql)
                cursor.execute(sql)
                field_names = [item[0] for item in cursor.description]
                rawData = cursor.fetchall()
                
                result = []
                if rawData:
                    print('prince')
                    for row in rawData:
                        objDict = {}
                        for index, value in enumerate(row):
                            objDict[field_names[index]] = value
                        result.append(objDict)
                    responseObject = {'message': 'Home Stats', 'data': result, 'status':True}
                    return JsonResponse(responseObject, safe=False)	
                
                else:
                    responseObject = {'message': 'No Stats Exists!', 'data': [], 'status':False}
                    return JsonResponse(responseObject, safe=False)
            
            responseObject = {'message': 'No Stats Exists!', 'data': {}, 'status':False}
            return JsonResponse(responseObject, safe=False)
            

        responseObject = {'message': 'Invalid User', 'data': [], 'status':False}
        return JsonResponse(responseObject, safe=False,status=204)


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


def ExportPublisherExcel(request):
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
        print(request.GET['affiliateid'])
        advstatsData = websiteDailyStats(request,request.GET['affiliateid'])
        data = (advstatsData.content).decode('utf8')
        data = json.loads(data)
        row = data["data"]
        print(row)
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
        advstatsData = webcampaignsDailyStats(request,request.GET['affiliateid'],request.GET['campaignid'])
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