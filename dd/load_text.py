import urllib2
import json
import sys
import os
import shutil
import xml.etree.ElementTree as ET
import psycopg2
import traceback

db='chemotaxis'
user=os.environ['PGUSER']
psswd=os.environ['PGPASSWORD']


xmldir = "xml"
xmlextension = '.nxml'

total   = 0;
success = 0;

override = True # set to true to update the article text instead of failing if it already exists

conn = psycopg2.connect("dbname='"+db+"' user='"+user+"' host='localhost' password='"+psswd+"'")
conn.autocommit = True
cur = conn.cursor()



for row in sys.stdin:
    filename = row.rstrip()
    if not filename:
        continue
    total+=1

    full_article = ET.parse(xmldir + "/" + filename+xmlextension).getroot()
    
    for i in full_article.findall('front/article-meta/article-id'):
        if i.get('pub-id-type') == 'pmid':
            pmid  = i.text
        elif i.get('pub-id-type') == 'pmc':
            pmcid = i.text
    
    # get title and abstract
    extract = ''
    titles = full_article.findall('front/article-meta/title-group/article-title') # could pick out alt title here too
    for t in titles:
        extract += ET.tostring(t,encoding='utf8',method='html')+"\n";
    abstracts = full_article.findall('front/article-meta/abstract') # multiple abstracts, for instance if there is an author summary
    for a in abstracts:
        extract += ET.tostring(a,encoding='utf8',method='html')+"\n";    
    
    # get main text body
    bodies = full_article.find('body')
    for b in bodies:
        extract += ET.tostring(b,encoding='utf8',method='html')+"\n";
    
    print("pubmed id: "+pmid+", pmc id: PMC"+ pmcid)
    #print(extract);
    try:
        cur.execute("INSERT INTO pmc_articles (pmid, pmcid, text) VALUES (%s, %s, %s)",
            (pmid, pmcid, extract))
        success += 1
    except psycopg2.IntegrityError,e:
        if override:
            cur.execute("UPDATE pmc_articles SET text = %s, pmid = %s, pmcid = %s",
            (extract,pmid,pmcid))
            success += 1
        else:
            print(e)
    
    
cur.close()
conn.close()
    
    

print("done.  imported "+str(success)+" of "+str(total));
