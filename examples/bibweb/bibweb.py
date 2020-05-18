# coding: utf-8 

import ads

####################################
fifi = "pub.html"
####################################
fn = u'Aymeric'
nn = u'Spiga'
year = [2007,2020]
#aff = '(aff:"*Dynamique*" OR aff:"*LMD*")' #marche pas
aff = '(aff:"Dynamique" OR aff:"LMD")'
####################################
embedded = True
#embedded = False
iscite = False
#iscite = True
kindlist = "bullet"
#kindlist = "numbered"
####################################
#emphrank = 0
emphrank = 2
limrank = 3
#limrank = 2
####################################
####################################


""" Create a webpage for publications from a given author """
__author__ = "Aymeric Spiga <aymeric.spiga@sorbonne-universite.fr>"

#------------------------#
def get_paper_links(identifier):
   """ Get the DOI link from identifier returned by ads.SearchQuery """
   lst = set(paper.identifier)
   match = list(x for x in lst if "/" in x)
   if len(match) !=0:
     linkwww = u' <a href=http://dx.doi.org/'+match[0]+u'>[Journal website]</a>'
   else:
     linkwww = ''
   return linkwww

def author(firstname,name):
   """ Duplicate search for first name and initial of first name """
   ini = firstname[0]
   return u'(author:"'+name+', '+ini+'." OR author:"'+name+', '+firstname+'")'

#------------------------#
if __name__ == "__main__":

  ## provide a list of attributes to download from ADS
  flz = ['bibcode', 'author', 'year', 'first_author', 'title', 'property', 'pub', 'citation_count', 'volume', 'abstract', 'identifier', 'metrics']
  ## list of possibilities
  #first_paper.abstract              first_paper.build_citation_tree   first_paper.first_author_norm     first_paper.keys                  first_paper.pubdate
  #first_paper.aff                   first_paper.build_reference_tree  first_paper.id                    first_paper.keyword               first_paper.read_count
  #first_paper.author                first_paper.citation              first_paper.identifier            first_paper.metrics               first_paper.reference
  #first_paper.bibcode               first_paper.citation_count        first_paper.issue                 first_paper.page                  first_paper.title
  #first_paper.bibstem               first_paper.database              first_paper.items                 first_paper.property              first_paper.volume
  #first_paper.bibtex                first_paper.first_author          first_paper.iteritems             first_paper.pub                   first_paper.year
  
  ## create query
  listquery=[]
  listquery.append(author(fn,nn))
  listquery.append('year:{ys}-{ye}'.format(ys=year[0],ye=year[1]))
  if aff is not None:
      listquery.append(aff)
  listquery.append('property:REFEREED')
  query=" AND ".join(listquery) # ou test: if 'REFEREED' in paper.property
  print(query)
  
  ## execute query
  sortz = "date" 
  #sortz = "citation_count" #have to cancel by-year classification
  papers = ads.SearchQuery(q=query,fl=flz,rows=500, sort=sortz)
  
  ### get total citations #you can only loop on papers once!
  #totcit = 0
  #for paper in papers:
  #   totcit += paper.citation_count
  #   print(paper)
  #print(fn+' '+nn)
  #print(totcit)

  ## format results in HTML webpage
  f = open(fifi,'w')

  ## add footer and header
  if embedded:
      htmlfile = open('header.html','r')
      f.write(htmlfile.read())
      htmlfile.close()

  ## set list style
  if kindlist == "numbered": 
      f.write(u'<ol reversed>\n')
  else:
      f.write(u'<ul>\n')

  ## include citation counts or not
  if iscite:
      canvascite = u'<a href=https://ui.adsabs.harvard.edu/#abs/{bibcode}/citations>[cite={count}]</a>'
  else:
      canvascite = u''


  yearsave = 0
################################################
################################################
  canvas = u'\
<li line-height=20px>{author}{end_author}<br> \
<b>{title}</b><br> \
<i>{journal}</i>, \
{volume}, \
{year}.<br> \
{doilink} \
<a href=https://ui.adsabs.harvard.edu/#abs/{bibcode}>[ADS link]</a> \
<a href=REF/{bibcode2}.pdf>[PDF]</a> '\
+canvascite+\
u'\n\n'
################################################
################################################

  for paper in papers:

   if "Discussions" not in paper.pub:

     ## manage the 'et al.' case     
     dalist = [nn in iii for iii in paper.author]
     rank = dalist.index(True)+1
     ## -- 1. no "et al"
     if len(paper.author) <= limrank:
         end_author = ''
         dlimrank = limrank
     else:
         ## -- 2. "et al" with rank number
         if rank > limrank:
             dalist = [nn in iii for iii in paper.author]
             end_author = ', et al. [{name}, {initial}. rank {rank}]'.format(rank=rank,name=nn,initial=fn[0])
             dlimrank = limrank-1
         ## -- 3. "et al" only
         else:
             end_author = ', et al.'
             dlimrank = limrank        

     ## emphasize some of the papers in which author is high on the list
     prefix = suffix = ''
     if rank <= emphrank:
         #prefix, suffix = '<table width="100%" border ="1" cellspacing="1" cellpadding="1"><tr><td>','</td><tr></table>'
         prefix, suffix = '<font color="red">', '</font>'

     ## loop on each entry, format each line
     char = u''
     if paper.year != yearsave:
        print(paper.year)
        yearsave = paper.year
        char += '<p><h2> {year} </h2>\n\n'.format(year=paper.year)
     #.replace('Spiga','<mark>Spiga</mark>')

     addchar = canvas.format(\
         author = u' and '.join(paper.author[0:dlimrank]).encode('ascii', 'xmlcharrefreplace').decode('utf8'),\
         end_author = end_author,\
         title = prefix+paper.title[0].encode('ascii', 'xmlcharrefreplace').decode('utf8')+suffix,\
         journal = paper.pub,\
         volume = paper.volume,\
         year = paper.year,\
         count = str(paper.citation_count),\
         doilink = get_paper_links(paper.identifier),\
         bibcode = paper.bibcode,\
         bibcode2 = paper.bibcode.replace("&","_26"))

#     ## PB
#     #if paper.abstract is not None:
#     #  char += paper.abstract.encode('ascii', 'xmlcharrefreplace')

     addchar = prefix + addchar + suffix
     char = char + addchar
     yearsave = paper.year
     f.write(char)

  if kindlist == "numbered": 
      f.write(u'\n</ol>')
  else:
      f.write(u'\n</ul>')

  if embedded:
      htmlfile = open('footer.html','r')
      f.write(htmlfile.read())
      htmlfile.close()

  f.close
  
  
  ## https://github.com/adsabs/adsabs-dev-api/issues/26
  #q = ads.SearchQuery(q=query, fl=['id', 'bibcode'],rows=500, sort="citation_count")
  #bibcodes = [article.bibcode for article in q]
  ##bibcodes = [paper.bibcode for paper in papers]
  #bibtex_query = ads.ExportQuery(bibcodes=bibcodes, format='bibtex').execute()
  #ff = open("test.bib",'w')
  #for paper in papers:
  #   print paper
  #   if 'REFEREED' in paper.property:
  #     ff.write(paper.bibtex)
  #ff.close

