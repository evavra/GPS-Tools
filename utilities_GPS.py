import numpy as np
import collections
import datetime as dt
import matplotlib.pyplot as plt
from getUNR import readStationList
import math


def driver():
    station()


# ------------------------- CONFIGURE -------------------------

def station():
    filename = '/Users/ellisvavra/Thesis/gps/GPS_data_20190904/RDOM.NA12.tenv3'
    data_format = 'env'
    component = 'V'
    start = '20141101'
    end = '20190901'
    theta = 31

    start_end = [dt.datetime.strptime(start, '%Y%m%d'), dt.datetime.strptime(end, '%Y%m%d')]
    gps_data = readUNR(filename, data_format)
    stationTimeSeries(gps_data.dates, gps_data.up, component, start_end)


    plt.xlabel('Date')
    plt.ylabel('Vertical displacement (m)')

    plt.show()


def baseline():
    # CALCULATE ONE BASELINE
    # Load data
    station1 = readUNR('/Users/ellisvavra/Thesis/gps/GPS_data_20190904/RDOM.NA12.tenv3', 'env')
    # station2 = readUNR('GPS_data_20190904/P636.NA12.tenv3', 'env')
    station2 = readUNR('/Users/ellisvavra/Thesis/gps/GPS_data_20190904/CA99.NA12.tenv3', 'env')

    start = '20141108'
    end = '20190801'

    component = 'up'
    outDir = 'BaselinePlots'

    # Compute baseline time series
    baselineDates, baselineChange = calcBaseline(station1, station2, start, end, component)
    fileName = outDir + '/' + station1.station_name[0] + '-' + station2.station_name[0]
    plotBaseline(baselineDates, baselineChange, fileName, component)


def baselineMean():
    # SMOOTH BASELINE WITH MOVING WINDOW MEAN
    # Load data
    station1 = readUNR('/Users/ellisvavra/Thesis/gps/GPS_data_20190904/RDOM.NA12.tenv3', 'env')
    # station2 = readUNR('GPS_data_20190904/P636.NA12.tenv3', 'env')
    station2 = readUNR('/Users/ellisvavra/Thesis/gps/GPS_data_20190904/CA99.NA12.tenv3', 'env')

    start = '20141108'
    end = '20190801'

    component = 'up'
    outDir = 'BaselinePlots'

    # Compute baseline time series
    baselineDates, baselineChange = calcBaseline(station1, station2, start, end, component)
    fileName = outDir + '/' + station1.station_name[0] + '-' + station2.station_name[0]



# ------------------------- READ -------------------------

def readUNR(filename, data_format):

    if data_format == 'xyz':

        xyz = collections.namedtuple('TimeS', ['name', 'coords', 'dt', 'dN', 'dE', 'dU'])

    elif data_format == 'env':
        # [0] station_name     # [10] north(m)
        # [1] YYMMMDD          # [11] u0(m)
        # [2] yyyy_yyyy        # [12] up(m)
        # [3] MJD              # [13] ant(m)
        # [4] week             # [14] sig_e(m)
        # [5] day              # [15] sig_n(m)
        # [6] reflon           # [16] sig_u(m)
        # [7] e0(m)            # [17] corr_en
        # [8] east(m)          # [18] corr_eu
        # [9] n0(m)            # [19] corr_nu

        enz = collections.namedtuple('dataGPS', ['station_name', 'dates', 'yyyy_yyyy', 'MJD', 'week', 'day', 'reflon', 'e0', 'east', 'n0', 'north', 'u0', 'up', 'ant', 'sig_e', 'sig_n', 'sig_u', 'corr_en', 'corr_eu', 'corr_nu'])

        print('Opening ' + str(filename))

        with open(filename) as f:
            lines = f.readlines()[1:]

        station_name = []
        dates = []
        yyyy_yyyy = []
        MJD = []
        week = []
        day = []
        reflon = []
        e0 = []
        east = []
        n0 = []
        north = []
        u0 = []
        up = []
        ant = []
        sig_e = []
        sig_n = []
        sig_u = []
        corr_en = []
        corr_eu = []
        corr_nu = []

        for line in lines:
            temp_line = line.split()

            station_name.append(temp_line[0])
            dates.append(dt.datetime.strptime(temp_line[1], '%y%b%d'))
            yyyy_yyyy.append(float(temp_line[2]))
            MJD.append(int(temp_line[3]))
            week.append(int(temp_line[4]))
            day.append(int(temp_line[5]))
            reflon.append(float(temp_line[6]))
            e0.append(int(temp_line[7]))
            east.append(float(temp_line[8]))
            n0.append(int(temp_line[9]))
            north.append(float(temp_line[10]))
            u0.append(float(temp_line[11]))
            up.append(float(temp_line[12]))
            ant.append(float(temp_line[13]))
            sig_e.append(float(temp_line[14]))
            sig_n.append(float(temp_line[15]))
            sig_u.append(float(temp_line[16]))
            corr_en.append(float(temp_line[17]))
            corr_eu.append(float(temp_line[18]))
            corr_nu.append(float(temp_line[19]))

        data = enz(station_name=station_name, dates=dates, yyyy_yyyy=yyyy_yyyy, MJD=MJD, week=week, day=day, reflon=reflon, e0=e0, east=east, n0=n0, north=north, u0=u0, up=up, ant=ant, sig_e=sig_e, sig_n=sig_n, sig_u=sig_u, corr_en=corr_en, corr_eu=corr_eu, corr_nu=corr_nu)

    return data


# ------------------------- ANALYSIS -------------------------

def calcBaseline(station1, station2, start, end, component):
    # ------------------------- DESCRIPTION: -------------------------
    # Calculates daily baseline lenghts and length changes between two input
    # GPS stations over given epoch using x, y, and z components. This function
    # assumes input data is formatted as described below (Nevada Geodetic
    # Laboratory convention), with the addition of a serial data number column.

    # INPUT:
    #   station1  - Time series data for first GPS station (dataGPS tuple)
    #   station2  - Time series data for second GPS station (dataGPS tuple)
    #   start - Start date of observation period (YYYYMMDD string)
    #   end   - End date of observation period (YYYYMMDD string)

    # OUTPUT:
    #   baselineData - three-column cell array containing dates where both
    #   stations have data, baseline lengths, and

    # Make namedTuple for GPS data
    enz = collections.namedtuple('dataGPS', ['station_name', 'dates', 'yyyy_yyyy', 'MJD', 'week', 'day', 'reflon', 'e0', 'east', 'n0', 'north', 'u0', 'up', 'ant', 'sig_e', 'sig_n', 'sig_u', 'corr_en', 'corr_eu', 'corr_nu'])

    # Find number of days in date range
    start_dt = dt.datetime.strptime(start, '%Y%m%d')
    end_dt = dt.datetime.strptime(end, '%Y%m%d')
    numDays = (end_dt - start_dt).days + 1

    print()
    print('Total of ' + str(numDays) + ' days between ' + start_dt.strftime('%Y%m%d') + ' and ' + end_dt.strftime('%Y%m%d'))

    # Create list of each day in range
    days_in_ts = [start_dt + dt.timedelta(days=x) for x in range(numDays)]
    print()
    print('Making list of dates between ' + days_in_ts[0].strftime('%Y%m%d') + ' and ' + days_in_ts[-1].strftime('%Y%m%d'))

    # -------------------------- STEP 1 --------------------------
    # Find data points in selected date range for each station
    # First intiate empty lists to go into GPS tuple
    station_name = []; dates = []; yyyy_yyyy = []; MJD = []; week = []; day = []; reflon = []; e0 = []; east = []; n0 = []; north = []; u0 = []; up = []; ant = []; sig_e = []; sig_n = []; sig_u = []; corr_en = []; corr_eu = []; corr_nu = []

    print()
    print(station1.station_name[0] + ' has ' + str(len(station1.station_name)) + ' data points between ' + min(station1.dates).strftime('%Y%m%d') + ' and ' + max(station1.dates).strftime('%Y%m%d'))

    # Add data points if they fall into specified date range
    for i in range(len(station1.dates)):
        date_str = station1.dates[i].strftime('%Y%m%d')
        if date_str >= start and date_str <= end:
            station_name.append(station1.station_name[i])
            dates.append(station1.dates[i])
            yyyy_yyyy.append(station1.yyyy_yyyy[i])
            MJD.append(station1.MJD[i])
            week.append(station1.week[i])
            day.append(station1.day[i])
            reflon.append(station1.reflon[i])
            e0.append(station1.e0[i])
            east.append(station1.east[i])
            n0.append(station1.n0[i])
            north.append(station1.north[i])
            u0.append(station1.u0[i])
            up.append(station1.up[i])
            ant.append(station1.ant[i])
            sig_e.append(station1.sig_e[i])
            sig_n.append(station1.sig_n[i])
            sig_u.append(station1.sig_u[i])
            corr_en.append(station1.corr_en[i])
            corr_eu.append(station1.corr_eu[i])
            corr_nu.append(station1.corr_nu[i])

    # Create new data tuple for selected date range
    clipped1 = enz(station_name=station_name, dates=dates, yyyy_yyyy=yyyy_yyyy, MJD=MJD, week=week, day=day, reflon=reflon, e0=e0, east=east, n0=n0, north=north, u0=u0, up=up, ant=ant, sig_e=sig_e, sig_n=sig_n, sig_u=sig_u, corr_en=corr_en, corr_eu=corr_eu, corr_nu=corr_nu)

    print(clipped1.station_name[0] + ' has ' + str(len(clipped1.station_name)) + ' data points between ' + clipped1.dates[0].strftime('%Y%m%d') + ' and ' + clipped1.dates[-1].strftime('%Y%m%d'))

    print()

    for i in range(len(clipped1.dates)):
        print(station_name[i] + ' ' + dates[i].strftime('%Y%m%d')
             + ' ' + str(yyyy_yyyy[i])
             + ' ' + str(MJD[i])
             + ' ' + str(week[i])
             + ' ' + str(day[i])
             + ' ' + str(reflon[i])
             + ' ' + str(e0[i])
             + ' ' + str(east[i])
             + ' ' + str(n0[i])
             + ' ' + str(north[i])
             + ' ' + str(u0[i])
             + ' ' + str(up[i])
             + ' ' + str(ant[i])
             + ' ' + str(sig_e[i])
             + ' ' + str(sig_n[i])
             + ' ' + str(sig_u[i])
             + ' ' + str(corr_en[i])
             + ' ' + str(corr_eu[i])
             + ' ' + str(corr_nu[i]))

    # Reset temporary lists for second station
    station_name = []; dates = []; yyyy_yyyy = []; MJD = []; week = []; day = []; reflon = []; e0 = []; east = []; n0 = []; north = []; u0 = []; up = []; ant = []; sig_e = []; sig_n = []; sig_u = []; corr_en = []; corr_eu = []; corr_nu = []

    print()
    print(station2.station_name[0] + ' has ' + str(len(station2.station_name)) + ' data points between ' + min(station2.dates).strftime('%Y%m%d') + ' and ' + max(station2.dates).strftime('%Y%m%d'))

    # Add data points if they fall into specified date range
    for i in range(len(station2.dates)):
        date_str = station2.dates[i].strftime('%Y%m%d')
        if date_str >= start and date_str <= end:
            station_name.append(station2.station_name[i])
            dates.append(station2.dates[i])
            yyyy_yyyy.append(station2.yyyy_yyyy[i])
            MJD.append(station2.MJD[i])
            week.append(station2.week[i])
            day.append(station2.day[i])
            reflon.append(station2.reflon[i])
            e0.append(station2.e0[i])
            east.append(station2.east[i])
            n0.append(station2.n0[i])
            north.append(station2.north[i])
            u0.append(station2.u0[i])
            up.append(station2.up[i])
            ant.append(station2.ant[i])
            sig_e.append(station2.sig_e[i])
            sig_n.append(station2.sig_n[i])
            sig_u.append(station2.sig_u[i])
            corr_en.append(station2.corr_en[i])
            corr_eu.append(station2.corr_eu[i])
            corr_nu.append(station2.corr_nu[i])

    # Create new data tuple for selected date range
    clipped2 = enz(station_name=station_name, dates=dates, yyyy_yyyy=yyyy_yyyy, MJD=MJD, week=week, day=day, reflon=reflon, e0=e0, east=east, n0=n0, north=north, u0=u0, up=up, ant=ant, sig_e=sig_e, sig_n=sig_n, sig_u=sig_u, corr_en=corr_en, corr_eu=corr_eu, corr_nu=corr_nu)

    print(clipped2.station_name[0] + ' has ' + str(len(clipped2.station_name)) + ' data points between ' + clipped2.dates[0].strftime('%Y%m%d') + ' and ' + clipped2.dates[-1].strftime('%Y%m%d'))

    for i in range(len(clipped2.dates)):
        print(station_name[i] + ' ' + dates[i].strftime('%Y%m%d')
             + ' ' + str(yyyy_yyyy[i])
             + ' ' + str(MJD[i])
             + ' ' + str(week[i])
             + ' ' + str(day[i])
             + ' ' + str(reflon[i])
             + ' ' + str(e0[i])
             + ' ' + str(east[i])
             + ' ' + str(n0[i])
             + ' ' + str(north[i])
             + ' ' + str(u0[i])
             + ' ' + str(up[i])
             + ' ' + str(ant[i])
             + ' ' + str(sig_e[i])
             + ' ' + str(sig_n[i])
             + ' ' + str(sig_u[i])
             + ' ' + str(corr_en[i])
             + ' ' + str(corr_eu[i])
             + ' ' + str(corr_nu[i]))

    # -------------------------- STEP 2 --------------------------
    # Align both station datasets adding empty spacer lists for dates with no data

    # Set loop-independent index for GPS data arrays.
    j1 = 0
    j2 = 0
    save_j1 = 0
    save_j2 = 0

    # Initialize empty arrays for aligned data
    station_name = []; dates = []; yyyy_yyyy = []; MJD = []; week = []; day = []; reflon = []; e0 = []; east = []; n0 = []; north = []; u0 = []; up = []; ant = []; sig_e = []; sig_n = []; sig_u = []; corr_en = []; corr_eu = []; corr_nu = []

    while len(corr_nu) < numDays:
        station_name.append([])
        dates.append([])
        yyyy_yyyy.append([])
        MJD.append([])
        week.append([])
        day.append([])
        reflon.append([])
        e0.append([])
        east.append([])
        n0.append([])
        north.append([])
        u0.append([])
        up.append([])
        ant.append([])
        sig_e.append([])
        sig_n.append([])
        sig_u.append([])
        corr_en.append([])
        corr_eu.append([])
        corr_nu.append([])

    print()
    print('Confirming length of empty lists is equal to number of days in date range: ' + str(len(reflon)) + ' = ' + str(numDays))

    # Align GPS data arrays to have indexing consistent with the selected date range. Days with no GPS data are left empty.
    print()
    print('Number of data points from ' + clipped1.station_name[0] + ': ' + str(len(clipped1.yyyy_yyyy)))

    for i in range(len(days_in_ts)):
        station_name[i] = clipped1.station_name[0]

        while j1 < len(clipped1.dates):
            if days_in_ts[i].strftime('%Y%m%d') == clipped1.dates[j1].strftime('%Y%m%d'):
                # print(days_in_ts[i].strftime('%Y%m%d') + ' == ' + clipped1.dates[j1].strftime('%Y%m%d'))

                # Add all the data to the new tuple
                # print('Adding data for ' + clipped1.dates[j1].strftime('%Y%m%d') + ' to [' + str(i) + '] ')
                dates[i] = clipped1.dates[j1]
                yyyy_yyyy[i] = clipped1.yyyy_yyyy[j1]
                MJD[i] = clipped1.MJD[j1]
                week[i] = clipped1.week[j1]
                day[i] = clipped1.day[j1]
                reflon[i] = clipped1.reflon[j1]
                e0[i] = clipped1.e0[j1]
                east[i] = clipped1.east[j1]
                n0[i] = clipped1.n0[j1]
                north[i] = clipped1.north[j1]
                u0[i] = clipped1.u0[j1]
                up[i] = clipped1.up[j1]
                ant[i] = clipped1.ant[j1]
                sig_e[i] = (clipped1.sig_e[j1])
                sig_n[i] = clipped1.sig_n[j1]
                sig_u[i] = clipped1.sig_u[j1]
                corr_en[i] = clipped1.corr_en[j1]
                corr_eu[i] = clipped1.corr_eu[j1]
                corr_nu[i] = clipped1.corr_nu[j1]

                # Save index of most recently mathched data point
                save_j1 = j1

                # Move to next data point
                j1 += 1

                # print(up[:i])

                break

            elif days_in_ts[i].strftime('%Y%m%d') != clipped1.dates[j1].strftime('%Y%m%d'):
                # print('Checking next data point')
                j1 += 1

        # if up[i] == []:
            # print(station_name[i] + ' has no data on ' + days_in_ts[i].strftime('%Y%m%d'))

        if j1 == len(clipped1.dates):
                dates[i] = np.nan
                yyyy_yyyy[i] = np.nan
                MJD[i] = np.nan
                week[i] = np.nan
                day[i] = np.nan
                reflon[i] = np.nan
                e0[i] = np.nan
                east[i] = np.nan
                n0[i] = np.nan
                north[i] = np.nan
                u0[i] = np.nan
                up[i] = np.nan
                ant[i] = np.nan
                sig_e[i] = np.nan
                sig_n[i] = np.nan
                sig_u[i] = np.nan
                corr_en[i] = np.nan
                corr_eu[i] = np.nan
                corr_nu[i] = np.nan

        # Start search for next date after last matched date
        j1 = save_j1

    aligned1 = enz(station_name=station_name, dates=dates, yyyy_yyyy=yyyy_yyyy, MJD=MJD, week=week, day=day, reflon=reflon, e0=e0, east=east, n0=n0, north=north, u0=u0, up=up, ant=ant, sig_e=sig_e, sig_n=sig_n, sig_u=sig_u, corr_en=corr_en, corr_eu=corr_eu, corr_nu=corr_nu)

    # ----------------- Repeat for second station -----------------
    # Initialize empty arrays for aligned data
    station_name = []; dates = []; yyyy_yyyy = []; MJD = []; week = []; day = []; reflon = []; e0 = []; east = []; n0 = []; north = []; u0 = []; up = []; ant = []; sig_e = []; sig_n = []; sig_u = []; corr_en = []; corr_eu = []; corr_nu = []

    while len(corr_nu) < numDays:
        station_name.append(([]))
        dates.append([])
        yyyy_yyyy.append([])
        MJD.append([])
        week.append([])
        day.append([])
        reflon.append([])
        e0.append([])
        east.append([])
        n0.append([])
        north.append([])
        u0.append([])
        up.append([])
        ant.append([])
        sig_e.append([])
        sig_n.append([])
        sig_u.append([])
        corr_en.append([])
        corr_eu.append([])
        corr_nu.append([])

    print()
    print('Confirming length of empty lists is equal to number of days in date range: ' + str(len(reflon)) + ' = ' + str(numDays))
    print()
    print('Number of data points from ' + clipped2.station_name[0] + ': ' + str(len(clipped2.yyyy_yyyy)))

    for i in range(len(days_in_ts)):
        station_name[i] = clipped2.station_name[0]

        while j2 < len(clipped2.dates):
            if days_in_ts[i].strftime('%Y%m%d') == clipped2.dates[j2].strftime('%Y%m%d'):
                # print(days_in_ts[i].strftime('%Y%m%d') + ' == ' + clipped2.dates[j2].strftime('%Y%m%d'))

                # Add all the data to the new tuple
                # print('Adding data for ' + clipped2.dates[j2].strftime('%Y%m%d') + ' to [' + str(i) + '] ')

                dates[i] = clipped2.dates[j2]
                yyyy_yyyy[i] = clipped2.yyyy_yyyy[j2]
                MJD[i] = clipped2.MJD[j2]
                week[i] = clipped2.week[j2]
                day[i] = clipped2.day[j2]
                reflon[i] = clipped2.reflon[j2]
                e0[i] = clipped2.e0[j2]
                east[i] = clipped2.east[j2]
                n0[i] = clipped2.n0[j2]
                north[i] = clipped2.north[j2]
                u0[i] = clipped2.u0[j2]
                up[i] = clipped2.up[j2]
                ant[i] = clipped2.ant[j2]
                sig_e[i] = (clipped2.sig_e[j2])
                sig_n[i] = clipped2.sig_n[j2]
                sig_u[i] = clipped2.sig_u[j2]
                corr_en[i] = clipped2.corr_en[j2]
                corr_eu[i] = clipped2.corr_eu[j2]
                corr_nu[i] = clipped2.corr_nu[j2]

                # Save index of most recently mathched data point
                save_j2 = j2

                # Move to next data point
                j2 += 1

                break

            elif days_in_ts[i].strftime('%Y%m%d') != clipped2.dates[j2].strftime('%Y%m%d'):
                j2 += 1


        if j2 == len(clipped2.dates):
                dates[i] = np.nan
                yyyy_yyyy[i] = np.nan
                MJD[i] = np.nan
                week[i] = np.nan
                day[i] = np.nan
                reflon[i] = np.nan
                e0[i] = np.nan
                east[i] = np.nan
                n0[i] = np.nan
                north[i] = np.nan
                u0[i] = np.nan
                up[i] = np.nan
                ant[i] = np.nan
                sig_e[i] = np.nan
                sig_n[i] = np.nan
                sig_u[i] = np.nan
                corr_en[i] = np.nan
                corr_eu[i] = np.nan
                corr_nu[i] = np.nan

        # Start search for next date after last matched date
        j2 = save_j2

    aligned2 = enz(station_name=station_name, dates=dates, yyyy_yyyy=yyyy_yyyy, MJD=MJD, week=week, day=day, reflon=reflon, e0=e0, east=east, n0=n0, north=north, u0=u0, up=up, ant=ant, sig_e=sig_e, sig_n=sig_n, sig_u=sig_u, corr_en=corr_en, corr_eu=corr_eu, corr_nu=corr_nu)


    # Calculate the change in GPS station displacement during the observation period. First, find the first data point
    initialDispE1 = np.nan;
    initialDispE2 = np.nan;    
    initialDispN1 = np.nan;
    initialDispN2 = np.nan;    
    initialDispV1 = np.nan;
    initialDispV2 = np.nan;
    i = 0;

    while math.isnan(initialDispE1):
        # Start from first day in time series. If tested time series date has data, set this to be the reference (position = 0).
        if math.isnan(aligned1.east[i]) == False:
            initialDispE1 = aligned1.east[i]
            initialDispN1 = aligned1.north[i]
            initialDispV1 = aligned1.up[i]
        else:
            i += 1

    # Reset for second station
    i = 0;
    while math.isnan(initialDispE2):
        # Start from first day in time series. If tested time series date has data, set this to be the reference (position = 0).
        if math.isnan(aligned2.east[i]) == False:
            initialDispE2 = aligned2.east[i]
            initialDispN2 = aligned2.north[i]
            initialDispV2 = aligned2.up[i]
        else:
            i += 1


    print('Intial displacements for ' + aligned1.station_name[i] + ': ' + str(initialDispE1) + ', ' + str(initialDispN1) + ', ' + str(initialDispV1))
    print('Intial displacements for ' + aligned2.station_name[i] + ': ' + str(initialDispE2) + ', ' + str(initialDispN2) + ', ' + str(initialDispV2))


    # Create new list for incremental GPS displacements
    baselineDates = []
    dispE1 = []
    dispE2 = []
    dispN1 = []
    dispN2 = []
    dispV1 = []
    dispV2 = []

    # Subtract initial displacement values for each 
    for i in range(len(days_in_ts)):
        # If there is GPS data for both stations on a given date, subtract the initial displacement value and append date and net displacement to new lists
        if math.isnan(aligned1.east[i]) == False and math.isnan(aligned2.east[i]) == False:
            baselineDates.append(days_in_ts[i])
            dispE1.append(aligned1.east[i] - initialDispE1)
            dispE2.append(aligned2.east[i] - initialDispE2)
            dispN1.append(aligned1.north[i] - initialDispN1)
            dispN2.append(aligned2.north[i] - initialDispN2)
            dispV1.append(aligned1.up[i] - initialDispV1)
            dispV2.append(aligned2.up[i] - initialDispV2)

            # print('Change in ' + aligned1.station_name[i] + '-' + aligned2.station_name[i] + ' baseline length from ' + days_in_ts[0].strftime('%Y%m%d') + ' to ' + days_in_ts[i].strftime('%Y%m%d') + ': ' + str(baselineChange[-1]) + ' m')


    # Compute baseline lengths for given period.
    baselineChange = []
    for i in range(len(baselineDates)):
        if component == 'true':
            baselineChange.append(np.sqrt((dispE1[i] - dispE2[i])**2 + (dispN1[i] - dispN2[i])**2 + (dispV1[i] - dispV2[i])**2))

        elif component == 'east':
            baselineChange.append(dispE1[i] - dispE2[i])

        elif component == 'north':
            baselineChange.append(dispN1[i] - dispN2[i])

        elif component == 'up':
            baselineChange.append(dispV1[i] - dispV2[i])

            print(dispV1[i], dispV2[i], baselineChange[-1])

    return baselineDates, baselineChange


def windowMean(baselineData, windowSize):
    smoothedData = []



# ------------------------- OUTPUT -------------------------

def proj2LOS(gps_data, theta):

    gps_los=[]

    for gps_z in gps_data:
        gps_los.append(gps_z * np.sin(theta * np.pi / 180))
        # print(str(gps_z) + ' -> ' + str(gps_los[-1]))
        # print(gps_z / np.sin(theta * np.pi / 180))

    return gps_los


def stationTimeSeries(dates, gps_data, component, start_end):

    # Get displacements
    plot_displacements=[]

    # First find start date
    z_init=999
    search_date=start_end[0]

    while z_init == 999:
        print('Looking for ' + search_date.strftime('%Y-%m-%d'))
        for i in range(len(dates)):
            if search_date.strftime('%Y%m%d') == dates[i].strftime('%Y%m%d'):
                plot_dates=dates[i:]
                print('GPS time series start: ' + str(plot_dates[0]))
                plot_data=gps_data[i:]
                z_init=gps_data[i]
                break

        search_date=search_date + dt.timedelta(days=1)

    search_date=search_date - dt.timedelta(days=1)
    print("Initial value: " + str(z_init))

    for value in plot_data:
        plot_displacements.append(value - z_init)

    # fig=plt.figure(figsize=(14, 8))
    ax1=plt.subplot(111)
    plt.grid()
    ax1.scatter(plot_dates, plot_displacements, marker='.', zorder=99)

    # ax1.set_aspect(30)
    ax1.set_xlim(start_end[0], start_end[1])
    # ax1.set_ylim(min(plot_displacements) - 0.005, max(plot_displacements) + 0.005)

    # plt.xlabel('Date')
    # plt.ylabel('Vertical displacement (m)')

    # plt.show()


def plotBaseline(baselineDates, baselineChange, fileName, component):

    fig = plt.figure(figsize=(14, 8))
    ax1 = plt.subplot(111)
    plt.grid()
    ax1.scatter(baselineDates, baselineChange, marker='.', zorder=99)
    # ax1.set_aspect(30)
    ax1.set_xlim(baselineDates[0], baselineDates[-1])
    # ax1.set_ylim(min(baselineChange) - 0.0005, max(baselineChange) + 0.0005)
    plt.title(component)
    plt.xlabel('Date')
    plt.ylabel('Length change (m)')

    plt.show()
    # plt.savefig(fileName + '.eps')
    # plt.close()





if __name__ == "__main__":
    driver()

   