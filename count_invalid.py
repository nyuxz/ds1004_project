import pandas as pd
import numpy as np
from itertools import compress
from collections import Counter
import pickle

# read result data
pkl_file = open('sanity_output.pkl', 'rb')
output = pickle.load(pkl_file)
output = pd.DataFrame(output)

header = ['CMPLNT_NUM', 'CMPLNT_FR_DT', 'CMPLNT_FR_TM', 'CMPLNT_TO_DT', 'CMPLNT_TO_TM', 'RPT_DT', 'KY_CD', 'OFNS_DESC', 'PD_CD', 'PD_DESC', 'CRM_ATPT_CPTD_CD', 'LAW_CAT_CD', 'JURIS_DESC', 'BORO_NM', 'ADDR_PCT_CD', 'LOC_OF_OCCUR_DESC', 'PREM_TYP_DESC', 'PARKS_NM', 'HADEVELOPT', 'X_COORD_CD', 'Y_COORD_CD', 'Latitude', 'Longitude', 'Lat_Lon']

list = []
total = output.shape[0]
for i in range(output.shape[1]):
	#Counter(output.iloc[:,i]).keys()
 	column = dict(Counter(output.iloc[:,i]))
 	perc_null = column.get('NULL',0)/total
 	perc_invalid = column.get('INVALID/OUTLIER',0)/total
 	perc_valid = column.get('VALID',0)/total
 	out = [perc_null,perc_invalid,perc_valid]
 	print (header[i])
 	print (['%.5f'%(outi) for outi in out])
 	list.append(out)

total = output.shape[0]
for i in range(output.shape[1]):
	#Counter(output.iloc[:,i]).keys()
	print (header[i])
	print (dict(Counter(output.iloc[:,i])))

