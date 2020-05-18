# coding: utf-8 

import ads

####################################
fn = u'Aymeric'
nn = u'Spiga'
year = [2007,2020]
#aff = '(aff:"*Dynamique*" OR aff:"*LMD*")' #marche pas
aff = '(aff:"Dynamique" OR aff:"LMD")'
embedded = True
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
  #sortz = "citation_count"
  papers = ads.SearchQuery(q=query,fl=flz,rows=500, sort=sortz)
  
  ### get total citations #you can only loop on papers once!
  #totcit = 0
  #for paper in papers:
  #   totcit += paper.citation_count
  #   print(paper)
  #print(fn+' '+nn)
  #print(totcit)

  ## format results in HTML webpage
  f = open("test.html",'w')

  if embedded:
      htmlfile = open('header.html','r')
      f.write(htmlfile.read())
      htmlfile.close()

  f.write(u'<ol reversed>\n')
  yearsave = 0
  canvas = u'\
<li line-height=20px>{author}{end_author}, \
<b>{title}</b>, \
<i>{journal}</i>, \
{volume}, \
{year}. \
{doilink} \
<a href=https://ui.adsabs.harvard.edu/#abs/{bibcode}>[ADS link]</a>\
<a href=https://ui.adsabs.harvard.edu/#abs/{bibcode}/citations>[cite={count}]</a>\
\n\n'

  limrank=3

  for paper in papers:

     ## manage the 'et al.' case     
     dalist = [nn in iii for iii in paper.author]
     rank = dalist.index(True)+1
     ## -- 1. no "et al"
     if len(paper.author) <= limrank:
         end_author = ''
     else:
         ## -- 2. "et al" with rank number
         if rank > limrank:
             dalist = [nn in iii for iii in paper.author]
             end_author = ', et al. [{name}, {initial}. in rank {rank}]'.format(rank=rank,name=nn,initial=fn[0])
         ## -- 3. "et al" only
         else:
             end_author = ', et al.'        

     ## loop on each entry, format each line
     char = u''
     if paper.year != yearsave:
        print(paper.year)
        yearsave = paper.year
        char += '<h2> {year} </h2>\n\n'.format(year=paper.year)
     #.replace('Spiga','<mark>Spiga</mark>')
     char += canvas.format(\
         author = u' and '.join(paper.author[0:limrank]).encode('ascii', 'xmlcharrefreplace').decode('utf8'),\
         end_author = end_author,\
         title = paper.title[0].encode('ascii', 'xmlcharrefreplace').decode('utf8'),\
         journal = paper.pub,\
         volume = paper.volume,\
         year = paper.year,\
         count = str(paper.citation_count),\
         doilink = get_paper_links(paper.identifier),\
         bibcode = paper.bibcode)
#     ## PB
#     #if paper.abstract is not None:
#     #  char += paper.abstract.encode('ascii', 'xmlcharrefreplace')
     yearsave = paper.year
     f.write(char)
  f.write(u'\n</ol>')

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

