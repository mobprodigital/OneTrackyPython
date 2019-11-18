<?php
	include_once $_SERVER['DOCUMENT_ROOT']."/adserver/delivery/config/delivery_config.php";
	function rendervideoad(){
		if(isset($_GET['zoneid'])){
			$now 					= time();
			$zoneid					= $_GET['zoneid'];
			$ip						= $_GET['domain'];
			$dfpClickUrl			= '';
			$protocol				= '';
			$protocol 				= $_SERVER['SERVER_PROTOCOL'];
			if(isset($_GET['adurl'])){
				$Original_url		= $_SERVER['QUERY_STRING'];
				$first_index 		= stripos($Original_url, "&click");
				$first_string 		= substr($Original_url, $first_index);
				$second_index 		= stripos($first_string, "&ord=");
				$dfpClickUrl 		= substr($first_string, strlen("&click")+1,$second_index-strlen("&ord=")-2);
			}
			
			$clientIP				= $_SERVER['REMOTE_ADDR'];
			//$this->User_Model->video_adrequest($ip, $clientIP, $bannerid);
			//$target_dir 	= $_SERVER['DOCUMENT_ROOT']."/report/adserver/assets/banners/";
			$adZoneAssocFile	= $GLOBALS['cachePath']."delivery_ad_zone_".$zoneid.".php";
			$adZoneAssocData	= json_decode(file_get_contents($adZoneAssocFile), true);

			if((!empty($adZoneAssocData))){
				$adId					= $adZoneAssocData['ad_id'];
				$my_file				= $GLOBALS['cachePath']."delivery_ad_".$adId.".php";
					
				$completeArr 			= json_decode(file_get_contents($my_file), true);
				$bannerdata				= $completeArr[0];
				$vastdata				= $completeArr[1];
				
				//echo '<pre>';print_r($bannerdata);print_r($vastdata);die;

				
				$result		= true;
				/*$row['acl_plugins']			= $bannerdata['acl_plugins'];
				
				//echo '<pre>';print_r($bannerdata['acl_plugins']);die;
				
				 if(strlen($row['acl_plugins'])) {
					include_once "/home/crickbooks/public_html/delivery//limitations/validate.php";
					$acl_plugins = explode('and', $bannerdata['compiled_Limit']);
					foreach ($acl_plugins as $acl_plugin) {
						@eval('$result = (' . $acl_plugin . ');');

					}
				} */
				
				if($result){
					$vastdata['autoplay']	= 0;
					$data['vidcontent1']	= $GLOBALS['contentPath']."swach bharat.mp4";
					$data['source']			= $GLOBALS['contentPath']."swach bharat.mp4";
					//echo '<pre>';print_r($bannerdata);print_r($vastdata);die;

					
					$campaignId				= 12;
					$campaignStatus			= 'active';
					$renderdata				= adRenderVideo($bannerdata, $vastdata, $data['vidcontent1'], $data['source'],$zoneid, $protocol,$dfpClickUrl, $ip);
				}else{
					$renderdata	= "";
					
				}
				echo MAX_javascriptToHTML($renderdata, 'MS_'.substr(md5(uniqid('', 1)), 0, 8));
			}
		}
	}
	
	
	function MAX_javascriptToHTML($string, $varName, $output = true, $localScope = true){
		$jsLines = array();
		$search[] = "\\"; $replace[] = "\\\\";
		$search[] = "\r"; $replace[] = '';
		$search[] = '"'; $replace[] = '\"';
		$search[] = "'"; $replace[] = "\\'";
		$search[] = '<'; $replace[] = '<"+"';
		$string 		= str_replace($search, $replace, $string);
		$lines 			= explode("\n", $string);
		foreach ($lines AS $line) {
			if(trim($line) != '') {
				$jsLines[] = $varName . ' += "' . trim($line) . '\n";';
			}
		}
		$buffer = (($localScope) ? 'var ' : '') . $varName ." = '';\n";
		$buffer .= implode("\n", $jsLines);
		if ($output == true) {
			$buffer .= "\ndocument.write({$varName});\n";
		}
		return $buffer;
	}


		function adRenderVideo($banner, $vastdata, $vidcontent1, $source, $zoneid=null,$protocol=null,$dfpClickUrl, $ip=null,$iframe=null){
		//echo '<pre>';print_r($vastdata);die;
		$src		= $GLOBALS['deliveryPath'];
		$rand		= substr(md5(uniqid(time(), true)), 0, 10);

		if($protocol == 'HTTP/1.1' || $protocol == 'HTTP/1.0'){
			$src	= str_replace('https','http',$src);
		}
		if($banner['ext_bannertype'] == 'create_video'){
			if(isset($vastdata['vast_video_outgoing_filename']) && $vastdata['vast_video_outgoing_filename'] != ""){
				$videourl = $GLOBALS['videoBannerPath'].$vastdata['vast_video_outgoing_filename'];
			}else{
				$videourl = 'no_ad';
			}
		}else{
			$videourl	= $vastdata['vast_video_outgoing_filename'];
		}
		
		
		if(isset($vastdata['skip'])){
		
		if($vastdata['skip']=='1' ){
			$skipOption	= 'true';
			if($vastdata['skip_time']	!='0' ){ 
				$skipTime	= $vastdata['skip_time'];
			}else{
				$skipTime	= 0;
			}			
		}else{
			$skipTime	= 0;
			$skipOption	= 'false';
		}
		}else{
			$skipTime	= 0;
			$skipOption	= 'false';
		}
		
		
		
		
		if(isset($vastdata['mute'])){
			if($vastdata['mute']=='0'){
				$mute		='false';
			}else{
				$mute		='true';
			}
		}else{
			$mute		='false';
		}
		
		if($vastdata['autoplay'] =='0'){
			$autoplay	= 'false';
		}else{
			$autoplay	= 'true';
		}
		
		if($vastdata['vast_video_width']==0){
			$width		= 500;
		}else{
			$width		= $vastdata['vast_video_width'];
		}
		
		if($vastdata['vast_video_height']==0){
			$height		= 400; 
		}else{
			$height		= $vastdata['vast_video_height'];
		}
		
		if(isset($vastdata['start_pixel'])){
			$startpixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['start_pixel']."';x.width='1';x.height='1';";
		}else{
			$startpixel	= "";
		}
		
		if(isset($vastdata['end_pixel'])){
			$endpixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['end_pixel']."';x.width='1';x.height='1';";
		}else{
			$endpixel	= "";
			
		} 
		if(isset($vastdata['mid_pixel'])){
			$midpixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['mid_pixel']."';x.width='1';x.height='1';";
		}else{
			$midpixel	= "";
			
		}
		
		if(isset($vastdata['quater_pixel'])){
			$quaterpixel	= "var x 	= document.createElement('img');
			x.src			= '".$vastdata['quater_pixel']."';x.width='1';x.height='1';";
		}else{
			$quaterpixel	= "";
		}
		
		if(isset($vastdata['third_quater_pixel'])){
			$thirdquaterpixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['third_quater_pixel']."';x.width='1';x.height='1';";
		}else{
			$thirdquaterpixel	= "";
		}
		
		if(isset($vastdata['mute_pixel'])){
			$mutepixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['mute_pixel']."';x.width='1';x.height='1';";
		}else{
			$mutepixel	= "";
		}
		
		if(isset($vastdata['pause_pixel'])){
			$pausepixel	= "var x 	= document.createElement('img');
			x.src		= '".$vastdata['pause_pixel']."';x.width='1';x.height='1';";
		}else{
			$pausepixel	= "";
		}
		
		if(isset($banner['url']) && $banner['url']){
			if($dfpClickUrl){
				$clickurl	= $dfpClickUrl;
			}else{
				$clickurl					= $src.'core/ckvast.php?bannerid='.$vastdata['banner_id'].'&zoneid='.$zoneid.'&cb='.$rand;
			}
		}else{
			//$lp						= "https://mediaconversion.com/";
			//$clickurl					= base_url().'users'.'/adtrack?bannerid='.$banner['bannerid;
			$clickurl					= '';
			$clickurl					= $src.'core/ckvast.php?bannerid='.$vastdata['banner_id'].'&zoneid='.$zoneid.'&cb='.$rand;
		}
		
		if($vidcontent1){
			//$contentVid	= base_url()."assets/content/videos/".$vidcontent1;
			$contentVid		= $src."assets/content/most-expensive-things-in-the-world.mp4";
		}else{
			$contentVid		= $src."assets/content/most-expensive-things-in-the-world.mp4";
		}
		
		
		
		
		$player		= "";
		
		
		if($iframe){
			$player		.=			"<script src='".$src."assets/js/jquery.js'></script>";

		}
		if($ip == 'partner.googleadservices.com' || 1){
			$player		.=			"<script src='".$src."assets/js/jquery.js'></script>";
 		}
		$player		.=			"<script src='".$src."assets/js/mediaelement-and-player.min.js'></script>";
		$player		.=			"<link rel='stylesheet' href='".$src."assets/css/mediaelementplayer.min.css'/>";

		$autoPlayParam	= '';
		if($mute	==	'true'){
			$autoPlayParam = ' muted ';
			//$autoPlayParam	= 'controls autoplay loop muted playsinline';
			$autoPlayParam="controls autoplay muted playsinline";
				
		}else{
			
			$autoPlayParam = 'onloadstart="this.volume=0.1"';
			$autoPlayParam = ' controls autoplay muted playsinline';
		}
	
		
		
		
		$player		.=			"<script>";
		$player		.=			"
		
								var unmuteSound			= '".$mute."';
								var source1				= '".$source."';
								var playingName='ad';
								var adDuration=1;
								var counter = ".$skipTime.";
								var displaySkipBtn	= '".$skipOption."';
								var contentSource='".$contentVid."';
								var landingPageUrl='".$clickurl."';
								var start	='false';";
								
		$player		.=			"</script>";

								
		
		$player		.=			"<style>
		
		/* @media only screen and (min-width:1365px){
			#mep_0{height: 415px !important;}
		} */
		
		 
		
		
		
		#closeDiv{
			z-index: 99999;
			position: relative;
			float: right;
			padding: 25px;
			cursor:pointer;
		}
		
		#skipBtn { background-color: rgba(0, 0, 0, .5); bottom: 30%; color: #fff; cursor: pointer; height: 30px; line-height: 30px; position: absolute;right:0; text-align: center; width: 100px;font-family:verdana;margin-bottom:-80px;top:0;}
										#mask {position: absolute; width:100%;width: 100%;z-index: 9999999;}
										#player1 {width: 100% !important;-moz-width: 100% !important;
											padding: 0 1%;
											box-sizing: border-box;
											
										}</style>";
		$player		.= "<div style='position:relative;width:100%;background:#000;padding:41px 0;'>
						<video ".$autoPlayParam." width='100%' height='100%'  onclick='window.open(landingPageUrl)' src='".$videourl."' type='video/mp4' id='player1' controls preload='no' ></video>
						<div id='skipBtn'></div>
						<div id='disableSlider'></div>
						</div>";
		$player		.="<script type='text/javascript'>
				
			jQuery('#player1').mediaelementplayer({
				success: function(player, node) {
					jQuery('#' + node.id + '-mode').html('mode: ' + player.pluginType);
				}
			});
			
			if(displaySkipBtn=='true'){
			   jQuery('#skipBtn').css('display','block');
			}else{
			   jQuery('#skipBtn').css('display','none');
			}

			

			new MediaElement('player1', {
	
				success: function (mediaElement, domObject) { 
				
				  if(playingName=='ad'){
			jQuery('.mejs-mediaelement').css('cursor','pointer');
			jQuery('.mejs-button.mejs-playpause-button.mejs-play').find('button').attr('title','Pause').css('display','none');
			jQuery('.mejs-time-rail').prepend('<div id=mask></div>');
		 }
				 
				if(jQuery('.mejs-controls').css('display')=='block'){
					
				}
				
				
				 
				mediaElement.addEventListener('ended', function(e) {
				  mediaElement.setSrc(contentSource);
				  mediaElement.play();
				  playingName='content';
				  
				  if(playingName=='content'){
					landingPageUrl = '';
					jQuery('.mejs-mediaelement').css('cursor','default');

					jQuery('.mejs-button.mejs-playpause-button.mejs-play').find('button').attr('title','Pause').css('display','block');
					jQuery('#disableSlider').css('display', 'none');
					
				  }
				  document.getElementById('skipBtn').style.display = 'none';
				 
				}, false);
				
				
				 mediaElement.addEventListener('loadeddata', function(e) {
				}, false);
				
				
				var link 	= document.getElementById('skipBtn');
				var host	= window.location.hostname;


				link.onclick = function () { mediaElement.setSrc(contentSource);
				jQuery('.mejs-button.mejs-playpause-button.mejs-play').find('button').attr('title','Pause').css('display','block');
				
				jQuery('#disableSlider').css('display', 'none');
				
				mediaElement.play();

				adDuration		=0;
				document.getElementById('skipBtn').style.display = 'none';
				playingName		='content';
			
				};
				
				 mediaElement.addEventListener('timeupdate', function(e) {
				   if(playingName=='ad'){
					   
				   
				  var durationBrake = Math.round(Math.round(mediaElement.duration)/4);
				  var duration		= durationBrake;
				  var event			= '';
				  
				  if(Math.round(mediaElement.currentTime)== 1&&start == 'false'){
					  ".$startpixel."
						eventname	= 'start';
						var rand 	= Math.floor(Math.random()*99999999999);
						var x 		= document.createElement('img');
						x.src		='".$src."core/lgvast.php?src='+host+'&event='+eventname+'&time='+duration+'&bannerid='+".$vastdata['banner_id']."+'&zoneid='+".$zoneid."+'&r='+rand;x.width='1';x.height='1';
					
						
						start ='true';
				  }
				  
				  if(Math.round(mediaElement.currentTime)==durationBrake && adDuration==1){
					  	".$quaterpixel."
						eventname	= 'firstquartile';
						var rand 	= Math.floor(Math.random()*99999999999);
						var x 		= document.createElement('img');
						x.src		='".$src."core/lgvast.php?src='+host+'&event='+eventname+'&time='+duration+'&bannerid='+".$vastdata['banner_id']."+'&zoneid='+".$zoneid."+'&r='+rand;x.width='1';x.height='1';
					
				
				  adDuration=2;
				  }
				  
				  if(Math.round(mediaElement.currentTime)==durationBrake*2&&adDuration==2){
				 
				  ".$midpixel."
					eventname		= 'midpoint';	
					var rand 	= Math.floor(Math.random()*99999999999);
					var x 		= document.createElement('img');
					x.src		='".$src."core/lgvast.php?src='+host+'&event='+eventname+'&time='+duration+'&bannerid='+".$vastdata['banner_id']."+'&zoneid='+".$zoneid."+'&r='+rand;x.width='1';x.height='1';
					
					adDuration=3;
				  }
				  
				   if(Math.round(mediaElement.currentTime)==durationBrake*3&&adDuration==3){
				
				  	".$thirdquaterpixel."
						eventname		= 'thirdquartile';	
						var rand 	= Math.floor(Math.random()*99999999999);
						var x 		= document.createElement('img');
						x.src		='".$src."core/lgvast.php?src='+host+'&event='+eventname+'&time='+duration+'&bannerid='+".$vastdata['banner_id']."+'&zoneid='+".$zoneid."+'&r='+rand;x.width='1';x.height='1';
					
				  adDuration=4;
				  }
				  
				   if(Math.round(mediaElement.currentTime)==Math.round(mediaElement.duration)&&adDuration==4){
				 
				  adDuration=0;
				  	".$endpixel."
						
						eventname		= 'complete';	
						var rand 	= Math.floor(Math.random()*99999999999);
						var x 		= document.createElement('img');
						x.src		='".$src."core/lgvast.php?src='+host+'&event='+eventname+'&time='+duration+'&bannerid='+".$vastdata['banner_id']."+'&zoneid='+".$zoneid."+'&r='+rand;x.width='1';x.height='1';
					
				  playingName='content';
				  }
				  
				  }
				  
				}, false);
				
				var interval = setInterval(function() {
					if(Math.round(mediaElement.currentTime)>0){
						if(counter!=0){
							counter--;
							document.getElementById('skipBtn').onclick = null;
						}
						
						if (counter == 0) {
							clearInterval(interval);
						}
					
					document.getElementById('skipBtn').innerHTML = 'Ad 00:0' + counter;
					if(counter==0){
						document.getElementById('skipBtn').innerHTML = 'Skip Ad';
						jQuery('#skipBtn').click(function(){
							landingPageUrl = '';
							jQuery('.mejs-mediaelement').css('cursor','default');
							
							playingName='content';
							if(playingName=='content'){
								jQuery('.mejs-button.mejs-playpause-button.mejs-play').find('button').attr('title','Pause').css('display','block');
								jQuery('#disableSlider').css('display', 'none');
							}
							if(document.getElementById('skipBtn').innerHTML==='Skip Ad'){
								mediaElement.setSrc(contentSource);
								mediaElement.play();
								jQuery(this).hide();
								jQuery('.mejs-controls.mejs-offscreen').find('button').attr('title','Pause').css('display','block');
								document.getElementById('player1').onclick = null;
								jQuery('#disableSlider').css('display', 'none');
							}
						});

					}				}}, 1000);
				mediaElement.play();
			},
			error: function () { 
			 
			}
	});

</script>";
$player	.="<img src='".$src."core/lgimpr.php?bannerid=".$vastdata['banner_id']."&zoneid=".$zoneid."&cb=".$rand."' width='0' height='0' alt='' style='width: 0px; height: 0px;'>";

if(isset($vastdata['impression_pixel'])){
	$buster		= $rand;
	$vastdata['impression_pixel'] = str_replace("{cache}","$buster",$vastdata['impression_pixel']);
	$player	.="<img src='".$vastdata['impression_pixel']."' width='1' height='1' alt='' style='width: 0px; height: 0px;'>";
}
if(isset($vastdata['vast_thirdparty_impression'])){
	$buster		= $rand;
	$vastdata['vast_thirdparty_impression'] = str_replace("{cache}","$buster",$vastdata['vast_thirdparty_impression']);
	
	$player	.="<img src='".$vastdata['vast_thirdparty_impression']."' width='1' height='1' alt='' style='width: 0px; height: 0px;'>";

}
return $player;
 

	
}


rendervideoad();
		
?>