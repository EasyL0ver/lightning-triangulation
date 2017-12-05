import struct
import numpy as np
import datamodels as dm
import datetime as dt
import io
import sqlite3
import common


def convert(filePath, fileName, conversionLog, midadc, convFactor, location):
    try:
        d_file = open(filePath + "/" + fileName, mode='rb')
    except IOError as e:
        conversionLog.reportFailure(e.strerror)
        return
    file = d_file.read()
    datastruct = dcdheader(file[:64], midadc, convFactor, location)
    datastruct.mid_adc = midadc
    datastruct.conv_fac = convFactor

    datalen = len(file)
    outputMatrix = readrawdata(file)

    if outputMatrix[0, -1] == 0:
        outputMatrix = outputMatrix[0:2, 0:expectedwidth - 1]

    datastruct.dat1 = common.nptobinary(outputMatrix[0, ])
    datastruct.dat2 = common.nptobinary(outputMatrix[1, ])
    datastruct.fsample = 887.7840909
    datastruct.expectedlen = (datalen - 72) / 4

    return datastruct


def readrawdata(file):
    datalen = len(file)
    expectedwidth = (datalen / 4) - 32
    outputMatrix = np.zeros((2, expectedwidth  ), dtype=np.uint16)
    index = 0;
    for i in range(64, datalen-68, 4):
        e1, e2 = struct.unpack('>HH', file[i:i + 4])
        outputMatrix[0, index] = e1
        outputMatrix[1, index] = e2
        index += 1

    if outputMatrix[0, -1] == 0:
        return outputMatrix[0:2, 0:expectedwidth - 1]
    return outputMatrix


def readheader(filePath, fileName, conversionLog):
    try:
        d_file = open(filePath + "/" + fileName, mode='rb')
    except IOError as e:
        conversionLog.reportFailure(e.strerror)
        return

    file = dcdheader(d_file.read(64), 0, 0, location=None)
    return file


def dcdheader(header, midadc, convfactor, location):
    file = dm.File()
    datetime = dt.datetime.strptime(header[16:32], "%d.%m.%Y %H:%M")
    exacttime, = struct.unpack('>H', header[48:50])
    sectime = float(exacttime) / 625000
    datetime += dt.timedelta(seconds=sectime)

    if location:
        thisloc = location
        timezone = thisloc.time_zone
        normalizedtime = datetime - dt.timedelta(hours=timezone)
        file.date = normalizedtime.date()
        file.time = normalizedtime.time()
        file.location_id = thisloc.id

    file.headerHash = header[0:43]
    file.mid_adc = midadc
    file.conv_fac = convfactor
    file.dat1type = "sn elf"
    file.dat2type = "ew elf"
    file.eventscreated = 0
    return file







