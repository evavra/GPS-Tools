import numpy as np
import collections
import datetime as dt
import matplotlib.pyplot as plt


def driver():
    filename = 'RDOM.IGS08.tenv3.txt'
    data_format = 'env'
    component = 'N'
    start = '20141101'
    end = '20190901'
    dates = [dt.datetime.strptime(start, '%Y%m%d'), dt.datetime.strptime(end, '%Y%m%d')]

    gps_data = readUNR(filename, data_format)
    stationTimeSeries(gps_data, component, dates)

# ------------------------- INPUT -------------------------


def readUNR(filename, data_format):

    if data_format == 'xyz':

        # RDOM 98AUG14 1998.6174 -0.244347624362904E+07 -0.442672558603183E+07  0.387861458785039E+07 0.115015240663353E-02 0.186956212545556E-02 0.153421727186364E-02  0.795294219540590E+00 -0.817631106526538E+00 -0.735794538541737E+00   0.0791

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


# ------------------------- OUTPUT -------------------------

def stationTimeSeries(gps_data, component, dates):

    # Get displacements
    plot_displacements = []

    # First find start date
    z_init = 999
    search_date = dates[0]

    while z_init == 999:
        print('Looking for ' + search_date.strftime('%Y-%m-%d'))
        for i in range(len(gps_data.dates)):
            if search_date.strftime('%Y%m%d') == gps_data.dates[i].strftime('%Y%m%d'):
                z_init = gps_data.up[i]
                plot_dates = gps_data.dates[i:]
                plot_data = gps_data.up[i:]

        search_date = search_date + dt.timedelta(days=1)

    print("Initial value: " + str(z_init))

    for value in plot_data:
        plot_displacements.append(value - z_init)

    fig = plt.figure(figsize=(14, 8))
    ax1 = plt.subplot(111)
    plt.grid()
    plt.scatter(plot_dates, plot_displacements, marker='.', zorder=99)

    # ax1.set_aspect(30)
    ax1.set_xlim(dates[0], dates[1])
    # ax1.set_ylim(min(displacements) - 0.005, max(displacements) + 0.005)

    plt.xlabel('Date')
    plt.ylabel('Vertical displacement (m)')

    plt.show()


if __name__ == "__main__":
    driver()
