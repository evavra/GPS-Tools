import numpy as np
import pandas as pd

seasonalData = pd.read_excel('/Users/ellisvavra/Desktop/Thesis/S1_Processing/GPS_reference_stations/Table_S1_V2.xlsx', index_col=None, header=0)

seasonalData.index[seasonalData['Station'] == 'RDOM']



# if __name__ == '__main__':
#     pr
