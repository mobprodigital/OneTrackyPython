import time
from datetime import datetime,timedelta
import os
import sys
import hashlib
from random import randint



def checkCampaignStatus(bannerData):
	if(bannerData):
		result          = True;
		activationTime  = bannerData['activate_time'];
		activationTime	= activationTime+" 00:00:00"
		activationTimeObject = datetime.strptime(activationTime,'%Y-%m-%d %H:%M:%S')

	
		expirationTime  		= bannerData['expire_time'];
		expirationTime			= expirationTime+" 23:59:59"
		#print(bannerData)
		expirationTimeObject  	= datetime.strptime(expirationTime,'%Y-%m-%d %H:%M:%S')
		
		now 							= datetime.now();
		currDateTimeString				= now.strftime('%Y-%m-%d %H:%M:%S');
		currDateTimeObject				= datetime.strptime(currDateTimeString,'%Y-%m-%d %H:%M:%S')
		
		#print(expirationTimeObject)
		#print(activationTimeObject)
		#print(currDateTimeObject)

		
		campaignStatus  = bannerData['campaign_status'];
		bannerStatus    = bannerData['banner_status'];
		
		deliveredImpr	= 100#bannerData['deliveredImpr'];
		todayDeliveredImpr = 1000;
		campaignTotalLimit          	= bannerData['views'];
		
		
		
		if(campaignStatus != 0):
			#print( 'campaignStatus True')
			
			if(currDateTimeObject >  activationTimeObject):
				#print( 'activationTimestamp True')
				if((not expirationTimeObject) or  (currDateTimeObject <  expirationTimeObject)):
					#print( 'expirationTimestamp True')

					if(checkCampaignTotalLimit(campaignTotalLimit, deliveredImpr)):
						#print( 'checkCampaignTotalLimit True')
						
						if(checkCampaignCappign(bannerData)):
							#print( 'checkCampaignCappign True')
						
							if(bannerStatus == 0):
								result	= True;
							else:
								result = False;
						else:
							return False;
						
					else:
						return False;
				else:
					result	= False;
			else:
				result	= False
		else:
			result	= False;
		return result;
	else:
		return True;
	
	
	
	
	
# def checkCampaignCappign(bannerData):
	# cookies				= os.environ['HTTP_COOKIE'].split(';')
	# for cookie in cookies:
		# (key, value ) = cookie.split('=')
		# key 	= key.strip()
		# if key == "JMMID":
			# JMMID = value.strip()
		# if key == "JMMCAP":
			# JMMCAP = value.strip()
	


def checkCampaignCappign(bannerData):
	JMMCAP	= ''
	JMMID	= ''
	cappingAmount 		= bannerData['capping_amount']
	
	if "HTTP_COOKIE" in os.environ:
		cookies				= os.environ['HTTP_COOKIE'].split(';')
		for cookie in cookies:
			(key, value ) = cookie.split('=')
			key 	= key.strip()
			if key == "JMMID":
				JMMID = value.strip()
			if key == "JMMCAP":
				JMMCAP = value.strip()
		
	# print(JMMID)
	# print(JMMCAP)
	# print(cappingAmount)
	
			
	if(cappingAmount != 0):
		cappingPeriod  = getTimeStamp(bannerData['capping_period_value'],bannerData['capping_period_type']);
		expires 		= datetime.utcnow() + timedelta(seconds=cappingPeriod) # expires in 30 days
		expireTime		= expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
		domain 		   = os.environ['HTTP_HOST'] if os.environ['HTTP_HOST'] != 'localhost' else False;
		if(not JMMID):
			#print("set")
			
			cbString 				= hashlib.md5(str(randint(100, 999)).encode())
			cb						= cbString.hexdigest()
			uniqueViewerId			= cb[0:16]
			now = datetime.now()
			timestamp = datetime.timestamp(now)
			print ("Set-Cookie:JMMID ="+uniqueViewerId)
			#print ("Set-Cookie:Expires ="+str(timestamp) + str(cappingPeriod))
			print ("Set-Cookie:Expires ="+expireTime)

			print ("Set-Cookie:Domain ="+str(domain))
			print ("Set-Cookie:Path =/")
			if(JMMCAP):
				print ("Set-Cookie:JMMCAP ="+JMMCAP)
				#print ("Set-Cookie:Expires ="+str(timestamp-cappingPeriod))
				print ("Set-Cookie:Expires ="+expireTime)

				print ("Set-Cookie:Domain ="+str(domain))
				print ("Set-Cookie:Path =/")
			
			return True;
		else:
			#print("unset")
			now = datetime.now()
			timestamp = datetime.timestamp(now)
			if(JMMID):
				if(not JMMCAP):
					print ("Set-Cookie:JMMCAP =1")
					#print ("Set-Cookie:Expires ="+str(timestamp+cappingPeriod))
					print ("Set-Cookie:Expires ="+expireTime)

					print ("Set-Cookie:Domain ="+str(domain))
					print ("Set-Cookie:Path =/")
					return True;
				else:
					cCap = cappingAmount;
					
					if(int(JMMCAP) <= cCap-2):
						cVal			= int(JMMCAP);
						newCVal			= cVal + 1;
						domain 			= os.environ['HTTP_HOST'] if os.environ['HTTP_HOST'] != 'localhost' else False;
						print ("Set-Cookie:JMMCAP ="+str(newCVal))
						#print ("Set-Cookie:Expires ="+str(timestamp+cappingPeriod))
						print ("Set-Cookie:Expires ="+expireTime)

						print ("Set-Cookie:Domain ="+str(domain))
						print ("Set-Cookie:Path =/")
						return True;
			
					else:
						return False;
	else:
		return True


def getTimeStamp(capping_period_value, capping_period_type):
	switcher	= {
		'hours':3600,
		'days':86400,
		'months':2520000,
		'years':919800000
	}
	#print(switcher.get(capping_period_type))
	return switcher.get(capping_period_type)*capping_period_value















	
def checkCampaignTotalLimit(campaignTotalLimit, totalDelivered):
	# if(campaignTotalLimit != -1):
		# if(campaignTotalLimit > totalDelivered):
			# return True;
		# else:
			# return False;
	# else:
		# return True;
	return True
	
def checkCampaignDailyLimit(campaignDailyLimit, todayDelivered):
	return True
	# print ('Set-Cookie: lastvisit=' + str(time.time()));
	# print ("Set-Cookie:UserID = XYZ")
	# print ("Set-Cookie:Password = XYZ123")
	# print ("Set-Cookie:Expires = Tuesday, 31-Dec-2019 23:12:40 GMT")
	#print ("Set-Cookie:Domain = www.tutorialspoint.com")
	#print ("Set-Cookie:Path = /perl")



