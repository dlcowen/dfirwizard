#!/usr/bin/python
# Sample program or step 5 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import pyewf
        
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
  
filenames = pyewf.glob("SSFCC-Level5.E01")

ewf_handle = pyewf.handle()

ewf_handle.open(filenames)

imagehandle = ewf_Img_Info(ewf_handle)

partitionTable = pytsk3.Volume_Info(imagehandle)
for partition in partitionTable:
  print partition.addr, partition.desc, "%ss(%s)" % (partition.start, partition.start * 512), partition.len
  if 'NTFS' in partition.desc:
    filesystemObject = pytsk3.FS_Info(imagehandle, offset=(partition.start*512))
    fileobject = filesystemObject.open("/$MFT")
    print "File Inode:",fileobject.info.meta.addr
    print "File Name:",fileobject.info.name.name
    print "File Creation Time:",datetime.datetime.fromtimestamp(fileobject.info.meta.crtime).strftime('%Y-%m-%d %H:%M:%S')
    outFileName = str(partition.addr)+fileobject.info.name.name
    print outFileName
    outfile = open(outFileName, 'w')
    filedata = fileobject.read_random(0,fileobject.info.meta.size)
    outfile.write(filedata)
    outfile.close
