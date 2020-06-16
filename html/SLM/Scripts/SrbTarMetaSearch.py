#!/usr/bin/env python
try:
	import os, glob, sys, getopt
	import tempfile 
	from SrbRegisterUtil import execMe,execSMe,PyIsSinit,CheckPyVersion
except: 
	raise "Check you local Python Version. A minimum Python version required"

""" A script that searches Metadata information from MCAT """


SCHEME_NAME = "Name_Value"

def usage():
	print """SrbTarMetaSearch.py: Recursively search for Data Objects that met your search criteria
	usage: SrbTarMetaSearch.py [option] [value] [collection]

		option:
		--exp : Experiment Number
		--dateRun: Date Run (e.g. 2012062200)
		--dateValid: Date Valid (e.g. 2012062200)
		-h: This help
		--version: Print the script version

		value:
		Valid value for your search term

		collection:
		SRB Collection to begin the search in (e.g. /home/margom.nirvana/Test) 



	Examples
		SrbTarMetaSearch.py -exp 310 /home/martin.nirvana/Test
		SrbTarMetaSearch.py -dateRun 2012062200 /home/martin.nirvana/Test
		
	"""
# end function


def version():
	print """$Header: /cvs_repository/customers/HPCMP/testbed/NavyPilot/SrbTarMetaSearch.py,v 1.3 2013/04/11 17:18:51 martin Exp $"""
# end function



def main():
	if not CheckPyVersion():
		sys.exit(1)

	directory 	= '.'
	term		= ""
	searchTerm	= ""

	try:
		opts,args = getopt.getopt(sys.argv[1:], "hv", ['version', 'exp', 'dateRun', 'dateValid'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for arg,val in opts:
		if arg == "-h":
			usage()
			sys.exit()
		elif arg == "--version" or arg == "-v":
			version()
			sys.exit()
		elif arg == "--exp":
			searchTerm = "ExperimentNum"
		elif arg == "--dateRun":
			searchTerm = "DateRun"	
		elif arg == "--dateValid":
			searchTErm ="DateValid"
		else:
			print "Invalid argument."
			usage()
			sys.exit()

			
	#end for


	if (PyIsSinit()):
		print "Sinit is OK..."
		status = 0
	else:
		print "No SRB session detected. Have you run Sinit yet?"
		sys.exit(2)

	if len(args) < 2 or len(args) > 2 or searchTerm == "":
		usage()
		sys.exit()
	else:

		# Construct command string cmd
		# 

		if len(args) == 2:
			directory = args[1]
			term = args[0]

		## Truncate hhmmsss from date string and add wildcard		
		if (searchTerm == 'DateRun'):
			term = '*' + term[0:8] + '*'
		elif (searchTerm == 'DateValid'):
			term = '*' + term[0:8] + '*' 

	
		cmd = "Sls -R -policy \"{0}.{1} like {2} AND {3}.{4} like {5}\" {6}".format(SCHEME_NAME, 'Name', searchTerm, SCHEME_NAME, 'Value', term, directory)
 
		(rc,out) = execSMe(cmd)
		print out

		if (rc != 0):
			if len(args) == 2:
				print "Did you use the correct Collection name?"

			print "Error Searching"
			rc = -1
	#end if 
	

#end of function

if __name__=="__main__":
	main()

