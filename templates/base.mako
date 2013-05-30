## -*- coding: utf-8 -*-
<%doc>
  context used by this template
  =============================

  entries            list of Entry objects
  user_url           URL to user login or logoff
  user               current logged in user
  tag                tag name. Used only when the view is filtered by tag
  tagobj             Tag object retrieved by using normal=tag
  is_view            True: no in edit mode;False : editing an entry
  archives           ([archive objs],total count)
  tag_clould_list    list of [tag normal name,tag name,entries count,font size]
  old_page_bkmk      bookmark to pages older than current top entry
  new_page_bkmk      bookmark to pages newer than current top entry

</%doc>

## ==== body begins ======
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <link rel="shortcut icon" href="/static/img/favicon.ico" />
  <title>Murphytalk's Weblog</title>
  <link rel="stylesheet" type="text/css" href="/static/theme/scribbish/application.css" />
  <%block name="customizecss"/>
  <style type="text/css">
    .invisible { display: none; }
  </style>
</head>
<body>

<div id="container">
  <div id="header" align="center">
    <a href="/">
      <img src="/static/img/title.gif" alt="山河奄有中華地 日月重開大漢天" />
    </a>
  </div>

  <div id="page">
    <div id="heading">
	<span > &raquo; <a href="/">Home</a>
	  (${archives[1]} posts)

	  % if user:
             % if is_view:
                  &bull; <a href="/new/"> New post </a>
             % endif
	     &bull; Logged in as ${user.nickname}
	     &raquo; <a href="${user_url}"> Logout</a>
          % else: 
             &bull;  <a href="${user_url}"> Login </a>
	  % endif
	</span>
    </div> <!-- div id="heading" -->

<!-- the blog entries -->
    <div id="content">
      <%block name="taginfo"/>
      ##content
      ${next.body()}
    </div> <!-- div id="content" -->

<!-- the page sidebar -->
    <div id="sidebar">
      <span id = "powered-by">
        <a href="http://www.twitter.
        3com/murphytalk"><img src="/static/img/twitter_follow_me.png" alt="Follow murphytalk on Twitter"/></a>
      </span>

      <p>

      <h3 class="sidbar-title">Tags</h3>

      <div class="tag-cloud">
        % for t in tag_cloud_list:
	  <span title="${t[1]}(${t[2]} posts)">
  	    <a class="tag" style="font-size: ${t[3]}%;" href="/tag/${t[0]}/"> ${t[1]} </a>
  	  </span>
	% endfor
      </div>

      <p>

      <h3>Feed</h3>
      <span id = "feed">
      <ul >
        <li>
          <img src="/static/img/rss.png" alt="RSS Feed"/>  <a href="/feed.xml">RSS Feed</a>
        </li>
        <li>
          <a href="http://feeds.feedburner.com/MurphytalksWeblog" rel="alternate" type="application/rss+xml"><img src="http://www.feedburner.com/fb/images/pub/feed-icon16x16.png" alt="" style="vertical-align:middle;border:0"/></a>&nbsp;<a href="http://feeds.feedburner.com/MurphytalksWeblog" rel="alternate" type="application/rss+xml">Subscribe in a reader</a>
        </li>
        <li>
          <span id = "powered-by">
          <a href="http://fusion.google.com/add?feedurl=http://feeds.feedburner.com/MurphytalksWeblog"><img src="http://buttons.googlesyndication.com/fusion/add.gif" width="104" height="17" style="border:0" alt="Add to Google Reader or Homepage"/></a></span>
        </li>
      </ul>
      </span>

      <!--Powered by -->
      <span id = "powered-by">
         <p>
           <a href="http://www.python.org/">
     	    <img src="/static/img/powered-by/PythonPowered.gif" alt="This site is Python powered." border="0" title="{% trans "Powered by Python"%}">
          </a>
         </p>
   
         <p>
           <a href="http://code.google.com/appengine/">
            <img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" />
           </a>
         </p>
   
         <p>
   	   <a href="http://www.gnu.org/software/emacs/">
   	    <img src="/static/img/powered-by/emacs-powered-blue.jpg" alt="This site is Emacs powered."  border="0" title="{% trans "Edit in Emacs"%}"> 
           </a>
         </p>
   
         <img src="/static/img/gmail.png" alt="mail" border="0" title="mail">
      </span>

      <p>

      <h3 class="sidebar-title">Archives</h3>
      <ul>
	% for a in archives[0]:
    	  <li>
	     <a href="/archive/${a.entry_id}/">${a.get_date()}</a> (${a.count})
  	  </li>
	% endfor
      </ul>

    </div> <!-- div class="side-bar" -->
  </div>   <!-- div class="page" -->
</div>     <!-- div class="container" -->

<div id="footer">&copy; Murphytalk,Since 2004 - layout and css design inspired by/copied from
  <a href="http://quotedprintable.com/pages/scribbish/">scribbish</a>
   - valid XHTML+CSS</div>
</div>
<div id="pagestatus">
  Trust is hard to earn,easy to lose,and almost impossible to take back.
</div>

  <link rel="stylesheet" type="text/css" href="/static/dp.SyntaxHighlighter/styles/shCore.css" />
  <link rel="stylesheet" type="text/css" href="/static/dp.SyntaxHighlighter/styles/shThemeDefault.css" />
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shCore.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushCSharp.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushXml.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushPython.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushCpp.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushJScript.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushBash.js"></script>
  <script language="javascript" src="/static/dp.SyntaxHighlighter/scripts/shBrushSql.js"></script>
  <script language="javascript">
    SyntaxHighlighter.defaults['ruler'] = true;
    SyntaxHighlighter.all();
  </script>

<script type="text/javascript">
var disqus_shortname = 'murpytalk-log';
(function () {
  var s = document.createElement('script'); s.async = true;
  s.src = 'http://disqus.com/forums/murpytalk-log/count.js';
  (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
}());
</script>


</body>

</html>
