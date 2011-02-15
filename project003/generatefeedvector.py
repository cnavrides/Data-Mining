import feedparser
import re

# returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
  # Parse the feed
  d=feedparser.parse(url)
  wc={}

  # Loop over all the entries
  for e in d.entries:
    if 'summary' in e: summary=e.summary
    else: summary=e.description

    # Extract a list of words
    words=getwords(e.title+' '+summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word]+=1
  return d.feed.title,wc

#this will get all of the words for the webpage passed in (html)
#and return them
def getwords(html):
  #remove all the HTML tags
  txt=re.compile(r'<[^>]+>').sub('',html)

  # Split words by all non-alpha characters
  words=re.compile(r'[^A-Z^a-z]+').split(txt)

  # Convert to lowercase
  return [word.lower() for word in words if word!='']


apcount={}
wordcounts={}
feedlist=[line for line in file('feedlist.txt')]#turns out this was the missing link
#go through each url in the file 'feedlist.txt'
for feedurl in feedlist:
  try:
    #this will get all the words from that webpage
    title,wc=getwordcounts(feedurl)
    wordcounts[title]=wc#save how many words were in each webpage
    for word,count in wc.items():
      apcount.setdefault(word,0)
      if count>1:
        apcount[word]+=1
  except:
    print 'Failed to parse feed %s' % feedurl

wordlist=[]
for w,bc in apcount.items():
  frac=float(bc)/len(feedlist)
  if frac>0.1 and frac<0.5:
    wordlist.append(w)

#open a file to write to
out=file('blogdata1.txt','w')
#make the first line the word 'Blog'
out.write('Blog')
#output each word from the wordlist to the file
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
#output each blog to the file now
for blog,wc in wordcounts.items():
  print blog
  out.write(blog)
  for word in wordlist:
    if word in wc: out.write('\t%d' % wc[word])
    else: out.write('\t0')
  out.write('\n')
