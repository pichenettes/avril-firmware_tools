#!/usr/bin/python2.5
#
# Copyright 2009 Emilie Gillet.
#
# Author: Emilie Gillet (emilie.o.gillet@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Utility for building a "user" wavetable to be sent by SysEx.

usage:
  python tools/wavetable2sysex/wavetable2sysex.py \
    [--output_file path_to/wavetable.mid] \
    path_to/wavetable_2048_samples.raw
"""

import logging
import optparse
import os
import sys

# Allows the code to be run from the project root directory
sys.path.append('.')

from tools.midi import midifile


def CreateMidifile(
    input_file_name,
    data,
    output_file,
    options):
  size = len(data)
  _, input_file_name = os.path.split(input_file_name)
  comments = [
      'Contains wavetable data for Shruthi-1',
      'Created from %(input_file_name)s' % locals(),
      'Size: %(size)d' % locals()]
  m = midifile.Writer()
  if options.write_comments:
    for comment in comments:
      m.AddTrack().AddEvent(0, midifile.TextEvent(comment))
  t = m.AddTrack()
  t.AddEvent(0, midifile.TempoEvent(120.0))
  event = midifile.SysExEvent(
      options.manufacturer_id,
      options.device_id,
      options.update_command + midifile.Nibblize(data))
  t.AddEvent(1, event)
  f = file(output_file, 'wb')
  if options.syx:
    f.write(''.join(event.raw_message))
  else:
    m.Write(f, format=1)
  f.close()


if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option(
      '-o',
      '--output_file',
      dest='output_file',
      default=None,
      help='Write output file to FILE',
      metavar='FILE')
  parser.add_option(
      '-m',
      '--manufacturer_id',
      dest='manufacturer_id',
      default='\x00\x21\x02',
      help='Manufacturer ID to use in SysEx message')
  parser.add_option(
      '-v',
      '--device_id',
      dest='device_id',
      default='\x00\x02',
      help='Device ID to use in SysEx message')
  parser.add_option(
      '-u',
      '--update_command',
      dest='update_command',
      default='\x03\x00',
      help='Wavetable transfer SysEx command')
  parser.add_option(
      '-s',
      '--syx',
      dest='syx',
      action='store_true',
      default=False,
      help='Produces a .syx file instead of a MIDI file')
  parser.add_option(
      '-c',
      '--comments',
      dest='write_comments',
      action='store_true',
      default=False,
      help='Store additional technical gibberish')

  options, args = parser.parse_args()
  if len(args) < 1:
    logging.fatal('Specify at least one wavetable .bin file!')
    sys.exit(1)
  for f in args:
    data = map(ord, file(f, 'rb').read())
    assert len(data) == 2048
    if not data:
      logging.fatal('Error while loading .bin file')
      sys.exit(2)
    packed_data = []
    for i in xrange(0, 16, 2):
      cycle = data[i * 128:(i + 1)*128]
      packed_data += cycle + [cycle[0]]

    output_file = options.output_file
    extension = '.syx' if options.syx else '.mid'
    if not output_file:
      if '.bin' in f:
        output_file = f.replace('.bin', extension)
      else:
        output_file = f + extension

    CreateMidifile(
        f,
        ''.join(map(chr, packed_data)),
        output_file,
        options)
