#!/usr/bin/python
# Sample program or step 11 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import pyewf
import argparse
import hashlib
import csv
import os
import re
import psutil
import admin

        
class ewf_Img_Info(pytsk3.Img_Info):
  def __init__(self, ewf_handle):
    self._ewf_handle = ewf_handle
    super(ewf_Img_Info, self).__init__(
        url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

  def close(self):
    self._ewf_handle.close()

  def read(self, offset, size):
    self._ewf_handle.seek(offset)
    return self._ewf_handle.read(size)

  def get_size(self):
    return self._ewf_handle.get_media_size()

def directoryRecurse(directoryObject, parentPath):
  for entryObject in directoryObject:
      if entryObject.info.name.name in [".", ".."]:
        continue
      #print entryObject.info.name.name
      try:
        f_type = entryObject.info.name.type
        size = entryObject.info.meta.size
      except Exception as error:
          print "Cannot retrieve type or size of",entryObject.info.name.name
          print error.message
          continue
        
      try:

        filepath = '/%s/%s' % ('/'.join(parentPath),entryObject.info.name.name)
        outputPath ='./%s/' % ('/'.join(parentPath))

        if f_type == pytsk3.TSK_FS_NAME_TYPE_DIR:
            sub_directory = entryObject.as_directory()
            print "Entering Directory: %s" % filepath
            parentPath.append(entryObject.info.name.name)
            directoryRecurse(sub_directory,parentPath)
            parentPath.pop(-1)
            print "Leaving Directory: %s" % filepath
            

        elif f_type == pytsk3.TSK_FS_NAME_TYPE_REG and entryObject.info.meta.size != 0:
            searchResult = re.match(args.search,entryObject.info.name.name)
            if not searchResult:
              continue
            #print "File:",parentPath,entryObject.info.name.name,entryObject.info.meta.size
            BUFF_SIZE = 1024 * 1024
            offset=0
            md5hash = hashlib.md5()
            sha1hash = hashlib.sha1()
            if args.extract == True:
                  if not os.path.exists(outputPath):
                    os.makedirs(outputPath)
                  extractFile = open(outputPath+entryObject.info.name.name,'w')
            while offset < entryObject.info.meta.size:
                available_to_read = min(BUFF_SIZE, entryObject.info.meta.size - offset)
                filedata = entryObject.read_random(offset,available_to_read)
                md5hash.update(filedata)
                sha1hash.update(filedata)
                offset += len(filedata)
                if args.extract == True:
                  extractFile.write(filedata)

            if args.extract == True:
                extractFile.close
            wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),md5hash.hexdigest(),sha1hash.hexdigest()])

        elif f_type == pytsk3.TSK_FS_NAME_TYPE_REG and entryObject.info.meta.size == 0:

            wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),"d41d8cd98f00b204e9800998ecf8427e","da39a3ee5e6b4b0d3255bfef95601890afd80709"])

        else:
          print "This went wrong",entryObject.info.name.name,f_type
          
      except IOError as e:
        print e
        continue
  
  
        
argparser = argparse.ArgumentParser(description='Hash files recursively from all NTFS parititions in a live system and optionally extract them')
argparser.add_argument(
        '-i', '--image',
        dest='imagefile',
        action="store",
        type=str,
        default=None,
        required=False,
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
        default='inventory.csv',
        required=False,
        help='File to write the hashes to'
    )
argparser.add_argument(
        '-s', '--search',
        dest='search',
        action="store",
        type=str,
        default='.*',
        required=False,
        help='Specify search parameter e.g. *.lnk'
    )
argparser.add_argument(
        '-e', '--extract',
        dest='extract',
        action="store_true",
        default=False,
        required=False,
        help='Pass this option to extract files found'
    )
args = argparser.parse_args()
if not admin.isUserAdmin():
  admin.runAsAdmin()
  sys.exit()

dirPath = args.path
if not args.search == '.*':
  print "Search Term Provided",args.search 
outfile = open(args.output,'w')
outfile.write('"Inode","Full Path","Creation Time","Size","MD5 Hash","SHA1 Hash"\n')
wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
partitionList = psutil.disk_partitions()
for partition in partitionList:
  imagehandle = pytsk3.Img_Info('\\\\.\\'+partition.device.strip("\\"))
  if 'NTFS' in partition.fstype:
    filesystemObject = pytsk3.FS_Info(imagehandle)
    directoryObject = filesystemObject.open_dir(path=dirPath)
    print "Directory:",dirPath
    directoryRecurse(directoryObject,[])
    
  
    
