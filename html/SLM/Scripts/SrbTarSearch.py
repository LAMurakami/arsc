#!/usr/bin/env python
try:
	import os, glob, sys, getopt
	import tempfile 
	from SrbRegisterUtil import execMe,execSMe,PyIsSinit,CheckPyVersion
except:
	raise "Check you local Python Version. A minimum Python version required"

""" A script that searches for a filename from TOC.file_name schema """


SCHEME_NAME = "TOC"
COLUMN_NAME = "file_name"

def usage():
	print """SrbTarSearch.py
	usage: SrbTarSearch.py <filename> <folder>
		-h: This help
		--version: Print the script version

	Example
		SrbTarSearch.py 310_archv_20120522_20120524.tar.gz
		SrbTarSearch.py 310_archv_20120522_20120524.tar.gz /home/margom.nirvana
	"""
# end function


def version():
	print """$Header: /cvs_repository/customers/HPCMP/testbed/NavyPilot/SrbTarSearch.py,v 1.4 2013/04/11 17:18:51 martin Exp $"""
# end function



def main():

	if not CheckPyVersion():
		sys.exit(1)

	directory = '.'

	try:
		opts,args = getopt.getopt(sys.argv[1:], "hv", ['version'])
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
	#end for


	if (PyIsSinit()):
		print "Sinit is OK..."
		status = 0
	else:
		print "No SRB session detected. Have you run Sinit yet?"
		sys.exit(2)

	if len(args) == 0:
		usage
		sys.exit()
	elif len(args) > 2:
		usage
		sys.exit()
	else:

		# Construct command string cmd
		# with force flag
		#   Sput -f abel.tar.gz .
		# without force flag
		#   Sput abel.tar.gz .
		searchTerm = '*' + args[0].replace('_','*') + '*'  ## ex: foo_dat.pdf -> *foo*dat.pdf*

		if len(args) == 2:
			directory = args[1]
			
		cmd = "Sls -R -policy \"{0}.{1} like {2}\" {3}".format(SCHEME_NAME, COLUMN_NAME, searchTerm, directory)
 
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

