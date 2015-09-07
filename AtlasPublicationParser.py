#!/usr/bin/env python
############################################################################################################
# A tool to parse the publications found at https://twiki.cern.ch/twiki/bin/view/AtlasPublic/Publications
# To run: "python AtlasPublicationParser.py" in the directory you want to populate. Folders for    
# for each journal will be created with the pdf files saved into their respective ones.            
# joshua.wyatt.smith@cern.ch                                                                       
#############################################################################################################
import bs4
import sys
import os
import re
import csv

YEAR=str('(2011)')
out_file_name = "title_and_url_Atlas"
out_file = open(out_file_name+"_"+YEAR+".txt", 'w')
Broken_links=[]
Unknown_Journals=[]
Publication_Count=[]

def download_all_publications_list():
       os.system('wget --quiet -O atlas.html "https://twiki.cern.ch/twiki/bin/view/AtlasPublic/Publications" ')

def download_html_INSPIRE(urladdress):
    print "Working on -> ", urladdress
    os.system('wget --quiet -O tempJournal.html ' + str(urladdress))  ## Save html to tempJournal.html. THis file will get written over often
    filename="tempJournal.html"
    html_file = open(filename, 'r')
    soup = bs4.BeautifulSoup(html_file)
    title=soup.find('title').string.encode('ascii','ignore')
######### find the DOI and year ###############
    URLS=[]
    Journal_and_date=[]
    for li in soup.find_all('li'):
        for link in li.find_all('a'):    ## Get all urls
            doi_url=link.get('href')
            URLS.append(str(doi_url))    ## append all the potential urls to a list
        for d in li.find_all('strong'):  ## find references to date and journal (inspire style)
            Journal_and_date.append(d.string)
    for u in URLS:
        if "dx.doi.org" in u:            ## search for dx.doi which means they've been published somehwere
            for J in Journal_and_date:
                if YEAR in J:
                    print "Found one that matches the criteria:",'\n', str(title).rstrip(" - INSPIRE-HEP"),'\n', u,'\n', J, '\n' ## Eye candy
                    out_file.write(str(title).rstrip(" - INSPIRE-HEP") + '\n') ## Write title to file
                    out_file.write(u+'\n')      ## Write doi url to file
                    out_file.write(J+'\n')      ## Write Journal, year stuff to file
                    with open("Atlas_Collaboration.csv",'a') as MyCsv:
                        linewriter = csv.writer(MyCsv, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        linewriter.writerow(["ATLAS Collaboration", str(title).rstrip(" - INSPIRE-HEP"), J, u])
                    Download_pdf(u,J)
                    Publication_Count.append(int(1))
                    print "Current publication count = ", sum(Publication_Count)

def Atlas_journals():
    filename = "atlas.html"
    html_file = open(filename, 'r')
    soup = bs4.BeautifulSoup(html_file)
    URLS = []
    inspirehep=[]
    for tr in soup.find_all('tr'):
        for td in tr.find_all('td'):
            if td.get('class') != None and td.get('class')[0] == "twikiTableCol2":
                for link in tr.find_all('a'):
                    url = link.get('href')
                    URLS.append(str(url))
    for u in URLS:
        if "inspirehep" in u:
            inspirehep.append(u)
    return inspirehep


def Download_pdf(pdfURL, Journal):
    print "Downloading html file..."
    os.system('wget --quiet --user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"\
     -O PDFtoDownload.html ' + '"'+str(pdfURL)+'"')  ## Science direct needs to be fooled into thinking a browser is accessing it
    html_file = open("PDFtoDownload.html", 'r')
    soup = bs4.BeautifulSoup(html_file)
    Journal_file=str(Journal).replace (" ", "_")+'.pdf'
    print str(Journal)
    ## For EurPhys
    print "################################################################"
    print "#                      Downloading PDF                         #"
    print "################################################################"
    try:
        ###############
        ## for Eur.Phys
        if "Eur.Phys" in str(Journal):
            pdf_url_eurphys=soup.find("meta", {"name":"citation_pdf_url"})['content'] 
            os_command_eurphys='"'+'./EurPhys-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_eurphys)+'"'
            os.system('wget --quiet -O'+os_command_eurphys)
        ###############
        ## for PhysRev
        elif "Phys.Rev" in str(Journal):
            physRev_tmp=[]
            physRev_tmp1=[]
            for a in soup.find_all('a', href=True):
                physRev_tmp.append(str(a["href"]))
            for t in physRev_tmp:
                if "/pdf" in t:
               # if "/pra/pdf" in t or "/prb/pdf" in t or "/prc/pdf" in t or "/prd/pdf" in t:
                    physRev_tmp1.append(t)
	    PhysRev_url=physRev_tmp1[0]
            pdf_url_PhysRev = 'http://journals.aps.org' + PhysRev_url
            os_command_PhysRev='"'+'./PhysRev-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_PhysRev)+'"'
            os.system('wget --quiet -O'+os_command_PhysRev)
        ###############
        ## For Elsevier/sciencedirect which is Nuclear Physics B
        elif "Nucl.Phys" in str(Journal):
            nucB_tmp=[]
            nucB_tmp1=[]
            for s in soup.find_all('a', href=True):
                nucB_tmp.append(str(s['href']))
            for n in nucB_tmp:
                if "/www.sciencedirect.com/science/article" in n:
                    nucB_tmp1.append(n)
            pdf_url_NucB=nucB_tmp1[1]
            os_command_NucB='"'+'./Nucl.Phys-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_NucB)+'"'
            os.system('wget --quiet --user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1" -O'+os_command_NucB)
        ###############
        ### For JHEP     
        elif "JHEP" in str(Journal):
            pdf_url_jhep=soup.find("meta", {"name":"citation_pdf_url"})['content'] 
            os_command_jhep='"'+'./JHEP-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_jhep)+'"'
            os.system('wget --quiet --user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1" -O'+os_command_jhep)
        ###############
        ## For Phys.Letters
        elif "Phys.Lett" in str(Journal):
            Physlett_tmp=[]
            Physlett_tmp1=[]
            for let in soup.find_all('a', href=True):
                Physlett_tmp.append(str(let['href']))
            for let1 in Physlett_tmp:
                if "/www.sciencedirect.com/science/article" in let1:
                    Physlett_tmp1.append(let1)
	    pdf_url_Physlett=Physlett_tmp1[1]
            os_command_Physlett='"'+'./Phys.Lett-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_Physlett)+'"'
            os.system('wget --quiet --user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1" -O'+os_command_Physlett)
	###############
        ## For New J. Phys
        elif "New J.Phys" in str(Journal):
            pdf_url_newj=soup.find("meta", {"name":"citation_pdf_url"})['content'] 
            os_command_newj='"'+'./New.J.Phys-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_newj)+'"'
            os.system('wget --quiet -O'+os_command_newj)
        ###############
        ## For JINST
        elif "JINST" in str(Journal):
            pdf_url_jinst=soup.find("meta", {"name":"citation_pdf_url"})['content'] 
            os_command_jinst='"'+'./JINST-2011/'+'"'+'"'+Journal_file+'"'+" "+ '"'+str(pdf_url_jinst)+'"'
            os.system('wget --quiet -O'+os_command_jinst)

        else:
            print "THIS IS A NEW JOURNAL: ",str(Journal), ". PLEASE ACCOMODATE CODE ACCORDINLGY."
            Unknown_Journals.append(str(Journal))
    except (TypeError, IndexError):
        print "Something was wrong with link. Please check it out: ", str(pdfURL)
        Broken_links.append(str(pdfURL))

def main():
    download_all_publications_list()
    Journals=Atlas_journals()
    inspirehep=Journals
    os.system('mkdir Nucl.Phys-2011 PhysRev-2011 JHEP-2011 EurPhys-2011 Phys.Lett-2011 New.J.Phys-2011 JINST-2011')
    for inspire in inspirehep:
        download_html_INSPIRE(inspire)
    ### To test code you can select at what url placing to start since most of the first urls on atlas twiki are not published    
    # for inspire in range(20,len(inspirehep),1):
    #     download_html_INSPIRE(inspirehep[inspire])
    print "Total Publications found =", sum(Publication_Count)
    print "Links that failed to download: ",Unknown_Journals
    print "Links with journals with a format that is unrecongnized: ", Unknown_Journals

main()









