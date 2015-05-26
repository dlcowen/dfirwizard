#!/usr/bin/python
# Sample program or step 1 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3

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