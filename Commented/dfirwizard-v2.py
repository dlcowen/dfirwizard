#!/usr/bin/python
# Sample program or step 2 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
# Import for manipulation of timestamps into user readable information
import datetime

# Hardcode the name of the image file, without path info has to be in the same directory
imagefile = "Stage2.vhd"
# Creates image object using Img_Info function from TSK and stores it in a variable so image can be accessed
imagehandle = pytsk3.Img_Info(imagefile)
# Retrieves the partition table for the image and retains it in the variable
partitionTable = pytsk3.Volume_Info(imagehandle)
# Use a loop to print up the partition table
for partition in partitionTable:
	# For each entry print the partition address, description, start, start * 512, and the length
	# Partition.start gives the sector it starts at, multiplying by 512 to get the actual start byte
	print partition.addr, partition.desc, '%ss(%s)' % (partition.start, partition.start * 512), partition.len
# Variable to store location of NTFS partition to access file system.  Hard coded start byte of partition
fileSystemObject = pytsk3.FS_Info(imagehandle, offset=65536)
# Obtain the file table ($MFT) file for further access and analysis by acquiring it from fileSystemObject
fileObject = fileSystemObject.open("/$MFT")
# Print metadata of the $MFT file, times will be returned as time from epoch
print "File Inode: ",fileObject.info.meta.addr
print "File Name: ",fileObject.info.name.name
# Because of being returned in epoch must use datetime/strftime to convert into something of use to humans
print "File Creation Time: ", datetime.datetime.fromtimestamp(fileObject.info.meta.crtime).strftime("%Y-%m-%d %H:%M:%S")
# Open a file to output the file from earlier to, 'w' tells python to write.  This is the file handle for writing to output file
outfile = open('DFIRWizard-output', 'w')
# Read the file data into a variable starting at the beginning and ending at the last byte which is the size attribute of the object
# This is probably not the best way to do this
filedata = fileObject.read_random(0, fileObject.info.meta.size)
# Take the data from $MFT that's been stored in filedate and write it the file we opened a minute ago
outfile.write(filedata)