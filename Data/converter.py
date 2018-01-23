import datetime as dt
import struct

import numpy as np

import common
from Data import datamodels as dm


def convert(path, name, log, mid_value, unit_factor, location, unpack):
    try:
        d_file = open(path + "/" + name, mode='rb')
    except IOError as e:
        log.reportFailure(e.strerror)
        return
    file = d_file.read()
    file_structure = decode_header(file[:64], mid_value, unit_factor, location)
    file_structure.mid_adc = mid_value
    file_structure.conv_fac = unit_factor

    data_length = len(file)
    expected_width = (data_length / 4) - 32
    if unpack:
        output_matrix = read_raw_data(file)

        if output_matrix[0, -1] == 0:
            output_matrix = output_matrix[0:2, 0:expected_width - 1]

        file_structure.dat1 = common.nptobinary(output_matrix[0,])
        file_structure.dat2 = common.nptobinary(output_matrix[1,])
    file_structure.fsample = 887.7840909
    file_structure.expectedlen = expected_width
    file_structure.filename = name
    file_structure.filepath = path

    return file_structure


def read_raw_data(input_file):
    data_length = len(input_file)
    expected_width = (data_length / 4) - 32
    output_matrix = np.zeros((2, expected_width), dtype=np.uint16)
    index = 0;
    for i in range(64, data_length-68, 4):
        e1, e2 = struct.unpack('>HH', input_file[i:i + 4])
        output_matrix[0, index] = e1
        output_matrix[1, index] = e2
        index += 1

    if output_matrix[0, -1] == 0:
        return output_matrix[0:2, 0:expected_width - 1]
    return output_matrix


def read_header(path, name, log):
    try:
        d_file = open(path + "/" + name, mode='rb')
    except IOError as e:
        log.reportFailure(e.strerror)
        return

    file = decode_header(d_file.read(64), 0, 0, location=None)
    file.filename = name
    file.filepath = path
    return file


def decode_header(header, middle_value, unit_factor, location):
    file = dm.File()
    datetime = dt.datetime.strptime(header[16:32], "%d.%m.%Y %H:%M")
    exact_time, = struct.unpack('>H', header[48:50])
    second_time = float(exact_time) / 625000
    datetime += dt.timedelta(seconds=second_time)

    if location:
        this_location = location
        timezone = this_location.time_zone
        normalized_time = datetime - dt.timedelta(hours=timezone)
        file.date = normalized_time.date()
        file.time = normalized_time.time()
        file.location_id = this_location.id

    file.headerHash = header[0:43]
    file.mid_adc = middle_value
    file.conv_fac = unit_factor
    file.dat1type = "sn elf"
    file.dat2type = "ew elf"
    file.eventscreated = 0
    return file


def convert_deconvolution_mask(file_path):
    try:
        d_file = open(file_path, mode='r')
    except IOError as e:
        # log.reportFailure(e.strerror)
        return

    num_lines = sum(1 for line in d_file)
    freq = np.zeros(num_lines + 1)
    mask = np.zeros(num_lines + 1).astype(complex)
    mask[0] = 1

    iter = 1
    for line in open(file_path, mode='r'):
        strs = line.split(' ')
        freq[iter] = float(strs[0])
        mask[iter] = complex(float(strs[2]), float(strs[3]))
        iter += 1

    return freq, mask







