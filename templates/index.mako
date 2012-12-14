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
      % if date is None or not same_date(p.post_date,date):
        <h3 class="date">
           ${p.post_date|n,weekday}
           <br>
           ${p.post_date|get_date_from_datetime}
        </h3>
      % endif

      ${entry(p,c.user,False,None)}

      <%
        date = p.post_date
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
