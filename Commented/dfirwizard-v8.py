#!/usr/bin/python
# Sample program or step 8 in becoming a DFIR Wizard!
# No license as this code is simple and free

import sys
import pytsk3
import datetime
# Imports library to work with E01's
import pyewf
import argparse
import hashlib
# Gives ability to write csv files
import csv

# Class inherits pytsk3.Img_Info to use with ewf images
class ewf_Img_Info(pytsk3.Img_Info):
	# Constructor, requires ewf handler to build
	def __init__(self, ewf_handle):
		# Stores ewf_handle as new object in class
		self._ewf_handle = ewf_handle
		# Super class constructor call to parent to make new object and allows overriding of pytsk3 methods
		super(ewf_Img_Info, self).__init__(
				url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)
	# End constructor-------------------------------------------------------------------
	
	# Override methods, pytsk3 methods will not be able to interact with ewf image
	# Close closes the ewf handle
	def close(self):
		self._ewf_handle.close()
	# End of close -----------------------------
	
	# Read allows the ewf image to be read by setting the amount to be read
	def read(self, offset, size):
		self._ewf_handle.seek(offset)
		return self._ewf_handle.read(size)
	# End read--------------------------------------------------------------
	
	# get_size gets the total media size
	def get_size(self):
		return self._ewf_handle.get_media_size()
	# End get_size ----------------------------------------------------
	
# directoryRecurse goes through everything in a directory
def directoryRecurse(directoryObject, parentPath):
	# A loop that goes through each entry in the directory
	for entryObject in directoryObject:
		# if the name is dot or double dot move onto the next, they are folder references
		if entryObject.info.name.name in [".", ".."]:
			continue
		
		# Try to get the file type, try/except so program doesnt crash if problem or no type
		try:
			f_type = entryObject.info.meta.type
		# If the filetype can't be retrieved report it and move on to the next
		except:
			print "Cannot retrieve type of",entryObject.info.name.name
			continue
			
		try:
			# Try to store the full filepath by joining the parentPath and the filename
			filepath = '/%s/%s' % ('/'.join(parentPath),entryObject.info.name.name)
			
			# If the file type is a directory store it as subdirectory then recurse through function through that subdirectory
			if f_type == pytsk3.TSK_FS_META_TYPE_DIR:
				sub_directory = entryObject.as_directory()
				parentPath.append(entryObject.info.name.name)
				# Call directoryRecurse to go through subdirectory passing in sub_directory and parentPath as new starting points
				directoryRecurse(sub_directory, parentPath)
				# Removes the appended info to parentPath so function can continue
				parentPath.pop(-1)
				# Prints the directory path for the subdirectory
				print "Directory: %s" % filepath
			
			# If the file type is a regular file and it has a size the data can be hashed and written
			elif f_type == pytsk3.TSK_FS_META_TYPE_REG and entryObject.info.meta.size !=0:
				# Copy the data in the file to a variable, then hash it
				filedata = entryObject.read_random(0, entryObject.info.meta.size)
				md5hash = hashlib.md5()
				md5hash.update(filedata)
				sha1hash = hashlib.sha1()
				sha1hash.update(filedata)
				# Write the metadata of the file into a csv file
				wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),md5hash.hexdigest(),sha1hash.hexdigest()])
				
			# If the file doesn't have anything in it, it can't be hashed, pull the file info and write hashes manually entered
			elif f_type == pytsk3.TSK_FS_META_TYPE_REG:
				wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),"d41d8cd98f00b204e9800998ecf8427e","da39a3ee5e6b4b0d3255bfef95601890afd80709"])
				
		except IOError as e:
			print e
			continue
			
# End of directoryRecurse ------------------------------------------------------------------------------------

argparser = argparse.ArgumentParser(description='Hash all files recursively from a forensic image')
argparser.add_argument(
			# Choose the flag, long and short version
			'-i', '--image',
			# Variable to store argument in
			dest='imagefile',
			action="store",
			type=str,
			default=None,
			required=True,
			help='E01 to extract from'
		)
argparser.add_argument(
			'-p', '--path',
			dest='path',
			action="store",
			type=str,
			default='/',
			required=False,
			help='Path to recurse from, defaults to /'
		)
argparser.add_argument(
			'-o', '--output',
			dest='output',
			action="store",
			type=str,
			default="inventory.csv",
			required=False,
			help='File to write the hashes to'
		)
		
args = argparser.parse_args()
# Takes the imagefile from argparse and stores it in a variable, glob will piece together an E01 with multiple parts
filenames = pyewf.glob(args.imagefile)
# Stores the directory path entered into arguments
dirPath = args.path
# Creates/opens a new file with name specified in command line to write to
outfile = open(args.output, 'w')
# Write the column headers for the CSV
outfile.write('"Inode","Full Path","Creation Time","Size","MD5 Hash","SHA1 Hash"\n')
# Create a csv writing object
wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
# Create the ewf handler so an image can be accessed
ewf_handle = pyewf.handle()
ewf_handle.open(filenames)
# Creates the handler with the ewf info that can be used with the pytsk3 libraries
imagehandle = ewf_Img_Info(ewf_handle)

# Creates a variable to store partition tables from the ewf image
partitionTable = pytsk3.Volume_Info(imagehandle)
# Iterates through partitions printing their information, looking for NTFS partitions to work with
for partition in partitionTable:
	print partition.addr, partition.desc, "%ss(%s)" % (partition.start, partition.start * 512), partition.len
	if 'NTFS' in partition.desc:
		# store where the file system starts in the partition, multiple partition start by 512 to get byte, not sector it starts on
		filesystemObject = pytsk3.FS_Info(imagehandle, offset=(partition.start*512))
		# store/open the specified directory set in the command line
		directoryObject = filesystemObject.open_dir(path=dirPath)
		print "Directory:",dirPath
		# With the directory path stored and opened it can be passed into directoryRecurse to go through and hash everything
		directoryRecurse(directoryObject,[])