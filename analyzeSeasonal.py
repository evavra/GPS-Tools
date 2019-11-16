import numpy as np
import pandas as pd



# ------------------------------------ STEP 1 ------------------------------------
# excel_file = '/Users/ellisvavra/Desktop/Thesis/S1_Processing/GPS_reference_stations/Table_S1_V2.xlsx' # Laptop
excel_file = '/Users/ellisvavra/Thesis/gps/Table_S1_V2.xlsx' # Lorax
target_station = 'RDOM'

# ------------------------------------ STEP 2 ------------------------------------
# Load in table of seasonal deformation characteristics from Amos et al. 2014
seasonalData = pd.read_excel(excel_file, index_col=None, header=0)


# ------------------------------------ STEP 3 ------------------------------------
# We want to first get the amplitude and phase data for our study station
target_data = seasonalData.loc[seasonalData['Station'] == target_station]

# ------------------------------------ STEP 4 ------------------------------------
# Now, use the phase and amplitude from the target station to find other stations with similar seasonal behavior

seasonalData.loc[

seasonalData['Phase (Julian day)'] > target_data.
 and ]


print(temp)


# if __name__ == '__main__':
#     pr
