## -*- coding: utf-8 -*-
<%doc>
  context used by this template
  =============================
</%doc>
<%!
  from filters import render_markup_text

  def show_private(entry,logged_in_user):
      return not (entry.private and entry.owner.user_id and (logged_in_user is None or logged_in_user.user_id != entry.owner.user_id) )
 %>

<%def name="entry(entry,logged_in_user,show_detail)">

<div class="atomentry">
  <h4 class="title">
     % if show_private(entry,logged_in_user):
       ##public entry or the private entry belongs to logged in user
       <a href="/blog/${entry.entry_id}/" title="Click to read"> <img class="permalink" alt="permalink" src="/static/img/permalink.png" /></a>
       ${entry.title}
     % else:
       ##private entry
       <img class="permalink" alt="permalink" src="/static/img/permalink.png" /> ${entry.title}
     % endif
     ## highlight matched search words ...
  </h4>

  % if show_private(entry,logged_in_user):
      ${entry.subject | render_markup_text(entry.format)}

      % if show_detail:
         % if entry.text:
	   ―
           ${entry.text | render_markup_text(entry.format)}
         % endif
      % elif entry.text:
         &nbsp; &nbsp; &bull;&nbsp;<a href="/blog/${entry.entry_id}/">Read more &raquo;</a><p>
      % endif
  % endif

 <div class="entry_tag" >

    &bull;
    Posted by ${entry.owner.nickname()} on ${entry.get_post_time()} | last edited on ${entry.get_ledit_time()}
    % if logged_in_user  and entry.owner.user_id == logged_in_user.user_id:
      | <a href="/edit/${entry.entry_id}/">Edit this article</a>
    % endif

    % if entry.private:
      | This is a <font color=red>private</font> post
    % endif
    | <a href="/blog/${entry.entry_id}/#disqus_thread"></a>
    <br>
    &bull;
    Tags :
    % for t in entry.get_tags():
      <span title="%{t.name}">
        <a href="/tag/${t.normal}/">${t.name}</a>&#32;
      </span>
    % endfor

  </div> <!-- div class= ... entry_tag -->

</div> <!-- div class="atomentry" -->
</%def>
