#!/usr/bin/python
# Sample program or step 8 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import pyewf
import argparse
import hashlib
        
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
  parentPath.append(directoryObject.info.fs_file.name.name)
  for entryObject in directoryObject:
      print str(parentPath)+entryObject.info.name.name
      if entryObject.info.name.name in [".", ".."]:
        continue
      try:
        sub_directory = entryObject.as_directory()
        print sub_directory
        print sub_directory.info.fs_file.name.name
        directoryRecurse(sub_directory,parentPath)
      except IOError:
        pass
  parentPath.pop(-1)
  
        
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
args = argparser.parse_args()
filenames = pyewf.glob(args.imagefile)
dirPath = args.path
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
    
  
    
