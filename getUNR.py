import subprocess
import datetime as dt
import collections

# ----------------------------- API_UNR -----------------------------
# A collection of functions to help with downloading

# ----------------------------- DRIVER -----------------------------


def driver():
    stationInfo_stem = 'http://geodesy.unr.edu/NGLStationPages/'
    stationInfo = ['DataHoldings.txt']
    # stations = '/Users/ellisvavra/Desktop/Thesis/S1_Processing/InSAR_GPS/station.list'
    stations = '/Users/ellisvavra/Thesis/gps/station.list'
    stem = 'http://geodesy.unr.edu/gps_timeseries/tenv3/NA12/'
    suffix = '.NA12.tenv3'
    outDir = 'GPS_data'

    # # Read in list of GPS stations to use
    stationList = readStationList(stations)

    # # Download station info
    wgetFiles(stationInfo_stem, stationInfo, '', outDir)

    # Read station info into memory
    gpsInfo = readStationInfo(outDir + '_' + getTimeStamp() + '/' + stationInfo[0])

    # Download data
    wgetFiles(stem, stationList, suffix, outDir)


# --------------------------- CONFIGURE ----------------------------

def readStationList(stations):
    with open(stations, 'r') as stationFile:
        tempList = stationFile.readlines()

    print()
    print('List of stations: ')

    stationList = []

    for line in tempList:
        if '#' not in line:
            stationList.append(line[:-1])
            print(line[:-1])

    return stationList


def readStationInfo(fileName):

    stationInfo = collections.namedtuple('stationInfo', ['Station', 'Lat', 'Long', 'Hgt', 'X', 'Y', 'Z', 'Dtbeg', 'Dtend', 'Dtmod', 'NumSol', 'StaOrigName'])

    Station = []
    Lat = []
    Long = []
    Hgt = []
    X = []
    Y = []
    Z = []
    Dtbeg = []
    Dtend = []
    Dtmod = []
    NumSol = []
    StaOrigName = []

    with open(fileName, 'r') as tempFile:

        # Data format:
        # Sta  Lat(deg)   Long(deg) Hgt(m)  X(m)           Y(m)         Z(m)          Dtbeg      Dtend      Dtmod      NumSol StaOrigName
        # 00NA -12.4666   130.8440  104.851 -4073662.2759  4712064.7454 -1367874.5096 2008-03-27 2018-09-25 2019-08-15   3157

        count = 0
        for line in tempFile:
            # print(line[:-1])
            if count > 0:
                temp = line.split()
                Station.append(temp[0])
                Lat.append(float(temp[1]))
                Long.append(float(temp[2]))
                Hgt.append(float(temp[3]))
                X.append(float(temp[4]))
                Y.append(float(temp[5]))
                Z.append(float(temp[5]))
                Dtbeg.append(dt.datetime.strptime(temp[6], '%Y-%m-%d'))
                Dtend.append(dt.datetime.strptime(temp[7], '%Y-%m-%d'))
                Dtmod.append(dt.datetime.strptime(temp[8], '%Y-%m-%d'))
                NumSol.append(int(temp[9]))
                StaOrigName.append(temp[10])

                count += 1

        gpsInfo = stationInfo(Station=Station, Lat=Lat, Long=Long, Hgt=Hgt, X=X, Y=Y, Z=Z, Dtbeg=Dtbeg, Dtend=Dtend, Dtmod=Dtmod, NumSol=NumSol, StaOrigName=StaOrigName)

    return gpsInfo


# ----------------------------- OUTPUT -----------------------------

def getTimeStamp():
    timeStamp = dt.datetime.now().strftime('%Y%m%d')
    return timeStamp


def wgetFiles(stem, fileNames, suffix, outDir):
    for fileName in fileNames:
        print('Downloading ' + fileName + suffix + '...')

        subprocess.call('wget -P ' + outDir + '_' + getTimeStamp() + ' ' + stem + fileName + suffix, shell=True)


if __name__ == '__main__':
    driver()
