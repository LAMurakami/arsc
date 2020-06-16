#!/usr/bin/env python
try:
	import os, glob, sys, getopt
	import tempfile 
	from SrbRegisterUtil import execMe,execSMe,PyIsSinit,CheckPyVersion
except:
	raise "Check you local Python Version. A minimum Python version required"
""" A script to query Metadata inside SRB """


SCHEME_NAME = "Name_Value"

def usage():
	print """SrbQueryUtil.py [--explore | --coll | --plot] <options>
  There are three exclusive modes available
    --explore [--name] | "key1" "key2" "key3" ... "keyN"
      List metadata names and possible values from existing SRB collections

    --coll <argument(s)>
      List collections that match all criterias provided in one or more 
      key::value pairs

      "key1::value1" "key2::value2" "key3::value3" ... "keyN::valueN"   : Input 
        parameters restraints

    --plot <arglist> 
      Create 2 dimensional plot file from existing SRB collections that match 
      all criterias provided in one or more key::value pair

      arglist:
        --xaxis <param>       : X-axis from Readme.xml. Ascending (program 
                                         will strip non numeric characters)
         --yaxis <param>       Y-axis from Readme.xml 
         --output <filename> : ASCII filename to store output
         --collection              : [Optional] Base SRB collection. If blank, 
                                         current Collection is used

         "key1::value1" "key2::value2" "key3::value3" ... "keyN::valueN"    : 
                                         Input parameters restraints 

  Generic options
    -h | --help        : This help text
    --version          : Print the script version

  Examples
  
  Explore mode examples
    To list valid metadata keys from existing SRB collections:
      SrbQueryUtil.py --explore --name

    To list valid metadata values (usually gotten from SrbQueryUtil.py 
    --explore --name) with key "PenMaterial", "StudyName", and 
    "PenStrModelPara":  
      SrbQueryUtil.py --explore "PenMaterial" "StudyName" "PenStrModelPara" 

  Collection mode example
    To list collection with StudyName is "WHA RHA study":
      SrbQueryUtil.py --coll "StudyName::WHA RHA study"

  Plot mode example
    To create a 2 dimensional chart with x axis being StrikingVel 
    and y axis being PenDepth,output file is myoutput.123, base 
    collection name is /home/margom.nirvana, with the following 
    restraints "PenMaterial::93W-5Ni-2Fe" "StudyName::WHA 
    RHA study" "PenStrModelPara::Weerasooriya" :

    SrbQueryUtil.py --plot --xaxis StrikingVel --yaxis PenDepth 
      --output myoutput.123 --collection  /home/margom.nirvana  
      "PenMaterial::93W-5Ni-2Fe" "StudyName::WHA RHA study"
      "PenStrModelPara::Weerasooriya" 
"""
# end function


def version():
	print """$Header: /cvs_repository/customers/HPCMP/testbed/NavyPilot/SrbQueryUtil.py,v 1.4 2013/04/11 17:18:50 martin Exp $"""
# end function

def printOneIndent(string):
	print '\t' + string
#end function

def parseSschemeOutput(rawInput):
	""" Parse output (with multiple lines) """
	arrOneLine = rawInput.split('\n')
	
	for strLine in arrOneLine:
		if len(strLine) > 0:
			arrElem = strLine.split()
			printOneIndent( (" ".join(arrElem[5:])).replace("\"",""))
#end of for



def plotMode():
	xaxis		= ''
	yaxis		= ''
	output		= '' #output file
	arrKeyValue	= ''
	collection	=	''
	
	try:
		opts,args = getopt.getopt(sys.argv[1:], "", ['plot','collection=','xaxis=', 'yaxis=','output='])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for arg,val in opts:
		if arg == "--collection":
			collection = val
		elif arg == "--xaxis":
			xaxis = val
		elif arg == "--yaxis":
			yaxis = val
		elif arg == "--output":
			output = val
		elif arg == "--plot":
			pass
		else:
			usage()
			sys.exit()	
			
	#end for
	try:
		fileOut = open(output, 'w')
	except IOError:
		print "Unable to open file {0}".format(output)
		sys.exit()
	#end try

	arrKeyValue = args
	fileOut.write("# Query Criteria : {0}\n".format(args))
	

	if xaxis == '' or yaxis == '' or output == '' or arrKeyValue == '':
		print "Missing mandatory option xaxis, yaxis, output, or key value"
		usage()
		sys.exit()
		
	fileOut.write("# x axis : {0}        y axis : {1}\n".format(xaxis,yaxis))

	if PyIsSinit():
		print "Sinit is OK..."
		status = 0
	else:
		print "No SRB session detected. Have you run Sinit yet?"
		sys.exit(2)


	if len(arrKeyValue) > 0 :

		## Try to unpack key_value
			
		subCmd = "SgetD -R -policy \""
		count  = 0
		for term in arrKeyValue:
			if count > 0:
				subCmd = subCmd + " AND "


			innerKey = term.split('::')[0]
			innerValue = term.split('::')[1]

			subCmd = subCmd + " DATA_OBJECT.data_id IN (select DATA_OBJECT.data_id where Name_Value.Name = '{0}' AND Name_Value.Value like '{1}')".format(innerKey,innerValue)
			
			count = count + 1

		#end for

		subCmd = subCmd + "\""	#end double quote before the collection name 	
		if collection != '':
			subCmd = subCmd + " " + collection #append collection name, if any

		print subCmd
		(rc,out) = execSMe(subCmd)
		if rc != 0:
			print "SQL query error. Perhaps an input parameter is incorrectly typed"
			rc = -1
		
		print out
		
	#end if 
	
	#Phase 2: Get the output from SgetD -R and extract X and Y axis from SRB MCAT

	xaxisVal = ''
	yaxisVal = ''
	if rc == 0:
		arrOutput = out.split('\n')
		arrOutput = arrOutput[2:] #I filter the first two lines. They are header information from SgetD
		for strEntry in arrOutput:
			arrEntry = strEntry.split()
			try:
				strAbsCol = arrEntry[0] + "/" + arrEntry[1]
			except:
				continue
			
			try:
				if arrEntry[2] != 'collection':
					print "This entry {0} is not a collection, skipping".format(strAbsCol)
					rc = -1
					continue
			except: 
				rc = -1

			if rc == 0:
				#WARNING: Parsing sixth column from Sscheme output. There is a dependency to SRB 2012 R3 Sscheme output column. If Sscheme output format changes, this command has to be revised
				subCmd = "Sscheme -l -scheme {0} {1} | egrep -1 '{2}|{3}'  ".format(SCHEME_NAME, strAbsCol, xaxis,yaxis)
				(rc,out) = execSMe(subCmd)
				if rc != 0:
					print "Unable to find datapoint for collection {0}. Skipping".format(strAbsCol)
				else:
					arrVal= out.split('\n')
					for index, strLine in enumerate(arrVal):
						arrStrLine = strLine.split()
						if len(arrStrLine)>5:
						
							try:
								if arrStrLine[5].replace('\"','') == xaxis:
									xaxisVal = arrVal[index+1].split()[5].replace('\"','')
								elif arrStrLine[5].replace('\"', '') == yaxis:
									yaxisVal = arrVal[index+1].split()[5].replace('\"','')
								#end if
							except Exception:
								print "Unable to parse Sscheme output. Skipping"
						#end if len
					#end for
					if xaxisVal != '' and yaxisVal != '':
						fileOut.write("{0} {1}\n".format(xaxisVal,yaxisVal))
						xaxisVal = ''
						yaxisVal = ''
					
				#end if rc != 0
			#end else
		#end for
	#end if
	
	fileOut.write("\n") # End it with a new line character. Some computers have problem reading files without endline character
	fileOut.close()
	if rc == 0:
		print "Success. Please review output file at : {0}".format(output)
	else:
		print "Error detected. Please review error message, fix, and try again"
#end function

def collMode():
	arrKeyValue	= ''
	try:
		opts,args = getopt.getopt(sys.argv[1:], "", ['coll'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	arrKeyValue = args
	
	if len(arrKeyValue) > 0 :
		if PyIsSinit():
			print "Sinit is OK..."
			status = 0
		else:
			print "No SRB session detected. Have you run Sinit yet?"
			sys.exit(2)

		## Try to unpack key_value
			
		subCmd = "SgetD -R -policy \""
		count  = 0
		for term in arrKeyValue:
			if count > 0:
				subCmd = subCmd + " AND "


			innerKey = term.split('::')[0]
			innerValue = term.split('::')[1]

			# This specifies the value as a non-exact match. TODO: Add flag for exact match.
			subCmd = subCmd + \
				" DATA_OBJECT.data_id IN (select DATA_OBJECT.data_id where Name_Value.Name = '{0}' AND Name_Value.Value like '{1}')".format(innerKey,innerValue)
			
			count = count + 1
		#end for

		subCmd = subCmd + "\""	#end double quote before the collection name 	

		#print subCmd
		(rc,out) = execSMe(subCmd)
		if rc != 0:
			print "SQL query error. Perhaps an input parameter is incorrectly typed"
			rc = -1
		
	#end if 
	else:
		print "At least one key::value pair must be specified.\n"
		usage()
		sys.exit()
	
	#Phase 2: Get the output from SgetD -R and extract collection, name, and value into columns

	if rc == 0:
		arrOutput = out.split('\n')
		arrOutput = arrOutput[2:] #I filter the first two lines. They are header information from SgetD

		matchingCollections = 0
		for strEntry in arrOutput:
			arrEntry = strEntry.split()
			try:
				# Absolute path to collection
				strAbsCol = arrEntry[0] + "/" + arrEntry[1]
				#print "strAbsCol: ", strAbscol
			except:
				continue
			
			try:
				if arrEntry[2] != 'collection':
					print "This entry {0} is not a collection, skipping".format(strAbsCol)
					rc = -1
					continue
				else:
					matchingCollections = matchingCollections + 1
			except: 
				rc = -1


			if rc == 0:
				print strAbsCol
				#WARNING: Parsing sixth column from Sscheme output. There is a dependency to SRB 2012 R3 Sscheme output column. If Sscheme output format changes, this command has to be revised
				subCmd = "Sscheme -l -scheme {0} {1} | egrep -w 'Name|Value' | grep string".format(SCHEME_NAME, strAbsCol)
				(rc,out) = execSMe(subCmd)

				if rc != 0:
					print "Unable to find name/value pairs for collection {0}. Skipping".format(strAbsCol)
				else:
					arrVal= out.split('\n')

					# Loop, incrementing index by 2
					#for index, strLine in [(2*i,l) for i,l in enumerate(arrVal)]:
					for index in range(0,len(arrVal),2):
						try:
							strNameLine = arrVal[index]
							arrStrNameLine = strNameLine.split()
							arrNameQuoteSplit = strNameLine.split('"')
						
							valIndex = index + 1
							strValLine = arrVal[valIndex]
							arrStrValLine = strValLine.split()
							arrValQuoteSplit = strValLine.split('"')						
						except Exception:
							break
						
						name = ''
						val = ''
						if len(arrStrNameLine)>5:
							try:
								if arrStrNameLine[0] == 'Name':
									name = arrNameQuoteSplit[1]
								#end if
							except Exception:
								print "Unable to parse Sscheme output. Skipping"
								break
						#end if len
						if len(arrStrValLine)>5:
							try:
								if arrStrValLine[0] == 'Value':
									val = arrValQuoteSplit[1]
								#end if
							except Exception:
								print "Unable to parse Sscheme output. Skipping"
								break
						#end if len
						print "\t{0}::{1}".format(name,val) 

					#end for
					
				#end if rc != 0
			#end else
		#end for
	#end if

	print "{0} matching collections found".format(matchingCollections)

	
	if rc == 0: 
		print "Success."
	else:
		print rc
		print "Error detected. Please review error message, fix, and try again"
#end function

def exploreMode():
	name_mode	=0
	path			= ''
	rc				= 0
	out			= ''
	
	try:
		opts,args = getopt.getopt(sys.argv[1:], "",  ['explore','name'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for arg,val in opts:
		if arg == "--name":
			name_mode = 1
		elif arg =="--explore":
			pass
		else:
			usage()
			sys.exit()	
			
	#end for

	if PyIsSinit():
		print "Sinit is OK..."
		status = 0
	else:
		print "No SRB session detected. Have you run Sinit/Sshell yet?"
		sys.exit(2)


	if len(args) > 0  or name_mode == 1:

		# Try to unpack key_value
		
		#Save overhead here by running Sscheme -l once and parse the output multiple times with help of temporary files
		
		subCmd = "Sscheme -l -scheme {0}  | egrep -w 'Name|Value' | grep 'string'".format(SCHEME_NAME)
		(rc,out) = execSMe(subCmd)
		
		if (rc == 0):
		
			fd, path = tempfile.mkstemp() 
			os.write(fd,out)
			os.close(fd)
		else:
			print "Failed to read Metadata Schema from MCAT. Exiting"
			rc = -1
		#end if
		
		
		if (rc == 0):
			if (name_mode == 1):
				print "Name mode"
				subCmd = "cat {0} | grep Name | sort | uniq".format(path)
				(rc,out) = execSMe(subCmd)
				if (rc != 0):
					print "Error getting Name listing"
				else:
					parseSschemeOutput(out)
			
			#end name mode
			else:
				print "Value mode"
				for strMetaName in args:
					print "Valid Metadata Values for key {0}".format(strMetaName)
					
					subCmd = "cat {0} | grep -A 1 -i {1} | grep -w Value | sort | uniq".format(path,strMetaName)
					(rc,out) = execSMe(subCmd)
					
					if (rc != 0):
						print "Error getting values for parameter {0}".format(strMetaName)
					else:
						parseSschemeOutput(out)
					#end if 
				
				#end of for loop
			#end if Value mode
		#end if 

	if (rc == 0):
		print "Success"
	else:
		print "Error detected. Please review error message, fix, and try again"
	
	try:
		os.remove(path) #cleanup
	except:
		pass

#end function

def main():

	if not CheckPyVersion():
		sys.exit(1)

	currMode = ''
	try:
		opts,args = getopt.getopt(sys.argv[1:], "hv", ['help', 'version','name','coll','plot','explore','collection=','xaxis=','yaxis=','output='])
	except getopt.GetoptError, err:
		print str(err)
		print
		usage()
		sys.exit(2)

	for arg,val in opts:
		if arg == "-h" or arg == "--help":
			usage()
			sys.exit()
		elif arg == "--version" or arg == "-v":
			version()
			sys.exit()
		elif arg == "--coll":
			if currMode == '': 
				currMode = 'COLL'
			else:
				print "Coll mode is exclusive, please remove plot or explore mode."
				print
				usage()
				sys.exit()
		elif arg =="--plot":
			if currMode == '':
				currMode = 'PLOT'
			else:
				print "Plot mode is exclusive, please remove coll or explore mode."
				print
				usage()
				sys.exit()
		elif arg == "--explore":
			if currMode == '':
				currMode = 'EXPLORE'
			else:
				print "Explore mode is exclusive, please remove coll or plot mode."
				print
				usage()
				sys.exit()

	#end for

	print """
SrbQueryUtil.py script
------------"""
	if currMode == 'COLL':
		collMode();
	elif currMode == 'PLOT':
		plotMode();
	elif currMode == 'EXPLORE':
		exploreMode();
	else:
		print "Unrecognized Mode"
		usage()
		sys.exit()
	
	

	


#end of function

if __name__=="__main__":
	main()

