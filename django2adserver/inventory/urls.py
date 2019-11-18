from django.urls import path
from inventory import views,advertiser_views,publisher_views,executive_views,pubexecutive_views,publisherexecutive_views,advertiserexecutive_views

urlpatterns = [
	#start of users
	path('inventory/users/', views.users_list),
	path('inventory/users/<int:pk>/', views.users_detail),
	path('api-token-auth/', views.CustomAuthToken),
	path('logout/', views.logout),
	path('inventory/users/changepassword/<int:pk>/', views.changePassword),
	path('inventory/users/forgotpassword/', views.forgotPassword),
	path('inventory/campaignstatus/<int:pk>/', views.campaignActiveInactive),
	#end of users

	#start of inventory
	
	path('inventory/home/', views.home_data),
	path('inventory/notifications/', views.notification_data),
	path('inventory/clients/', views.clients_list),
	path('inventory/clients/<int:pk>/', views.clients_detail),
	path('inventory/advertiser/<int:pk>/campaigns/', views.getAdvtAllCampaigns),
	path('inventory/campaigns/', views.campaigns_list),
	path('inventory/campaigns/<int:pk>/', views.campaigns_detail),
	path('inventory/campaigns/<int:pk>/banners/', views.getCmpsAllBanners),
	path('inventory/banners/', views.banners_list),
	path('inventory/banners/<int:pk>/', views.banners_detail),
	path('inventory/bannersupdate/<int:pk>/', views.bannersupdate),

	path('inventory/zones/', views.zones_list),
	path('inventory/zones/<int:pk>/', views.zones_detail),
	path('inventory/zonesinvocation/', views.zonesInvocation),
	path('inventory/zones-invocation-vast/', views.zonesInvocationVast),
	path('inventory/zonesinclude/', views.zonesInclude),

	path('inventory/affiliates/', views.affiliates_list),
	path('inventory/affiliates/<int:pk>/', views.affiliates_detail),
	path('inventory/affiliate/<int:pk>/zones/', views.getAffltAllZones),


	#### Delete by checkbox #####
    path('inventory/clients/advertiserdelete/', views.advertiserDelete),
    path('inventory/campaigns/campaigndelete/', views.campaignDelete),
	path('inventory/banners/bannerdelete/', views.bannerDelete),
	path('inventory/affiliates/affiliatesdelete/', views.affiliatesDelete),
	path('inventory/zones/zonesdelete/', views.zonesDelete),
	#end of inventory
	
	#start of adcampstats
	path('inventory/clientsstats/', views.advertiserStats),
	path('inventory/clientsdailystats/<int:pk>/', views.advertiserDailyStats),
	path('inventory/clients/<int:pk>/campaignsstats/', views.campaignsStats),
	path('inventory/clients/<int:pk>/campaignsdailystats/<int:id>/', views.campaignsDailyStats),
	path('inventory/clients/<int:clientid>/campaigns/<int:campaignid>/banners/', views.bannersStats),
	path('inventory/clients/<int:clientid>/campaigns/<int:campaignid>/bannersdailystats/<int:bannerid>/', views.bannersDailyStats),
	#end of adcampstats

	#excel export
	path('inventory/exportclientexcel/', views.ExportExcel),
	path('inventory/exportwebexcel/', views.ExportWebExcel),
	# path('inventory/clientsstats/advertiserexport/', views.advertiserStatsExport),
	# path('inventory/clientsstats/advertisdailyerexport/<int:pk>/', views.advertiserDailyStatsExport),

	#end export

	#start of video adcampstats
	path('inventory/vaststats/clientsvaststats/<int:pk>/', views.advertiserVastStats),
	path('inventory/vaststats/clients/<int:pk>/campaignsvaststats/<int:id>/', views.campaignsVastStats),
	path('inventory/vaststats/<int:clientid>/campaigns/<int:campaignid>/bannersvaststats/<int:bannerid>/', views.bannersVastStats),
	#end of video adcampstats
	path('inventory/campaigns/linkedzones/<int:pk>/', views.linkedZones),
	
	#start of webzonestats
	path('inventory/websitestats/', views.websiteStats),
	path('inventory/websitedailystats/<int:pk>/', views.websiteDailyStats),
	path('inventory/websitestats/<int:pk>/zonestats/', views.zoneStats),
	path('inventory/websitestats/<int:pk>/zonedailystats/<int:id>/', views.zoneDailyStats),
	path('inventory/websitestats/<int:pk>/webcampaignsstats/', views.webcampaignsStats),
	path('inventory/websitestats/<int:pk>/webcampaignsdailystats/<int:id>/', views.webcampaignsDailyStats),
	#end of webzonestats
	
	#excel export
	path('inventory/exportwebexcel/', views.ExportWebExcel),


	#end export	

	#start of video webzonestats

	path('inventory/vaststats/websitevaststats/<int:pk>/', views.websiteVastStats),
	path('inventory/vaststats/websitevaststats/<int:pk>/zonevaststats/<int:id>/', views.zoneVastStats),

	#end of video webzonestats




	#start of executive
	path('inventory/executive/users/<int:clientid>/', views.adusers_list),
	path('inventory/executive/notifications/', views.anotification_data),
	path('inventory/executive/users/edit/<int:pk>/', views.adusers_detail),
	path('inventory/executive/bannersupdate/<int:pk>/', executive_views.bannersupdate),
	path('inventory/executive/home/', executive_views.home_data),

	path('inventory/executive/clients/', executive_views.clients_list),
	path('inventory/executive/clients/<int:pk>/', executive_views.clients_detail),	
	path('inventory/executive/<int:clientid>/campaigns/', executive_views.campaigns_list),
	path('inventory/executive/campaigns/<int:campaignid>/banners/', executive_views.getCmpsAllBanners),
    path('inventory/executive/<int:clientid>/campaigns/', executive_views.campaigns_list),
	
#reports
    path('inventory/executive/stats/<int:clientid>/campaignsstats/', views.ecampaignsStats),
	path('inventory/executive/stats/campaignsdailystats/<int:campaignid>/', views.ecampaignsDailyStats),
	path('inventory/executive/stats/<int:campaignid>/bannerstats/', views.ebannerStats),
	path('inventory/executive/stats/bannerdailystats/<int:bannerid>/',views.ebannerDailyStats),

#export
	path('inventory/executive/exportexecutiveexcel/', views.ExportexecutiveExcel),


	path('inventory/advertiser/advertiseradmin/', views.publisheradmin_list),
	path('inventory/advertiser/advertiseradmin/<int:pk>/', views.publisheradmin_detail),


	#end of executive
    
	#admin pubexecutive

	path('inventory/pubexecutive/users/<int:affiliateid>/', views.pusers_list),
	path('inventory/pubexecutive/users/edit/<int:pk>/', views.pusers_detail),
	path('inventory/pubexecutive/notifications/', views.pnotification_data),

	path('inventory/pubexecutive/linkedzones/<int:campaignid>/', pubexecutive_views.linkedZones),
	path('inventory/pubexecutive/affiliates/', pubexecutive_views.affiliates_list),
	path('inventory/pubexecutive/affiliates/<int:pk>/', pubexecutive_views.affiliates_detail),
	path('inventory/pubexecutive/home/', pubexecutive_views.home_data),   
	path('inventory/pubexecutive/<int:affiliateid>/zones/', pubexecutive_views.zones_list),
	path('inventory/pubexecutive/zones/<int:pk>/', pubexecutive_views.zones_detail),
	path('inventory/pubexecutive/<int:pk>/zonestats/', pubexecutive_views.zoneStats),
	path('inventory/pubexecutive/<int:pk>/zonedailystats/<int:id>/', pubexecutive_views.zoneDailyStats),
#export
	path('inventory/pubexecutive/exportpubecutiveexcel/', pubexecutive_views.ExportPubexecutiveExcel),

	path('inventory/publisher/publisheradmin/', views.publisheradmin_list),
	path('inventory/publisher/publisheradmin/<int:pk>/', views.publisheradmin_detail),
	
    #end admin pubexecutive


	#publisher login as publisher executive

	path('inventory/publisher/pubexecutive/users/<int:affiliateid>/', publisherexecutive_views.pusers_list),
	path('inventory/publisher/pubexecutive/users/edit/<int:pk>/', publisherexecutive_views.pusers_detail),

	path('inventory/publisher/pubexecutive/home/', publisherexecutive_views.home_data),   
	path('inventory/publisher/pubexecutive/<int:affiliateid>/zones/', publisherexecutive_views.zones_list),
	path('inventory/publisher/pubexecutive/zones/<int:pk>/', publisherexecutive_views.zones_detail),
	path('inventory/publisher/pubexecutive/<int:pk>/zonestats/', publisherexecutive_views.zoneStats),
	path('inventory/publisher/pubexecutive/<int:pk>/zonedailystats/<int:id>/', publisherexecutive_views.zoneDailyStats),
	
	
    #end publisher login publisher executive


	#advertiser login as advertiser executive
	path('inventory/advertiser/executive/users/<int:clientid>/', views.adusers_list),
	path('inventory/advertiser/executive/users/edit/<int:pk>/', views.adusers_detail),

	path('inventory/advertiser/executive/home/', executive_views.home_data),
	path('inventory/advertiser/executive/<int:clientid>/campaigns/', executive_views.campaigns_list),
	path('inventory/advertiser/executive/campaigns/<int:campaignid>/banners/', executive_views.getCmpsAllBanners),
    path('inventory/advertiser/executive/<int:clientid>/campaigns/', executive_views.campaigns_list),
	

    path('inventory/advertiser/executive/stats/<int:clientid>/campaignsstats/', views.ecampaignsStats),
	path('inventory/advertiser/executive/stats/campaignsdailystats/<int:campaignid>/', views.ecampaignsDailyStats),
	path('inventory/advertiser/executive/stats/<int:campaignid>/bannerstats/', views.ebannerStats),
	path('inventory/advertiser/executive/stats/bannerdailystats/<int:bannerid>/',views.ebannerDailyStats),
	#end advertiser login as advertiser executive 





	################### FOR ADVERTISER START #################
    path('inventory/advertiser/home/', advertiser_views.home_data),
	path('inventory/advertiser/notifications/', advertiser_views.notification_data),
	path('inventory/advertiser/users/', advertiser_views.users_list),
	path('inventory/advertiser/users/<int:pk>/', advertiser_views.users_detail),

	path('inventory/advertiser/clients/', advertiser_views.clients_list),
	path('inventory/advertiser/clients/<int:pk>/', advertiser_views.clients_detail),

	path('inventory/advertiser/campaigns/', advertiser_views.campaigns_list),
	path('inventory/advertiser/campaigns/<int:pk>/', advertiser_views.campaigns_detail),

	path('inventory/advertiser/banners/', advertiser_views.banners_list),
	path('inventory/advertiser/banners/<int:pk>/', advertiser_views.banners_detail),

	path('inventory/advertiser/advertiser/<int:pk>/campaigns/', advertiser_views.getAdvtAllCampaigns),
	path('inventory/advertiser/campaigns/<int:pk>/banners/', advertiser_views.getCmpsAllBanners),

	### export excel 
	path('inventory/advertiser/exportadvertserexcel/', advertiser_views.ExportAdvertiserExcel),

#### Resports

	path('inventory/advertiser/clientsstats/', advertiser_views.advertiserStats),
	path('inventory/advertiser/clientsdailystats/<int:pk>/', advertiser_views.advertiserDailyStats),

	path('inventory/advertiser/clients/<int:pk>/campaignsstats/', advertiser_views.campaignsStats),
	path('inventory/advertiser/clients/<int:pk>/campaignsdailystats/<int:id>/', advertiser_views.campaignsDailyStats),

	path('inventory/advertiser/clients/<int:clientid>/campaigns/<int:campaignid>/banners/', advertiser_views.bannersStats),
	path('inventory/advertiser/clients/<int:clientid>/campaigns/<int:campaignid>/banners/<int:bannerid>/', advertiser_views.bannersDailyStats),


############### FOR ADVERTISER END   ##############


################### FOR PUBLISHER START #################
    path('inventory/publisher/home/', publisher_views.home_data),
	path('inventory/publisher/notifications/', publisher_views.notification_data),
	path('inventory/publisher/users/', publisher_views.users_list),
	path('inventory/publisher/users/<int:pk>/', publisher_views.users_detail),

	path('inventory/publisher/affiliates/', publisher_views.affiliates_list),
	path('inventory/publisher/affiliates/<int:pk>/', publisher_views.affiliates_detail),
	path('inventory/publisher/zonesinclude/', publisher_views.zonesInclude),
	path('inventory/publisher/zonesinvocation/', publisher_views.zonesInvocation),

	path('inventory/publisher/zones/', publisher_views.zones_list),
	path('inventory/publisher/zones/<int:pk>/', publisher_views.zones_detail),

	

#### Resports
   
   	path('inventory/publisher/websitestats/', publisher_views.websiteStats),
	path('inventory/publisher/websitedailystats/<int:pk>/', publisher_views.websiteDailyStats),
	path('inventory/publisher/websitestats/<int:pk>/zonestats/', publisher_views.zoneStats),
	path('inventory/publisher/websitestats/<int:pk>/zonedailystats/<int:id>/', publisher_views.zoneDailyStats),

	path('inventory/publisher/websitestats/<int:pk>/webcampaignsstats/', publisher_views.webcampaignsStats),
	path('inventory/publisher/websitestats/<int:pk>/webcampaignsdailystats/<int:id>/', publisher_views.webcampaignsDailyStats),

	path('inventory/publisher/affiliate/<int:pk>/zones/', publisher_views.getAffltAllZones),
	### export excel 
	path('inventory/publisher/exportpublisherexcel/', publisher_views.ExportPublisherExcel),

############### FOR PUBLISHER END   ##############


    # path('inventory/inventory/<int:pk>/', views.user_login),
]
