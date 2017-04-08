from __future__ import print_function

import sys
import pickle
from operator import add
from pyspark import SparkContext
from csv import reader
import datetime

def groupby_and_count(df, col_idx):
    """
    Return a list of tuples (val_i, count)
    :param df:
    :param col_idx:
    :return:
    """
    return df.map(lambda x: (x[col_idx], 1)).groupByKey().mapValues(lambda x: len(x))

if __name__ == "__main__":
    sc = SparkContext()
    filename = sys.argv[1]
  
    df = sc.textFile(filename, 1).mapPartitions(lambda x: reader(x))
    all_columns = df.first()
    col2idx = dict([(all_columns[i], i) for i in range(len(all_columns))])
    df = df.filter(lambda line: line != all_columns)

    # Overview
    #nrow = df.count()
    #ncol = len(all_columns)
    #print("dataset has {0} rows".format(nrow)) # 5101231
    #print("dataset has {0} cols".format(ncol)) # 24

    # top level function that check if each column in the row are NULL/VALID/INVALID
    def check_row(row, col_func_dict):
        output = []
        for i in range(len(row)):
            if all_columns[i] in col_func_dict:
                output.append(col_func_dict[all_columns[i]](row, i))
            else:
                output.append("VALID")
        return output

    # ASHEN COLUMNS
    ashen_columns = ["BORO_NM",  # 463 blank, 6 vals
                     "ADDR_PCT_CD", # 390 blank, 78 vals
                     "PARKS_NM", # 5093632 blank, 864 vals
                     "HADEVELOPT", # 4848026 blank, 279 vals
                     "X_COORD_CD", # 188146 blank, 69533 vals
                     "Y_COORD_CD", # 188146 blank, 72317 vals
                     "Latitude", # 188146 blank, 112804 vals
                     "Longitude", # 188146 blank, 112808 vals
                     "Lat_Lon"] # 188146 blank, 112827 vals
    #ashen_dict = {}
    #for col in ashen_columns:
    #    ashen_dict[col] = groupby_and_count(df, col2idx[col]).collect()

    # ZYU COLUMNS
    zyu_columns = ["CMPLNT_NUM",       # 0 blank,     5101231 vals
                   "KY_CD",            # 0 blank,     74 vals
                   "OFNS_DESC",        # 18840 blank, 71 vals
                   "PD_CD",            # 4574 blank,  416 vals
                   "PD_DESC",          # 4574 blank,  404 vals
                   "CRM_ATPT_CPTD_CD", # 7 blank,     3 vals
                   "LAW_CAT_CD",       # 0 blank,     3 vals
                   "JURIS_DESC"]       # 0 blank,     25 vals
    #zyu_dict = {}
    #for col in zyu_columns:
    #    zyu_dict[col] = groupby_and_count(df, col2idx[col]).collect()
    #
    #for key in zyu_dict:
    #    print(key, len(zyu_dict[key]))
    #    for item in zyu_dict[key]:
    #        if item[0] == "":
    #            print(key, item)


    xzhang_columns = ['CMPLNT_FR_DT', # 655 null 
                      'CMPLNT_FR_TM', # 45 null
                      'CMPLNT_TO_DT', # 1391478 null
                      'CMPLNT_TO_TM', # 1387785 null
                      'RPT_DT', # 0 null
                      'LOC_OF_OCCUR_DESC', # 1127128 " ", 213 "  "
                      'PREM_TYP_DESC' ] # 33279 null


    all_column = ["BORO_NM",  # 463 blank, 6 vals
                   "ADDR_PCT_CD", # 390 blank, 78 vals
                   "PARKS_NM", # 5093632 blank, 864 vals
                   "HADEVELOPT", # 4848026 blank, 279 vals
                   "X_COORD_CD", # 188146 blank, 69533 vals
                   "Y_COORD_CD", # 188146 blank, 72317 vals
                   "Latitude", # 188146 blank, 112804 vals
                   "Longitude", # 188146 blank, 112808 vals
                   "Lat_Lon", # 188146 blank, 112827 vals
                   "CMPLNT_NUM",       # 0 blank,     5101231 vals
                   "KY_CD",            # 0 blank,     74 vals
                   "OFNS_DESC",        # 18840 blank, 71 vals
                   "PD_CD",            # 4574 blank,  416 vals
                   "PD_DESC",          # 4574 blank,  404 vals
                   "CRM_ATPT_CPTD_CD", # 7 blank,     3 vals
                   "LAW_CAT_CD",       # 0 blank,     3 vals
                   "JURIS_DESC",       # 0 blank,     25 vals
                   "CMPLNT_FR_DT",
                   "CMPLNT_FR_TM",
                   "CMPLNT_TO_DT",
                   "CMPLNT_TO_TM",
                   "RPT_DT",
                   "LOC_OF_OCCUR_DESC",
                   "PREM_TYP_DESC"]
    #all_dict = {}
    #for col in all_column:
    #    all_dict[col] = groupby_and_count(df, col2idx[col]).collect()

    #with open('all_dict', 'wb') as f:
    #    pickle.dump(all_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    def duplicate_key(counts):
        '''
        check if there are duplicate keys
        '''
        key_list = []
        for x in counts.collect():
           key_list.append(x[0][0])
        return (len(key_list) != len(set(key_list)))

    #KY_counts = df.map(lambda x: ((x[6], x[7]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    #PD_counts = df.map(lambda x: ((x[8], x[9]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    #PD_LAW = df.map(lambda x: ((x[8], x[11]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    #PD_KY = df.map(lambda x: ((x[8], x[9], x[6], x[7]),1)).reduceByKey(add).sortBy(lambda x: x[0])

    #print(duplicate_key(KY_counts)) #True
    #print(duplicate_key(PD_counts)) #False
    #print(duplicate_key(PD_LAW))    #False
    #print(duplicate_key(PD_KY))     #True

    #with open('KY_counts', 'wb') as f:
    #    pickle.dump(KY_counts.collect(), f, protocol=pickle.HIGHEST_PROTOCOL)

    #with open('PD_KY', 'wb') as f:
    #    pickle.dump(PD_KY.collect(), f, protocol=pickle.HIGHEST_PROTOCOL)

    # NULL values for each columns
    null_vals_dict = {"BORO_NM":[""],
                 "ADDR_PCT_CD":[""],
                 "PARKS_NM":[""],
                 "HADEVELOPT":[""],
                 "X_COORD_CD":[""],
                 "Y_COORD_CD":[""],
                 "Latitude":[""],
                 "Longitude":[""],
                 "Lat_Lon":[""],
                 "CMPLNT_NUM":[""],
                 "KY_CD":[""],
                 "OFNS_DESC":[""],
                 "PD_CD":[""],
                 "PD_DESC":[""],
                 "CRM_ATPT_CPTD_CD":[""],
                 "LAW_CAT_CD":[""],
                 "JURIS_DESC":[""],
                 "CMPLNT_FR_DT":[""],
                 "CMPLNT_FR_TM":[""],
                 "CMPLNT_TO_DT":[""],
                 "CMPLNT_TO_TM":[""],
                 "RPT_DT":[""],
                 "LOC_OF_OCCUR_DESC":[""],
                 "PREM_TYP_DESC":[""]}

    # column check function
    def general_check_col_func(check_null_func, check_valid_func, row, col_idx):
        if check_null_func(row, col_idx):
            return "NULL"
        elif not check_valid_func(row, col_idx):
            return "INVALID/OUTLIER"
        else:
            return "VALID"


    def general_check_null_func(row, col_idx):
        return all_columns[col_idx] in null_vals_dict and row[col_idx] in null_vals_dict[all_columns[col_idx]]


    def check_loc(loc_str):
        all_numbers = loc_str[1:-1].split(",")
        if len(all_numbers) != 2:
            return False
        for num in all_numbers:
            if not num.replace(' ', '', 1).replace('-', '', 1).replace('.','',1).isdigit():
                return False
        return True

    format_re_dict = {
        "POS_INT": lambda row, col_idx: row[col_idx].isdigit(),
        "FLOAT": lambda row, col_idx: row[col_idx].replace('-', '', 1).replace('.','',1).isdigit(),
        # text should not be purely number?
        "TEXT": lambda row, col_idx: not row[col_idx].replace('-', '', 1).replace('.','',1).isdigit(),
        "LOCATION": lambda row, col_idx: check_loc(row[col_idx])
    }

    # check functions for each columns
    def check_valid_BORO_NM(row, col_idx):
        if not format_re_dict["TEXT"](row, col_idx):
            return False
        elif row[col_idx] not in ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]:
            return False
        else:
            return True

    def check_valid_Latitude(row, col_idx):
        if not format_re_dict["FLOAT"](row, col_idx):
            return False
        elif float(row[col_idx]) < 40.477399 or float(row[col_idx]) > 40.917577:
            return False
        else:
            return True

    def check_valid_Longitude(row, col_idx):
        if not format_re_dict["FLOAT"](row, col_idx):
            return False
        elif float(row[col_idx]) < -74.259090 or float(row[col_idx]) > -73.700272:
            return False
        else:
            return True

    def check_valid_Lat_Lon(row, col_idx):
        if not format_re_dict["LOCATION"](row, col_idx):
            return False
        elif '({0}, {1})'.format(row[col2idx["Latitude"]], row[col2idx["Longitude"]]) == row[col_idx]:
            return False
        else:
            return True


    def check_FR_DT(row, col_idx):
        FR_numbers = row[col_idx].split("/")
        if len(FR_numbers) != 3:
            return False
        try:
            newDate = datetime.datetime(int(FR_numbers[2]),int(FR_numbers[0]),int(FR_numbers[1]))
            return True
        except ValueError:
            return False
        if newDate.year < 2006 or newDate.year > 2015 :
            return False


    def check_TO_DT(row, col_idx):
        FR_numbers = row[col2idx["CMPLNT_FR_DT"]].split("/")
        TO_numbers = row[col_idx].split("/")
        if len(TO_numbers) != 3:
            return False
        try:
            newDate = datetime.datetime(int(TO_numbers[2]),int(TO_numbers[0]),int(TO_numbers[1]))
            return True
        except ValueError:
            return False
        fr_dt = datetime.datetime(int(FR_numbers[2]),int(FR_numbers[0]),int(FR_numbers[1]))
        to_dt = datetime.datetime(int(TO_numbers[2]),int(TO_numbers[0]),int(TO_numbers[1]))
        if not fr_dt < to_dt:
            return False 
        if newDate.year < 2006 or newDate.year > 2015 :
            return False


    def check_RPT_DT(row, col_idx):
        FR_numbers = row[col2idx["CMPLNT_FR_DT"]].split("/")
        RPT_numbers = row[col_idx].split("/")
        if len(RPT_numbers) != 3:
            return False
        try:
            newDate = datetime.datetime(int(RPT_numbers[2]),int(RPT_numbers[0]),int(RPT_numbers[1]))
            return True
        except ValueError:
            return False
        fr_dt = datetime.datetime(int(FR_numbers[2]),int(FR_numbers[0]),int(FR_numbers[1]))
        rpt_dt = datetime.datetime(int(RPT_numbers[2]),int(RPT_numbers[0]),int(RPT_numbers[1]))
        if not fr_dt < rpt_dt:
            return False
        if newDate.year < 2006 or newDate.year > 2015 :
            return False 


    def check_FR_TM(row, col_idx):
        FR_numbers = row[col2idx["CMPLNT_FR_DT"]].split("/")
        FR_TM_numbers = row[col_idx].split(":")
        if len(FR_numbers) != 3:
            return False
        if len(FR_TM_numbers) != 3:
            return False
        try:
            newDate = datetime.datetime(int(FR_numbers[2]),int(FR_numbers[0]),int(FR_numbers[1]),int(FR_TM_numbers[0]),int(FR_TM_numbers[1]),int(FR_TM_numbers[2]))
            return True
        except ValueError:
            return False
        if newDate.year < 2006 or newDate.year > 2015 :
            return False

            
    def check_TO_TM(row, col_idx):
        FR_numbers = row[col2idx["CMPLNT_FR_DT"]].split("/")
        FR_TM_numbers = row[col2idx["CMPLNT_FR_TM"]].split(":")
        TO_numbers = row[col2idx["CMPLNT_TO_DT"]].split("/")
        TO_TM_numbers = row[col_idx].split(":")
        if len(FR_TM_numbers) != 3:
            return False
        if len(FR_numbers) != 3:
            return False
        if len(TO_numbers) != 3:
            return False
        if len(TO_TM_numbers) != 3:
            return False
        try:
            newDate = datetime.datetime(int(TO_numbers[2]),int(TO_numbers[0]),int(TO_numbers[1]),int(TO_TM_numbers[0]),int(TO_TM_numbers[1]),int(TO_TM_numbers[2]))
            return True
        except ValueError:
            return False
        fr_tm = datetime.datetime(int(FR_numbers[2]),int(FR_numbers[0]),int(FR_numbers[1]),int(FR_TM_numbers[0]),int(FR_TM_numbers[1]),int(FR_TM_numbers[2]))
        to_tm = datetime.datetime(int(TO_numbers[2]),int(TO_numbers[0]),int(TO_numbers[1]),int(TO_TM_numbers[0]),int(TO_TM_numbers[1]),int(TO_TM_numbers[2]))
        if not fr_tm < to_tm:
            return False
        if newDate.year < 2006 or newDate.year > 2015 :
            return False

    def check_LOC_DESC(row, col_idx):
        if not format_re_dict["TEXT"](row, col_idx):
            return False

    def check_PREM_DESC(row, col_idx):
        if not format_re_dict["TEXT"](row, col_idx):
            return False


    check_col_func_dict = {
                        # valid text + within 5 district
                        "BORO_NM": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_BORO_NM, row, col_idx),
                        # any valid pos int
                        "ADDR_PCT_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # any valid string
                        "PARKS_NM": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid string
                        "HADEVELOPT": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid pos integer
                        "X_COORD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # any valid pos integer
                        "Y_COORD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # valid float + within NYC
                        "Latitude": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                check_valid_Latitude, row, col_idx),
                        # valid float + within NYC
                        "Longitude": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                 check_valid_Longitude, row, col_idx),
                        # valid loc + should be consistent with previous columns
                        "Lat_Lon": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                               check_valid_Lat_Lon, row, col_idx),
                        # any valid pos int
                        "CMPLNT_NUM": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # any valid pos int
                        "KY_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # any valid string
                        "OFNS_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid pos int
                        "PD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["POS_INT"], row, col_idx),
                        # any valid string
                        "PD_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid string
                        "CRM_ATPT_CPTD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid string
                        "LAW_CAT_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid string
                        "JURIS_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        "CMPLNT_FR_DT": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_FR_DT, row, col_idx),

                        "CMPLNT_TO_DT": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_TO_DT, row, col_idx),

                        "RPT_DT": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_RPT_DT, row, col_idx),

                        "CMPLNT_FR_TM": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_FR_TM, row, col_idx),

                        "LOC_OF_OCCUR_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_LOC_DESC, row, col_idx),
                        "PREM_TYP_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_PREM_DESC, row, col_idx)}
                        
    # check each single ****ing cell in the data frame
    sanity_output = df.map(lambda x: check_row(x, check_col_func_dict)).collect()
    print(sanity_output)

