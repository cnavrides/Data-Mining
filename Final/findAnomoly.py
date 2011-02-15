#!/usr/bin/python

#dictionary which will hold the line as a key and the count as the value
count = {}

#Open the orignial csv provided
fileIn = open('final_ORIGINAL.csv', 'r')
#skip the first line
fileIn.readline()

#go through each line and give it a key value pair
for line in fileIn:
	if line[0:len(line)-1] in count:
		count[line[0:len(line)-1]] = count[line[0:len(line)-1]]+1
	else:
		count[line[0:len(line)-1]] = 1
#close the in file
fileIn.close()

#open the outfile
fileOut = open('Anomoly_Output.txt', 'w')

for keyVal in count.keys():
	fileOut.write(str(keyVal) + "   ---   " + str(count[keyVal]) + "\n")

fileOut.close()

'''
#open the outfile
fileOut = open('Anomoly_Output.txt', 'w')

for keyVal in count.keys():
	sortedKeys[keyVal.split(';')[0]] = keyVal

for keyVal in sorted(sortedKeys.iterkeys()):
	fileOut.write(str(sortedKeys[keyVal]) + "   ---   " + str(count[sortedKeys[keyVal]]) + "\n")

fileOut.close()
'''
