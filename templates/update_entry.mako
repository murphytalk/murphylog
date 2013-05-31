<%inherit file="base.mako"/>

<%block name="customizecss">
<link rel="stylesheet" type="text/css" href="/static/theme/scribbish/form.css" />
</%block>

##==== body begins ====

<form method="post" action=
% if entry:
      "/post/${id}/"
% else:
      "/post-new/"
% endif

method="post" class="cssform" id="update-entry-form">

  <p>
  <label>Title</label>
  <input type="text" name="title" value=
    % if entry:
         "${entry.title}"
    % else:
         ""
    % endif
  />
  </p>

  <p>
  <label>Subject</label>
<textarea name="subject" rows="10" cols="80">
%if entry:
${entry.subject}
%endif
</textarea>
  </p>

  <p>
  <label>Text</label>
<textarea name="text" rows="10" cols="80">
%if entry:
${entry.text}
%endif
</textarea>
  </p>

  <p>
  <label>Type</label>
   <input type="radio" name="texttype" value="rs" 
          % if format == "rs":
             checked
          % endif
    /> reStructureText
   <input type="radio" name="texttype" value="st" 
          % if format == "st":
             checked
          % endif
    /> StructureText
   <input type="radio" name="texttype" value="bb" 
          % if format == "bb":
             checked
          % endif
   /> BBCode
  </p>

  <p>
  <label>Private</label>
  <input type="checkbox" name="private" value="private"
         % if entry and  entry.private:
             checked
         % endif
  />
  </p>

  <p>
  <label>Tags</label>
  <input type="text" name="tags" value=
         % if entry and entry.tags:
          "${entry.get_tags_as_str()}"
         % else:
           ""
         % endif
  />
  </p>


  <div style="margin-left: 150px;">
   <input name="post"   type="submit" value="Post" >
   <input name="cancel" type="submit" value="Cancel" onclick="history.back()">
    % if update_post and comment_count == 0: 
        <input name="delete" type="submit" value="Delete" style="color:red">
    % endif
  </div>

</form>
