## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>
<%namespace file="entry.mako" import="entry"/>

<%!
from filters import weekday,get_date_from_datetime
from myutils import same_date
%>

##==== body begins ====

% if entries:
  <%
    date = None
  %>

  % for p in entries:
      % if date is None or not same_date(p.post_time,date):
        <h3 class="date">
           ${p.get_post_time()|n,weekday}
           <br>
           ${p.get_post_time()|get_date_from_datetime}
        </h3>
      % endif

      ${entry(p,user,False)}

      <%
        date = p.post_time
      %>
  % endfor

  <!-- pager -->

    <div class="pager">
    % if tag:
        % if new_page_bkmk:
            <a href="/tag/${tag}/prev/${new_page_bkmk}/"><< Newer posts</a>&nbsp;
        % endif

        % if old_page_bkmk:
            <a href="/tag/${tag}/next/${old_page_bkmk}/">Older posts >></a>&nbsp;
        % endif
    % else:
        % if new_page_bkmk:
           <a href="/prev/${new_page_bkmk}/"><< Newer posts</a>&nbsp;
        % endif

        % if old_page_bkmk:
           <a href="/next/${old_page_bkmk}/">Older posts >></a>&nbsp;
        % endif 
    % endif
    </div>

% else:
  <p>No entries are available.</p>
% endif
