import pandas as pd
import numpy as np
from itertools import compress
from collections import Counter
import pickle


# read result data
pkl_file = open('sanity_output.pkl', 'rb')
output = pickle.load(pkl_file)
output = pd.DataFrame(output)

# read original data
data = pd.read_csv('data.csv')


check_output = output.copy()
check_data = data.copy()
check_output = check_output.replace(['INVALID/OUTLIER', 'NULL'], True)
check_output = check_output.replace(['VALID'], False)


# header = list(data.columns.values)
#['CMPLNT_NUM', 'CMPLNT_FR_DT', 'CMPLNT_FR_TM', 'CMPLNT_TO_DT', 'CMPLNT_TO_TM', 'RPT_DT', 'KY_CD', 'OFNS_DESC', 'PD_CD', 'PD_DESC', 'CRM_ATPT_CPTD_CD', 'LAW_CAT_CD', 'JURIS_DESC', 'BORO_NM', 'ADDR_PCT_CD', 'LOC_OF_OCCUR_DESC', 'PREM_TYP_DESC', 'PARKS_NM', 'HADEVELOPT', 'X_COORD_CD', 'Y_COORD_CD', 'Latitude', 'Longitude', 'Lat_Lon']


invalid_value = []
for i in range(24):
	a = check_output.iloc[:,i]
	b = check_data.iloc[:,i]
	tmp = list(compress(b,a))
	invalid_value.append(tmp)

for i in range(24):
	print(np.unique(invalid_value[i]))

