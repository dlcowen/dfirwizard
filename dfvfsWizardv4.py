import sys
import logging

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import tsk_volume_system
from dfvfs.resolver import resolver
from dfvfs.lib import raw

source_path="image.e01"

path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          path_spec)

if len(type_indicators) > 1:
  raise RuntimeError((
      u'Unsupported source: {0:s} found more than one storage media '
      u'image types.').format(source_path))

if len(type_indicators) == 1:
  path_spec = path_spec_factory.Factory.NewPathSpec(
      type_indicators[0], parent=path_spec)

if not type_indicators:
  # The RAW storage media image type cannot be detected based on
  # a signature so we try to detect it based on common file naming
  # schemas.
  file_system = resolver.Resolver.OpenFileSystem(path_spec)
  raw_path_spec = path_spec_factory.Factory.NewPathSpec(
      definitions.TYPE_INDICATOR_RAW, parent=path_spec)

  glob_results = raw.RawGlobPathSpec(file_system, raw_path_spec)
  if glob_results:
    path_spec = raw_path_spec

volume_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=u'/',
        parent=path_spec)

volume_system = tsk_volume_system.TSKVolumeSystem()
volume_system.Open(volume_path_spec)

volume_identifiers = []
for volume in volume_system.volumes:
  volume_identifier = getattr(volume, 'identifier', None)
  if volume_identifier:
    volume_identifiers.append(volume_identifier)
 
print(u'The following partitions were found:')
print(u'Identifier\tOffset\t\t\tSize')

for volume_identifier in sorted(volume_identifiers):
  volume = volume_system.GetVolumeByIdentifier(volume_identifier)
  if not volume:
    raise RuntimeError(
        u'Volume missing for identifier: {0:s}.'.format(volume_identifier))

  volume_extent = volume.extents[0]
  print(
      u'{0:s}\t\t{1:d} (0x{1:08x})\t{2:d}'.format(
          volume.identifier, volume_extent.offset, volume_extent.size))

  volume_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=u'/'+volume_identifier,
        parent=path_spec)

  mft_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location=u'/$MFT',
        parent=volume_path_spec)

  file_entry = resolver.Resolver.OpenFileEntry(mft_path_spec)


  stat_object = file_entry.GetStat()

  print(u'Inode: {0:d}'.format(stat_object.ino))
  print(u'Inode: {0:s}'.format(file_entry.name))
  outFile = volume_identifier+file_entry.name
  extractFile = open(outFile,'wb')
  file_object = file_entry.GetFileObject()

  data = file_object.read(4096)
  while data:
      extractFile.write(data)
      data = file_object.read(4096)

  extractFile.close
  file_object.close()
  volume_path_spec=""
  mft_path_spec=""
