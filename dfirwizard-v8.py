#!/usr/bin/python
# Sample program or step 8 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import pyewf
import argparse
import hashlib
import csv
        
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
      try:
        sub_directory = entryObject.as_directory()
        parentPath.append(entryObject.info.name.name)
        directoryRecurse(sub_directory,parentPath)
        parentPath.pop(-1)
      except IOError:
        if entryObject.info.meta.size == 0:
          wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),"d41d8cd98f00b204e9800998ecf8427e","da39a3ee5e6b4b0d3255bfef95601890afd80709"])
          continue
        filedata = entryObject.read_random(0,entryObject.info.meta.size)
        md5hash = hashlib.md5()
        md5hash.update(filedata)
        sha1hash = hashlib.sha1()
        sha1hash.update(filedata)
        wr.writerow([int(entryObject.info.meta.addr),'/'.join(parentPath)+entryObject.info.name.name,datetime.datetime.fromtimestamp(entryObject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S'),int(entryObject.info.meta.size),md5hash.hexdigest(),sha1hash.hexdigest()])
        pass
      
  
  
        
argparser = argparse.ArgumentParser(description='Hash all files recursively from a forensic image')
argparser.add_argument(
        '-i', '--image',
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
        default='inventory.csv',
        required=False,
        help='File to write the hashes to'
    )
args = argparser.parse_args()
filenames = pyewf.glob(args.imagefile)
dirPath = args.path
outfile = open(args.output,'w')
outfile.write('"Inode","Full Path","Creation Time","Size","MD5 Hash","SHA1 Hash"\n')
wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
ewf_handle = pyewf.handle()
ewf_handle.open(filenames)
imagehandle = ewf_Img_Info(ewf_handle)

partitionTable = pytsk3.Volume_Info(imagehandle)
for partition in partitionTable:
  print partition.addr, partition.desc, "%ss(%s)" % (partition.start, partition.start * 512), partition.len
  if 'NTFS' in partition.desc:
    filesystemObject = pytsk3.FS_Info(imagehandle, offset=(partition.start*512))
    directoryObject = filesystemObject.open_dir(path=dirPath)
    print directoryObject.info.fs_file.name.name
    directoryRecurse(directoryObject,[])
    
  
    
