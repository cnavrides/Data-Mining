# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

#This will calculate the euclidian distance between person1 & person2 
#based on the movies they have in common
def sim_distance(prefs,person1,person2):
	#get the list of shared items
	shared_items={}
	for item in prefs[person1]:
		if item in prefs[person2]:
			shared_items[item]=1

	#if they have no ratings in common then return 0
	if len(shared_items)==0: return 0

	#Add up the squares of all the differences
	#if they both rate a movie, then take person1 - person 2 and square it
	#then sum it all up
	sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
			for item in prefs[person1] if item in prefs[person2]])
	return 1/(1+sqrt(sum_of_squares))


def sim_pearson(prefs,person1,person2):
	#get the list of shared items
	shared_items={}
	for item in prefs[person1]:
		if item in prefs[person2]:
			shared_items[item]=1
	#n = number of elements in common
	n=len(shared_items)
	
	#if they have no items in common return 0
	if n == 0: return 0

	#add up all the preferences
	sum1=sum([prefs[person1][item] for item in shared_items])
	sum2=sum([prefs[person2][item] for item in shared_items])

	#sum up the squares
	sum1_square=sum([pow(prefs[person1][item],2) for item in shared_items])
	sum2_square=sum([pow(prefs[person2][item],2) for item in shared_items])

	#sum up the products
	sum_product=sum([prefs[person1][item]*prefs[person2][item] for item in shared_items])

	#Calculate the Pearson score
	num=sum_product-(sum1*sum2/n)
	denominator=sqrt((sum1_square-pow(sum1,2)/n)*(sum2_square-pow(sum2,2)/n))
	if denominator==0: return 0

	r=num/denominator
	return r

#Returns the top match for that persoon
#similarity coeffecient is defaulted to pearson, stars to 5
def topMatches(prefs, person, n=5, similarity=sim_pearson):
	scores=[(similarity(prefs,person,other),other)
			for other in prefs if other != person]
	
	#Sort. highest score on top
	scores.sort()
	scores.reverse()
	return scores[0:n]




# Gets recommendations for a person by using a weighted average
# of every other user's rankings. Default similarity metric is pearson
def getRecommendations(prefs,person,similarity=sim_pearson):
  totals={}
  similarity_Sums={}
  
  #compare person (passed in) to everyone else
  for other in prefs:
    # don't compare me to myself
    if other==person: continue
    sim=similarity(prefs,person,other)

    # ignore scorees of zero or lower
    if sim<=0: continue
    for item in prefs[other]:
	    
      # only score movies person haven't seen yet
      if item not in prefs[person] or prefs[person][item]==0:
        # Similarity * Score
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # Sum of similarities
        similarity_Sums.setdefault(item,0)
        similarity_Sums[item]+=sim

  # Create the normalized list
  rankings=[(total/similarity_Sums[item],item) for item,total in totals.items()]

  # Return the sorted list
  rankings.sort()
  rankings.reverse()
  return rankings

#will take in the preferences from everyone and return a flipped dictionary
#so that you can so who has rated an item instead of what items a person has
#rated
def transformPrefs(prefs):
  result={}
  for person in prefs:
    for item in prefs[person]:
      result.setdefault(item,{})
      
      # Flip item and person
      result[item][person]=prefs[person][item]
  return result


#name says it all...
def calculateSimilarItems(prefs,n=10):
  # Create a dictionary of items showing which other items they
  # are most similar to.
  result={}
  # Invert the preference matrix to be item-centric
  itemPrefs=transformPrefs(prefs)
  counter=0
  for item in itemPrefs:
    #Status updates for large datasets
    counter+=1
    if counter%100==0: print "%d / %d" % (counter,len(itemPrefs))
    # Find the most similaar items to this one
    scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
    result[item]=scores
  return result

#this will get the recommended items for the user and return a list
#of movies.
def getRecommendedItems(prefs,itemMatch,user):
  userRatings=prefs[user]
  scores={}
  totalSimilarity={}
  # Loop over items rated by this user
  for (item,rating) in userRatings.items( ):

    # Loop over items similar to this one
    for (similarity,item2) in itemMatch[item]:

      # Ignore if this user has already rated this item
      if item2 in userRatings: continue

      # Weighted sum of rating times similarity
      scores.setdefault(item2,0)
      scores[item2]+=similarity*rating

      # Sum of all the similarities
      totalSimilarity.setdefault(item2,0)
      totalSimilarity[item2]+=similarity

  # Divide each total score by total weighting to get an average
  rankings=[(score/totalSim[item],item) for item,score in scores.items( )]

  # Return the rankings from highest to lowest
  rankings.sort( )
  rankings.reverse( )
  return rankings

#movie lens data from university of michigan
def loadMovieLens(path='/data/movielens'):
  # Get movie titles
  movies={}
  for line in open(path+'/u.item'):
    (id,title)=line.split('|')[0:2]
    movies[id]=title
  
  # Load data from file and put into preferences
  preferences={}
  for line in open(path+'/u.data'):
    (user,movieid,rating,ts)=line.split('\t')
    preferences.setdefault(user,{})
    preferences[user][movies[movieid]]=float(rating)
  return preferences
