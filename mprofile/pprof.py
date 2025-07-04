# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Builds the profile proto from call stack traces."""

import collections
import gzip
import io

try:
  from mprofile import profile_pb2
except ImportError:
  raise Exception("Error importing pprof protobuf definition. Try installing package with [pprof] extra")

Func = collections.namedtuple('Func', ['name', 'filename', 'start_line'])
Loc = collections.namedtuple('Loc', ['func_id', 'line_number'])


class Builder(object):
  """Builds the profile proto from call stack traces."""

  def __init__(self):
    self._profile = profile_pb2.Profile()
    self._function_map = {}
    self._location_map = {}
    self._string_map = {}
    # string_table[0] in the profile proto must be an empty string.
    self._string_id('')

  def populate_profile(self, samples, profile_type, period_unit, period,
                       duration_ns):
    """Populates call stack traces into a profile proto.

    Args:
      samples: A dict of trace => (count, measurement). A trace is a sequence of
        frames. The leaf frame is at trace[0]. A frame is represented as a tuple
        of (function name, filename, function start line, line number).
      profile_type: A string specifying the profile type, e.g 'CPU' or 'WALL'.
        See https://github.com/google/pprof/blob/master/proto/profile.proto for
        possible profile types.
      period_unit: A string specifying the measurement unit of the sampling
        period, e.g 'nanoseconds'.
      period: An integer specifying the interval between sampled occurrences.
        The measurement unit is specified by the period_unit argument.
      duration_ns: An integer specifying the profiling duration in nanoseconds.
    """
    self._profile.period_type.type = self._string_id(profile_type)
    self._profile.period_type.unit = self._string_id(period_unit)
    self._profile.period = period
    self._profile.duration_nanos = duration_ns
    type1 = self._profile.sample_type.add()
    type1.type = self._string_id('sample')
    type1.unit = self._string_id('count')
    type2 = self._profile.sample_type.add()
    type2.type = self._string_id(profile_type)
    type2.unit = self._string_id(period_unit)

    for trace, (count, value) in samples.items():
      sample = self._profile.sample.add()
      sample.value.append(count)
      sample.value.append(value)
      for frame in trace:
        func_id = self._function_id(frame[0], frame[1], frame[2])
        location_id = self._location_id(func_id, frame[3])
        sample.location_id.append(location_id)

  def emit(self):
    """Returns the profile in gzip-compressed profile proto format."""
    profile = self._profile.SerializeToString()
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb') as f:
      f.write(profile)
    return out.getvalue()

  def _function_id(self, name, filename, start_line):
    """Finds the function ID in the proto, adds the function if not yet exists.

    Args:
      name: A string representing the function name.
      filename: A string representing the file name.
      start_line: The line number in filename on which this function starts.

    Returns:
      An integer representing the unique ID of the function in the profile
      proto.
    """
    name_id = self._string_id(name)
    filename_id = self._string_id(filename)
    func = Func(name_id, filename_id, start_line)

    func_id = self._function_map.get(func)
    if func_id is None:
      # Function ID in profile proto must not be zero.
      func_id = len(self._function_map) + 1
      self._function_map[func] = func_id
      function = self._profile.function.add()
      function.name = name_id
      function.filename = filename_id
      function.start_line = start_line
      function.id = func_id
    return func_id

  def _location_id(self, func_id, line_number):
    """Finds the location ID in the proto, adds the location if not yet exists.

    Args:
      func_id: An integer representing the ID of the corresponding function in
        the profile proto.
      line_number: An integer representing the line number in the source code.

    Returns:
      An integer representing the unique ID of the location in the profile
      proto.
    """
    loc = Loc(func_id=func_id, line_number=line_number)

    location_id = self._location_map.get(loc)
    if location_id is None:
      # Location ID in profile proto must not be zero.
      location_id = len(self._location_map) + 1
      self._location_map[loc] = location_id
      location = self._profile.location.add()
      location.id = location_id
      line = location.line.add()
      line.line = line_number
      line.function_id = func_id
    return location_id

  def _string_id(self, value):
    """Finds the string ID in the proto, adds the string if not yet exists."""
    string_id = self._string_map.get(value)
    if string_id is None:
      string_id = len(self._string_map)
      self._string_map[value] = string_id
      self._profile.string_table.append(value)
    return string_id


def build_heap_pprof(snapshot):
  profile_builder = Builder()
  samples = {}  # trace => (count, measurement)
  for stat in snapshot.statistics('traceback'):
    trace = tuple((frame.name, frame.filename, frame.firstlineno, frame.lineno)
                  for frame in stat.traceback)
    try:
        samples[trace][0] += stat.count
        samples[trace][1] += stat.size
    except KeyError:
        samples[trace] = (stat.count, stat.size)
  profile_builder.populate_profile(samples, 'HEAP', 'bytes', snapshot.sample_rate, 1)
  return profile_builder.emit()
