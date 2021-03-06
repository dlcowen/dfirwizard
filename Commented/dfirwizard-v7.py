#!/usr/bin/python
# Sample program or step 5 in becoming a DFIR Wizard!
# No license as this code is simple and free!

import sys
import pytsk3
import datetime
# this library part of libewf is what allows us to access expert witness format images
import pyewf
import argparse
import hashlib

# Creates an Img_Info object for ewf, based on pytsk3's library for image info
# Class inherits base classes of pytsk3.Img_Info
class ewf_Img_Info(pytsk3.Img_Info):
	# Class constructor, takes itself and ewf_handle object from code below?
	def __init__(self, ewf_handle):
		# stores ewf_handle in class as new variable
		self._ewf_handle = ewf_handle
		super(ewf_Img_Info, self).__init__(
			url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)
	
	# The following methods override pytsk3's Img_Info methods which would not know how to handle the e01 image
	# close Closes a ewf object
	def close(self):
		self._ewf_handle.close()
	# end of close -----------------------------------
	
	# read allows an e01 file to be opened/read by specifying where the file system info is on the image
	def read(self, offset, size):
		self._ewf_handle.seek(offset)
		return self._ewf_handle.read(size)
	# end of read ------------------------------------------------
	
	# get_size gets the size of the image
	def get_size(self):
		return self._ewf_handle.get_media_size()

# Create an argparse object so command line arguments can be used
argparser = argparse.ArgumentParser(description='Extract the $MFT from all of the NTFS partitions of an E01')
# Add an argument for the image to be accessed
argparser.add_argument(
			'-i', '--image', # Identifies what the argument is, user can use -i or --image to pass in the filename
			dest='imagefile', # Dest tells what variable to store the argument in
			action='store', # What to do with the argument, here we want to store the argument in the variable
			type=str, # What type of variable to store it as
			default=None, # Default value, here we do not have one
			required=True, # If not entered program will not run, will print out help
			help='E01 to extract from')
# Save the arguments to an object
args = argparser.parse_args()
	
# Get the filename from the argument object		
filenames = pyewf.glob(args.imagefile)

# Opening a handle for the image, creating a new pyewf object
ewf_handle = pyewf.handle()

ewf_handle.open(filenames)

# Create a new Img_Info object using self created class as this is not in the ewf library
imagehandle = ewf_Img_Info(ewf_handle)

# Stores the partition table from the image in a list/array
partitionTable = pytsk3.Volume_Info(imagehandle)

# Iterates through each partition in the previously stored partition table and prints information about it to the console
for partition in partitionTable:
	print partition.addr, partition.desc, "%ss(%s)" % (partition.start, partition.start * 512), partition.len
	# If the partition is labeled as NTFS it uses the imagehandle and offset to access the file system
	if 'NTFS' in partition.desc:
		filesystemObject = pytsk3.FS_Info(imagehandle, offset =(partition.start *512))
		# Opens $MFT in the file system
		fileobject = filesystemObject.open("/$MFT")
		# Prints metadata about $MFT
		print "File Inode:", fileobject.info.meta.addr
		print "File Name:", fileobject.info.name.name
		print "File Creation Time:", datetime.datetime.fromtimestamp(fileobject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S')
		# Creates a filename combining the partition # and files name then prints it to the console
		outFileName = str(partition.addr) + fileobject.info.name.name
		print outFileName
		# Creates/opens a file to write to using the file name specified above
		outfile = open(outFileName, 'w')
		# Stores the data in the file opened above starting at beginning of file and ending at last byte
		filedata = fileobject.read_random(0, fileobject.info.meta.size)
		# Creates md5 hash object
		md5hash = hashlib.md5()
		# Hashes the data of the specified variable filedata
		md5hash.update(filedata)
		# Prints the md5 hash out in hexidecimal form
		print "MD5 Hash",md5hash.hexdigest()
		# Creates a sha1 hash object
		sha1hash = hashlib.sha1()
		# Hashes the data in filedata using sha1
		sha1hash.update(filedata)
		# Prints the sha1 hash out in hexidecimal form
		print "SHA1 Hash",sha1hash.hexdigest()
		# Writes the date stored in filedata to the new file created
		outfile.write(filedata)
		# Closes the file the data was copied to
		outfile.close