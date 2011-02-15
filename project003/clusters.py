from PIL import Image,ImageDraw
import random
from math import sqrt
'''
			Classes
'''
#This class will represent a cluster in a hierarchical tree
class bicluster:
  #This is what to do when the class gets initiliazed. You can pass in spe$
  #or use the default values
  def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
    self.left=left
    self.right=right
    self.vec=vec
    self.id=id
    self.distance=distance


'''
			Functions
'''
# As the name suggests this will read in a file and return it's contents
def readfile(filename):
  # Go through each line and save it in lines
  lines=[line for line in file(filename)]
  
  # First line is the column titles
  columnNames=lines[0].strip().split('\t')[1:]
  rowNames=[]
  data=[]
  for line in lines[1:]:
    p=line.strip().split('\t')
    # First column in each row is the rowname
    rowNames.append(p[0])
    # the data for this row is the remainder of the row
    data.append([float(x) for x in p[1:]])
  return rowNames,columnNames,data

#Good old pearson... This will give the pearson correlation for the 2 vectors
def pearson(list1,list2):
  # Simple sums. Take the sum of each list
  sum1=sum(list1)
  sum2=sum(list2)
  
  # Sums of the squres. Add up the square of each number in the list
  sum1_squared=sum([pow(l,2) for l in list1])
  sum2_squared=sum([pow(l,2) for l in list2])	
  
  # Sum of the products. Take each item in the list and multiply 
  pSum=sum([list1[i]*list2[i] for i in range(len(list1))])
  
  # Calculate pearson coreleation
  numerator=pSum-(sum1*sum2/len(list1))
  denemonator=sqrt((sum1_squared-pow(sum1,2)/len(list1))*(sum2_squared-pow(sum2,2)/len(list1)))
  if denemonator==0: return 0

  return 1.0-numerator/denemonator

#This function takes in the rows and makes each row a cluster.
def initializeClusters(rows,distance=pearson):
  distances={}
  currentclustid=-1

  # Clusters are initially just the rows
  clust=[bicluster(rows[i],id=i) for i in range(len(rows))]

  while len(clust)>1:
    lowestpair=(0,1)
    closest=distance(clust[0].vec,clust[1].vec)

    # loop through every pair looking for the smallest distance
    for i in range(len(clust)):
      for j in range(i+1,len(clust)):
        # distances is the cache of distance calculations
        if (clust[i].id,clust[j].id) not in distances: 
          distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)

        d=distances[(clust[i].id,clust[j].id)]

        if d<closest:
          closest=d
          lowestpair=(i,j)

    # calculate the average of the two clusters
    mergevec=[
    (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 
    for i in range(len(clust[0].vec))]

    # create the new cluster
    newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
                         right=clust[lowestpair[1]],
                         distance=closest,id=currentclustid)

    # cluster ids that weren't in the original set are negative
    currentclustid-=1
    del clust[lowestpair[1]]
    del clust[lowestpair[0]]
    clust.append(newcluster)

  return clust[0]

#This will print the cluster and show the branches and endpoints
def printclust(clust,labels=None,n=0):
  # indent to make a hierarchy layout
  for i in range(n):  print ' ',
  if clust.id<0:
    # negative id means that this is branch
    print '-'
  else:
    # positive id means that this is an endpoint
    # if a label was passed in use that one, otherwise use it's 
    # number id
    if labels==None: print clust.id
    else: print labels[clust.id]

  #now print the right and left branches
  if clust.left!=None: printclust(clust.left,labels=labels,n=n+1)
  if clust.right!=None: printclust(clust.right,labels=labels,n=n+1)


# This will determine the height of the image that will be needed
def getheight(clust):
  #is this an endpoint? Then the height is just 1
  if clust.left==None and clust.right==None: return 1

  # Otherwise the height is the same of the heights of
  # each branch
  return getheight(clust.left)+getheight(clust.right)


def getdepth(clust):
  # The distance of an endpoint is 0.0
  if clust.left==None and clust.right==None: return 0

  #The distance of a branch is the greater of its two sides
  # plus its own distance
  return max( getdepth(clust.left), getdepth(clust.right) )+clust.distance


#this will make a new image that is 20 pixels for each unit of height and 
#a fixed width of 1200 for each cluster
def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
  # height and width
  height=getheight(clust)*20
  width=1200
  depth=getdepth(clust)

  # width is fixed, so scale distances accordingly
  scaling=float(width-150)/depth

  # Create a new image with a white background
  img=Image.new('RGB',(width,height),(255,255,255))
  draw=ImageDraw.Draw(img)

  draw.line((0,h/2,10,h/2),fill=(255,0,0))    

  # Draw the first node
  drawnode(draw,clust,10,(height/2),scaling,labels)
  img.save(jpeg,'JPEG')

#takes a cluster and it's location then draws a line to it's nearest neighbor.
#the line indicates how much error there was
def drawnode(draw,clust,x,y,scaling,labels):
  if clust.id<0:
    h1=getheight(clust.left)*20
    h2=getheight(clust.right)*20
    top=y-(h1+h2)/2
    bottom=y+(h1+h2)/2

    # Line length
    ll=clust.distance*scaling
    
    # Vertical line from this cluster to children    
    draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))    
    
    # Horizontal line to left item
    draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))    

    # Horizontal line to right item
    draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))        

    # Call the function to draw the left and right nodes    
    drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
    drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
  else:   
    # If this is an endpoint, draw the item label
    draw.text((x+5,y-7),labels[clust.id],(0,0,0))


#switch the rows and columns in data.
def rotatematrix(data):
  newdata=[]
  for i in range(len(data[0])):
    newrow=[data[j][i] for j in range(len(data))]
    newdata.append(newrow)
  return newdata


# Use k-means clustering to make clusters.
#the default number of clusters is 4.
def kcluster(rows,distance=pearson,k=4):
  # Determine the minimum and maximum values for each point
  ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) 
  for i in range(len(rows[0]))]

  # Create k randomly placed centroids
  clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] 
  for i in range(len(rows[0]))] for j in range(k)]
  
  lastmatches=None
  for t in range(100):
    print 'Iteration %d' % t
    bestmatches=[[] for i in range(k)]
    
    # Find which centroid is the closest for each row
    for j in range(len(rows)):
      row=rows[j]
      bestmatch=0
      for i in range(k):
        d=distance(clusters[i],row)
        if d<distance(clusters[bestmatch],row): bestmatch=i
      bestmatches[bestmatch].append(j)

    # If the results are the same as last time, this is complete
    if bestmatches==lastmatches: break
    lastmatches=bestmatches
    
    # Move the centroids to the average of their members
    for i in range(k):
      avgs=[0.0]*len(rows[0])
      if len(bestmatches[i])>0:
        for rowid in bestmatches[i]:
          for m in range(len(rows[rowid])):
            avgs[m]+=rows[rowid][m]
        for j in range(len(avgs)):
          avgs[j]/=len(bestmatches[i])
        clusters[i]=avgs
      
  return bestmatches

#returns the tanimoto coefficient between the two vectors/lists
def tanimoto(vector1,vector2):
  OnlyIn_Vector1,OnlyIn_Vector2,shared=0,0,0
  
  for i in range(len(vector1)):
    if vector1[i]!=0: OnlyIn_Vector1+=1 # in v1
    if vector2[i]!=0: OnlyIn_Vector2+=1 # in v2
    if vector1[i]!=0 and vector2[i]!=0: shared+=1 # in both
  
  return 1.0-(float(shared)/(OnlyIn_Vector1+OnlyIn_Vector2-shared))

#takes the data and shifts each point around based on where the other 
#points are. It does this until it can't anymore and returns that list
#the default distance to use is the pearson
def scaledown(data,distance=pearson,rate=0.01):
  n=len(data)

  #realdist will hold the real distances between every pair of items
  realdist=[[distance(data[i],data[j]) for j in range(n)] 
             for i in range(0,n)]

  # Randomly initialize the starting points of the locations in 2D
  locations=[[random.random(),random.random()] for i in range(n)]
  fakedist=[[0.0 for j in range(n)] for i in range(n)]
  
  lasterror=None
  for m in range(0,1000):
    # Find projected distances. fakedist is the euclidian dist between them
    for i in range(n):
      for j in range(n):
        fakedist[i][j]=sqrt(sum([pow(locations[i][x]-locations[j][x],2) 
                                 for x in range(len(locations[i]))]))
  
    # Move points
    grad=[[0.0,0.0] for i in range(n)]
    
    totalerror=0
    for k in range(n):
      for j in range(n):
        if j==k: continue
        # The error is percent difference between the distances
        errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
        
        # Each point needs to be moved away from or towards the other
        #point in proportion to how much error it has
        grad[k][0]+=((locations[k][0]-locations[j][0])/fakedist[j][k])*errorterm
        grad[k][1]+=((locations[k][1]-locations[j][1])/fakedist[j][k])*errorterm

        # Keep track of the total error
        totalerror+=abs(errorterm)
    print totalerror

    # If the answer got worse by moving the points, we are done
    if lasterror and lasterror<totalerror: break
    lasterror=totalerror
    
    # Move each of the points by the learning rate times the gradient
    for k in range(n):
      locations[k][0]-=rate*grad[k][0]
      locations[k][1]-=rate*grad[k][1]

  return locations

#Draw a graph with labels and save it to file jpeg, which defaults to mds2d.jpg
def draw2d(data,labels,jpeg='mds2d.jpg'):
  img=Image.new('RGB',(2000,2000),(255,255,255))
  draw=ImageDraw.Draw(img)
  for i in range(len(data)):
    x=(data[i][0]+0.5)*1000
    y=(data[i][1]+0.5)*1000
    draw.text((x,y),labels[i],(0,0,0))
  img.save(jpeg,'JPEG')  
