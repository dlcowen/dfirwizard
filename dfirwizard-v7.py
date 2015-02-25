#!/usr/bin/python
# Sample program or step 6 in becoming a DFIR Wizard!
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
argparser = argparse.ArgumentParser(description='Extract the $MFT from all of the NTFS partitions of an E01')
argparser.add_argument(
        '-i', '--image',
        dest='imagefile',
        action="store",
        type=str,
        default=None,
        required=True,
        help='E01 to extract from'
    )
args = argparser.parse_args()
filenames = pyewf.glob(args.imagefile)
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
    md5hash = hashlib.md5()  
    md5hash.update(filedata)
    print "MD5 Hash",md5hash.hexdigest()
    sha1hash = hashlib.sha1()
    sha1hash.update(filedata)
    print "SHA1 Hash",sha1hash.hexdigest()
    outfile.write(filedata)
    outfile.close
