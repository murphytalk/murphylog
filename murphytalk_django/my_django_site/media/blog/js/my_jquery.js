/*
 do the live search
 */
function do_search(){
	var search_for = encodeURI($("#q").val());
	$("#loading").show();
	$("div#results").load("/blog/search/"+search_for+"/", /*remote CGI*/
			      function(){                     /*callback:get called while load from remote CGI finished*/
			          $("#loading").hide();
                              });
}


/*the workhorse;)*/
$(document).ready(function(){
	if($.browser.msie){       	  
	     $("input[@type='text'], input[@type='password'], textarea").focus(function(){
								           $(this).css({background:"#fcc", border:"1px solid #f00"})}).blur(
									     function(){
                       							         $(this).css({background: "transparent", border: "1px solid #ccc"})
                                                                             });
	}       
       	       
	/*called while press enter in search form 
	  1) do the live search
          2) return false to tell browser not to submit
         */
	$("#sform").submit(function(){do_search();return false;});
});
