import struct
import numpy as np
import datamodels as dm
import datetime as dt
import io
import sqlite3
import common


def convert(path, name, log, mid_value, unit_factor, location, unpack):
    try:
        d_file = open(path + "/" + name, mode='rb')
    except IOError as e:
        log.reportFailure(e.strerror)
        return
    file = d_file.read()
    data_struct = decode_header(file[:64], mid_value, unit_factor, location)
    data_struct.mid_adc = mid_value
    data_struct.conv_fac = unit_factor

    data_length = len(file)
    expected_width = (data_length / 4) - 32
    if unpack:
        outputMatrix = read_raw_data(file)

        if outputMatrix[0, -1] == 0:
            outputMatrix = outputMatrix[0:2, 0:expected_width - 1]

        #TODO THESE ARE TO BE SWITCHED
        data_struct.dat1 = common.nptobinary(outputMatrix[0, ])
        data_struct.dat2 = common.nptobinary(outputMatrix[1, ])
    data_struct.fsample = 887.7840909
    data_struct.expectedlen = expected_width
    data_struct.filename = name
    data_struct.filepath = path

    return data_struct


def read_raw_data(file):
    data_length = len(file)
    expected_width = (data_length / 4) - 32
    output_matrix = np.zeros((2, expected_width), dtype=np.uint16)
    index = 0;
    for i in range(64, data_length-68, 4):
        e1, e2 = struct.unpack('>HH', file[i:i + 4])
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







