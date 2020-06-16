#!/usr/bin/env python
import sys
try:
	import os, glob, sys, getopt
	import tempfile 
	import tarfile
	from datetime import datetime
	from SrbRegisterUtil import execMe,execSMe,PyIsSinit,CheckPyVersion
except:
	raise "Check you local Python Version. A minimum Python version required"

""" A script that takes a tar bundle (tar.gz) file as argument, read the file listing, put said tar bundle file into SRB and register metadata """


SCHEME_NAME = "Name_Value"

def usage():
	print """SrbTarManifest.py
	usage: SrbTarManifest.py <option> <file or group of files>
		-h: This help
		-m: Include metadata attribute to my file
		-f: Force flag. Overwrite older version in SRB. 
		--version: Print the script version

	Example
		SrbTarManifest.py 310_archv_1234_440.tar.gz 310_archm_1234_440.tar.gz
		SrbTarManifest.py -f 310_arch*.tar.gz
		SrbTarManifest.py -m -f 310_arch*.tar.gz 
	"""
# end function


def version():
	print """$Header: /cvs_repository/customers/HPCMP/testbed/NavyPilot/SrbTarManifest.py,v 1.6 2013/06/03 20:44:28 martin Exp $"""
# end function


def parseAndRegister(tarfile):
	""" 
	A function to take a well formatted tarfile and register parts of 
	the name as metadata in SRB MCAT database
	
	example: 310_archv_2012062618_2012062700.tar.gz

	parsed:
		ExperimentNum = 310
		OutputType = archv
		DateRun = 2012062618 (parsed to ISO 8601)
		DateValid = 2012062700 (parsed to ISO 8601)
	"""
	rc = 0
	strTarFile = tarfile.replace('.tar.gz','') # chop extension
	lisComp = strTarFile.split('_')
	
	experimentNum = lisComp[0]
	outputType = lisComp[1]
	dateRun = lisComp[2]
	dateValid = lisComp[3]
	
	if (rc == 0):
		(rc,out) = execSMe("Sscheme -w -scheme {0} -val \"Name[0]::ExperimentNum, Value[0]::\"{1}\"\" {2}".format(SCHEME_NAME, experimentNum, tarfile))
	

	if (rc == 0):
		(rc,out) = execSMe("Sscheme -w -scheme {0} -val \"Name[1]::OutputType, Value[1]::\"{1}\"\" {2}".format(SCHEME_NAME, outputType, tarfile))
	

	if (rc == 0):
		(rc,out) = execSMe("Sscheme -w -scheme {0} -val \"Name[2]::DateRun, Value[2]::\"{1}\"\" {2}".format(SCHEME_NAME, dateRun, tarfile))
	
	
	if (rc == 0):
		(rc,out) = execSMe("Sscheme -w -scheme {0} -val \"Name[3]::DateValid, Value[3]::\"{1}\"\" {2}".format(SCHEME_NAME, dateValid, tarfile))
	

	if (rc != 0):
		print "Warning: One or more metadata from tar filename failed to register"


# end function 

def main():

	if not CheckPyVersion():
		sys.exit(1)

	forceFlag = 0
	metadataFlag = 0

	try:
		opts,args = getopt.getopt(sys.argv[1:], "hmfv", ['version'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	for arg,val in opts:
		if arg == "-h":
			usage()
			sys.exit()
		elif arg == "-f":
			forceFlag = 1
		elif arg == "-m":
			metadataFlag = 1
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


	if len(args) > 0:

		print "Stage 1: Sput {0} to SRB current collection".format(' '.join(args))

		# Construct command string cmd
		# with force flag
		#   Sput -f abel.tar.gz .
		# without force flag
		#   Sput abel.tar.gz .
	
		cmd = "Sput " 
		if forceFlag == 1:
			cmd = cmd + "-f "
		cmd = cmd + "{0} .".format(' '.join(args))
		

		(rc,out) = execSMe(cmd)
		if (rc != 0):
			print "Error putting file to SRB!"
			rc = -1
		else:
			print "Put file to SRB successful"
		
		if (rc == 0):
			print "Stage 2: Reading tar file manifest" 
			# for each input file do
			for tarfilenames in args:

				lrealfile = glob.glob(tarfilenames) #extract real file from wildcard filename
				for realfile in lrealfile:
		
					tar = tarfile.open(realfile,'r')
					rows = 0
					#create temporary file
					fd, path = tempfile.mkstemp() 
					manifest = "unix_mode,unix_uid,unix_gid,file_size,date_modify,file_name\n"
					for tarinfo in tar:
						if ((rows % 5000) == 0):
							#bug 1944 memory error if writing too many rows to string manifest
							os.write(fd, manifest)
							manifest = '' 
						#end if

						manifest = manifest + oct(tarinfo.mode)[0:8] + ',' + str(tarinfo.uid)[0:8] + ',' + \
							str(tarinfo.gid)[0:8] + ',' +  str(tarinfo.size)[0:14] + ',' +(datetime.fromtimestamp(tarinfo.mtime)).__str__() + '.0000,' + \
							tarinfo.name[0:256] + '\n'
						rows = rows + 1
					#end for loop

					os.write(fd, manifest)
					os.close(fd)

			
					(rc,out) = execMe("Sscheme -w -scheme TOC -file {0} {1}".format(path, realfile))
					if (rc != 0):
						print "Error writing manifest for {0}".format(realfile)
						
			
					#os.remove(path) #clean up
					if (rc == 0 ) and (metadataFlag == 1):
						rc = parseAndRegister(realfile)
					#end if
				#end-for inside loop
		
			#end-for loop		
			if rc == 0:
				print "Success. Tar.gz manifest has been written to MCAT for all input files"
		#end if passed second gate if (rc == 0)
	#end if 
	

#end of function

if __name__=="__main__":
	main()

