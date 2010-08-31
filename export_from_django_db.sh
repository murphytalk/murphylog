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

dump_archive(){
    #$1 output file name
    mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N   > $1.1 <<EOF
select left(post_date,7) as pd ,count(*) from murphylog_entry group by pd order by id desc;
EOF
cat $1.1 |sed 's/\t/,/g' > $1.2
    awk 'BEGIN{FS=","}{printf("select id  from murphylog_entry where left(post_date,7)=\"%s\" order by id desc limit 1;\n",$1);}' $1.2 |\
    mysql -h${HOST} -u${USER} -p${PASS} ${DB} -N   > $1.3
    pr -m -t -s\, $1.2  $1.3 > $1
    rm $1.1 $1.2 $1.3
}

#dump_tags tags.csv
#dump_entries entry.csv
#dump_relationships r.csv
dump_archive arch.csv
