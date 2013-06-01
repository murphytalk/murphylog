## -*- coding: utf-8 -*-
<?xml version="1.0" encoding="utf-8"?>
<%! from filters import render_markup_text %>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Murphytalk's Weblog</title>
<subtitle>山河奄有中華地 日月重開大漢天</subtitle>
<link rel="alternate" type="text/html" href="http://${site_domain}/" />
<link rel="self" type="application/atom+xml" href="http://${site_domain}/feed.xml" />
<id>http://${ site_domain }/</id>
<updated>${entries[0].last_edit.strftime("%Y-%m-%dT%H:%m:%SZ")}</updated>
<rights>Copyright © 2004-2010 murphytalk </rights>
% for entry in entries:
% if not entry.private:
<entry>
	<title>${ entry.title }</title>
	<link rel="alternate" type="text/html" href="${ site_domain}/blog/${entry.entry_id}/" />
	<id>${ site_domain },${ entry.post_time.strftime("%Y-%m-%dT%H:%m:%SZ") }:/blog/${ entry.entry_id }/</id>
	<published>${ entry.post_time.strftime("%Y-%m-%dT%H:%m:%SZ") }</published>
	<updated>${ entry.last_edit.strftime("%Y-%m-%dT%H:%m:%SZ") }</updated>
	<author>
		<name>${ entry.owner.nickname() }</name>
		<uri>http://${ site_domain }/</uri>
	</author>
	<content type="html" xml:base="http://${ site_domain }/" xml:lang="en"><![CDATA[
        ${ entry.subject|render_markup_text(entry.format)}
         % if entry.text:
	   ―
           ${entry.text | render_markup_text(entry.format)}
         % endif
	]]></content>
</entry>
% endif
% endfor
</feed>
