"""
prepare csv for GAE from django_db dump files
3 inputs:
1. tags.csv dumped from GAE
2. entry.csv dumped from django_db
3. tag/entry relation csv dumped from django_db
"""
import csv

TAGS_F ="tags.csv"
ENTRY_F="/Users/murphytalk/leadmain/home/temp/entry.csv" # tab seprated
R_F    ="/Users/murphytalk/leadmain/home/temp/r.csv"

tags     = {} #{id:key}
entries  = [] #[(id,title,subject,text,'murphy@gmail.com',private,type,post_date,last_edit,tags),] #tags=key1;key2
relation = {} #{entry id:[tag key,],}

def load_tags(fname):
    id = 1
    lines = open(fname).readlines()
    for l in lines:
        fields=l.split(",")
        tags[str(id)] = fields[0]
        id+=1

def load_relation(fname):
    lines = open(fname).readlines()
    for l in lines:
        f=l.split("\t")
        entryid = f[0]
        tagid   = f[1][:-1]
        if relation.has_key(entryid):
            relation[entryid].append(tags[tagid])
        else:
            relation[entryid]=[tags[tagid]]

def load_entries(fname):
    def replace(txt):
        txt = txt.replace("\\n","\n")
        txt = txt.replace("\\r","\r")
        txt = txt.replace("\\t","\t")
        return txt

    lines = open(fname).readlines()
    for l in lines:
        f=l.split("\t")
        eid   = f[0]
        title = replace(f[1])
        #title.replace('\n','')
        #title.replace('\r','')
        sub   = replace(f[2])
        txt   = replace(f[3])
        tpe   = f[4]
        if(f[5]=="1"):
            priv = "True"
        else:
            priv = "False"
        pd    = f[6]
        le    = f[7][:-1]

        tags  = ""
        for t in relation[eid]:
            tags+=t+";"
        tags = tags[:-1]

        entries.append((eid,title,sub,txt,'murphytalk@gmail.com',priv,tpe,pd,le,tags))

def write_csv(fname):
    w = csv.writer(open(fname,"w+t"))
    w.writerows(entries)

if __name__ == "__main__":
    load_tags(TAGS_F)
    load_relation(R_F)
    load_entries(ENTRY_F)
    #print tags
    #print relation
    #print entries[4]
    write_csv("gae_entry.csv")
