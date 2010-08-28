#!/bin/sh
HOST=localhost
USER=root
PASS=java2
DB=django_db_ver1
MYSQL="mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N "

dump_tags(){
    #$1 output file name
    mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N   > $1.tmp <<EOF
select t.value , count(m.tag_id) from murphylog_entry_tags m, tagsfield_tag t where t.id=m.tag_id group by m.tag_id ;
EOF
cat $1.tmp |sed 's/\t/,/g' > $1
rm $1.tmp
}

dump_entries(){
    #$1 output file name
    mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N   > $1 <<EOF
set charset utf8;
select id , title ,subject,text,text_type,private,post_date,last_edit from murphylog_entry;
EOF
}

dump_relationships(){
    #$1 output file name
    mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N   > $1 <<EOF
select entry_id ,tag_id from murphylog_entry_tags;
EOF
}


dump_tags tags.csv
dump_entries entry.csv
dump_relationships r.csv
