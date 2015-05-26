#!/usr/bin/python
# Sample program 4 in becoming a DFIR Wizard!
# No licenses as this code is simple and free!

import sys
import pytsk3
import datetime
# This is a class of our own written in another file in this directory
import admin

# Checks if running as an admin, if yes it will return false and continue with script, if no will run code under it
if not admin.isUserAdmin():
	# Uses the function runAsAdmin from the admin class to elevate privileges
	admin.runAsAdmin()
	# Shuts down the program
	sys.exit()
# Hardcode the image file, in this case the live drive
imagefile = "\\\\.\\PhysicalDrive0"
# Make an object so that the drive can be accessed using pystsk3 img_info function
imagehandle = pytsk3.Img_Info(imagefile)
# Extract and store the partition table for the live drive
partitionTable = pytsk3.Volume_Info(imagehandle)
# Use a loop to print the partition table data in a meaningful way
for partition in partitionTable:
	# Because partition.start lists the sector we include the *512 entry to give absolute starting byte
	print partition.addr, partition.desc, "%ss(%s)" % (partition.start, partition.start * 512), partition.len	
	# After printing check if NTFS so we can extract $MFT inside loop.  Make sure to indent again, won't work outside of loop
	if  'NTFS' in partition.desc:
		# Set the start of the filesystem so it can be accessed
		filesystemObject = pytsk3.FS_Info(imagehandle, offset = (partition.start * 512))
		# Use a variable to open the $MFT file from the stored filesystem object
		fileobject = filesystemObject.open("/$MFT")
		#Print metadata about the file
		print "File Inode:", fileobject.info.meta.addr
		print "File Name:", fileobject.info.name.name
		print "File Creation Time:", datetime.datetime.fromtimestamp(fileobject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S')
		# Name the output file based on partition # and name so nothing is overwritten.  Makes sure to cast partition addr as a string
		outFileName = str(partition.addr)+fileobject.info.name.name
		print outFileName
		# Create the output file using the created variable above.  Want to write the file data to it so set to 'w'
		outfile = open(outFileName, 'w')
		# Copy the file data, the object information tells it where to end copying
		filedata = fileobject.read_random(0, fileobject.info.meta.size)
		# Write the data to the open file
		outfile.write(filedata)
		# Close the file so you can move on to a new one
		outfile.close