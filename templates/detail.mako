<%inherit file="base.mako"/>
<%namespace file="entry.mako" import="entry"/>

<%!
from filters import weekday,get_date_from_datetime
%>

##content

<h3 class="date">
  ${post.post_time|n,weekday}
  <br>
  ${post.post_time|get_date_from_datetime}
</h3>

${entry(post,user,True)}

<!--
<script type="text/javascript">
  var disqus_developer = 1;
</script>
-->

<div id="disqus_thread"></div>
<script type="text/javascript">
  /**
    * var disqus_identifier; [Optional but recommended: Define a unique identifier (e.g. post id or slug) for this thread]
    */
  var disqus_identifier = ${post.entry_id};
  (function() {
   var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
   dsq.src = 'http://murpytalk-log.disqus.com/embed.js';
   (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
  })();
</script>
<noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript=murpytalk-log">comments powered by Disqus.</a></noscript>
<a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
