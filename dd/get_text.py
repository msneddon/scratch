

import urllib2
import json
import sys
import os
import shutil
import xml.etree.ElementTree as ET


pmc_lookup_url = "http://www.pubmedcentral.nih.gov/utils/oa/oa.fcgi?id="
tgzdir = "tgz"
xmldir = "xml"
pdfdir = "pdf"

total   = 0;
success = 0;

for row in sys.stdin:
    pmcid = row.rstrip()
    if not pmcid:
        continue
    total+=1
    lookup_data = urllib2.urlopen(pmc_lookup_url + pmcid).read()
    rsp_root = ET.fromstring(lookup_data)

    #print("===\n"+lookup_data)
    if rsp_root.findall("./error"):
        sys.stderr.write("Error retrieving "+pmcid+": "+rsp_root.find("./error").text+"\n")
        continue
    
    links = rsp_root.findall("./records/record/link")
    tgz_href = ''
    for l in links:
        if l.attrib['format'] == 'tgz':
            tgz_href=l.attrib['href']
    if not tgz_href:
        sys.stderr.write("Error retrieving "+pmcid+": could not find tgz link in XML response.\n")
        sys.stderr.write(lookup_data)
        continue

    
    tgzcontent = urllib2.urlopen(tgz_href)
    tgz_file = tgzdir+"/"+tgz_href.split('/')[-1] # get the filename from the url
    record_name = tgz_file.split('/')[-1].split('.')[0]  # get the expected output folder name, assuming no dots in name
    with open(tgz_file, 'wb') as fp:
        shutil.copyfileobj(tgzcontent, fp)
    
    # unpack
    contents = os.popen("tar xfvz '"+tgz_file+"' -C "+tgzdir).read()
    #print(record_name+"--"+tgz_file)
    content_paths = [s.strip() for s in contents.splitlines()]
    for c in content_paths:
        if c.endswith('.nxml'):
            shutil.move(tgzdir+"/"+c,xmldir+"/"+pmcid+".nxml") #"___"+c.split('/')[-1]) #could add more descriptive info
        if c.endswith('.pdf'):
            shutil.move(tgzdir+"/"+c,pdfdir+"/"+pmcid+"___"+c.split('/')[-1])

    shutil.rmtree(tgzdir+"/"+content_paths[0]);

    print(" - success on "+pmcid)
    success += 1


print("done.  downloaded "+str(success)+" of "+str(total));
