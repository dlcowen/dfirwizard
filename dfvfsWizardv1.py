#This sample program goes with the blog post found here:
#http://www.hecfblog.com/2016/04/daily-blog-367-automating-dfir-with.html
#
import sys
import logging

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import tsk_volume_system

source_path="Stage2.vhd"

path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          path_spec)

source_path_spec = path_spec_factory.Factory.NewPathSpec(
            type_indicators[0], parent=path_spec)

volume_system_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=u'/',
        parent=source_path_spec)

volume_system = tsk_volume_system.TSKVolumeSystem()
volume_system.Open(volume_system_path_spec)

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

print(u'')

