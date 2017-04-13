from __future__ import print_function

import sys
import pickle
from operator import add
from pyspark import SparkContext
from csv import reader
from datetime import datetime

def groupby_and_count(df, col_idx):
    """
    Return a list of tuples (val_i, count)
    :param df:
    :param col_idx:
    :return:
    """
    return df.map(lambda x: (x[col_idx], 1)).groupByKey().mapValues(lambda x: len(x))


# boro_dist = groupby_and_count(df, col2idx["BORO_NM"])
# boro_dist = boro_dist.collect()
# boro_dist
# [('BRONX', 1103514), ('', 463), ('STATEN ISLAND', 243790), ('BROOKLYN', 1526213), ('MANHATTAN', 1216249), ('QUEENS', 1011002)]


def date_hisogram(df, col_idx):
    """
    Function that takes in a spark rdd of data and return the count of rows for each year
    :param df:
    :return:
    """
    min_date = datetime.strptime("01/01/2006", "%m/%d/%Y")
    date_col = col_idx['RPT_DT']
    def get_date(row):
        if len(row[date_col]) < 4:
            return None
        else:
            date_obj = datetime.strptime(row[date_col], "%m/%d/%Y")
            if date_obj <= min_date:
                return None
            else:
                return date_obj
    return df.map(lambda x: (get_date(x), 1)).groupByKey().mapValues(lambda x: len(x))


def year_hisogram(df, col_idx):
    """
    Function that takes in a spark rdd of data and return the count of rows for each day
    :param df:
    :return:
    """
    report_date = col_idx['RPT_DT']
    def get_year(row):
        if len(row[report_date]) < 4:
            return 2004
        else:
            year = int(row[report_date][-4:])
            if year <= 2004:
                return 2004
            else:
                return year
    return df.map(lambda x: (get_year(x), 1)).groupByKey().mapValues(lambda x: len(x))

#year_df = year_hisogram(df, col2idx)
#year_df = year_df.collect()
#year_df
#[(2010, 509725), (2011, 498198), (2012, 504128), (2013, 494958), (2004, 8670), (2014, 490363), (2005, 10767), (2015, 468576), (2006, 539024), (2007, 537201), (2008, 528675), (2009, 510946)]






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

    all_column = ["BORO_NM",           # 463 blank,     6 vals
                  "ADDR_PCT_CD",       # 390 blank,     78 vals
                  "PARKS_NM",          # 5093632 blank, 864 vals
                  "HADEVELOPT",        # 4848026 blank, 279 vals
                  "X_COORD_CD",        # 188146 blank,  69533 vals
                  "Y_COORD_CD",        # 188146 blank,  72317 vals
                  "Latitude",          # 188146 blank,  112804 vals
                  "Longitude",         # 188146 blank,  112808 vals
                  "Lat_Lon",           # 188146 blank,  112827 vals
                  "CMPLNT_NUM",        # 0 blank,       5101231 vals
                  "KY_CD",             # 0 blank,       74 vals
                  "OFNS_DESC",         # 18840 blank,   71 vals
                  "PD_CD",             # 4574 blank,    416 vals
                  "PD_DESC",           # 4574 blank,    404 vals
                  "CRM_ATPT_CPTD_CD",  # 7 blank,       3 vals
                  "LAW_CAT_CD",        # 0 blank,       3 vals
                  "JURIS_DESC",        # 0 blank,       25 vals
                  "CMPLNT_FR_DT",      # 655 blank,     6372 vals
                  "CMPLNT_FR_TM",      # 48 blank,      1443 vals
                  "CMPLNT_TO_DT",      # 1391478 blank, 4828 vals
                  "CMPLNT_TO_TM",      # 1387785 blank, 1442 vals
                  "RPT_DT",            # 0 blank,       3652 vals
                  "LOC_OF_OCCUR_DESC", # 1127128 blank, 7 vals (213 " ")
                  "PREM_TYP_DESC"]     # 33279 blank,   71 vals
    #all_dict = {}
    #for col in all_column:
    #    all_dict[col] = groupby_and_count(df, col2idx[col]).collect()

    #with open('all_dict', 'wb') as f:
    #    pickle.dump(all_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    #for key in all_dict:
    #    print(key, len(all_dict[key]))
    #    for item in all_dict[key]:
    #        if item[0] == "":
    #            print(key, item)

    def duplicate_key(counts):
        '''
        check if there are duplicate keys
        '''
        key_list = []
        for x in counts.collect():
           key_list.append(x[0][0])
        return (len(key_list) != len(set(key_list)))

    KY_counts = df.map(lambda x: ((x[6], x[7]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    #PD_counts = df.map(lambda x: ((x[8], x[9]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    #PD_LAW = df.map(lambda x: ((x[8], x[11]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    PD_KY = df.map(lambda x: ((x[8], x[6], x[9], x[7]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    ADDR_BORO = df.map(lambda x: ((x[14], x[13]),1)).reduceByKey(add).sortBy(lambda x: x[0])
    
    #print(duplicate_key(KY_counts)) #True
    #print(duplicate_key(PD_counts)) #False
    #print(duplicate_key(PD_LAW))    #False
    #print(duplicate_key(PD_KY))     #True
    #print(duplicate_key(ADDR_BORO)) #True

    # Save for future reference
    #with open('KY_counts', 'wb') as f:
    #    pickle.dump(KY_counts.collect(), f, protocol=pickle.HIGHEST_PROTOCOL)

    #with open('PD_KY', 'wb') as f:
    #    pickle.dump(PD_KY.collect(), f, protocol=pickle.HIGHEST_PROTOCOL)

    #with open('ADDR_BORO', 'wb') as f:
    #    pickle.dump(ADDR_BORO.collect(), f, protocol=pickle.HIGHEST_PROTOCOL)

    def pair_dictionary(counts):
        '''
        Return (code, description) pair dictionary
        For each code, the valid description is the description with the most counts
        '''
        pairs = {}
        code = None
        for x in counts.collect():
            if x[0][0] != code:
                code = x[0][0]
                max_value = x[1]
                pairs[x[0][0]] = [x[0][1]]
            else:
                if x[1] > max_value:
                    max_value = x[1]
                    pairs[x[0][0]] = [x[0][1]]
        return pairs

    KY_dict = pair_dictionary(KY_counts)
    KY_dict['120'].append('ENDAN WELFARE INCOMP')
    KY_dict['343'].append('THEFT OF SERVICES')
    KY_dict['345'].append('ENDAN WELFARE INCOMP')
    KY_dict['360'] = ['LOITERING FOR DRUG PURPOSES']
    KY_dict['364'].append('AGRICULTURE & MRKTS LAW-UNCLASSIFIED')
    KY_dict['677'].append('NYS LAWS-UNCLASSIFIED VIOLATION')
    
    PDKY_dict = pair_dictionary(PD_KY)
    ADDR_dict = pair_dictionary(ADDR_BORO)

    #for key in sorted(ADDR_dict):
    #    print(key, ADDR_dict[key])

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
        code = row[col2idx["ADDR_PCT_CD"]]
        if not format_re_dict["TEXT"](row, col_idx):
            return False
        elif row[col_idx] not in ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]:
            return False
        elif row[col_idx] not in ADDR_dict[code]:
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
   
    def check_valid_three_digit(row, col_idx):
        if not format_re_dict["POS_INT"](row, col_idx):
            return False
        elif int(row[col_idx]) < 100 or int(row[col_idx]) > 1000:
            return False
        else:
            return True    

    def check_valid_KY(row, col_idx):
        code = row[col2idx["PD_CD"]]
        if check_valid_three_digit(row, col_idx) == False:
            return False
        elif row[col_idx] not in PDKY_dict[code]:
            return False
        else:
            return True

    def check_valid_OFNS_DESC(row, col_idx):
        code = row[col2idx["KY_CD"]]
        if not format_re_dict["TEXT"](row, col_idx):
            return False
        elif row[col_idx] not in KY_dict[code]:
            return False
        else:
            return True

    def check_valid_CRM(row, col_idx):
        if not format_re_dict["TEXT"](row, col_idx):
            return False
        elif row[col_idx] not in ["COMPLETED", "ATTEMPTED"]:
            return False
        else:
            return True
 
    def check_valid_LAW(row, col_idx):
        if not format_re_dict["TEXT"](row, col_idx):
            return False
        elif row[col_idx] not in ["FELONY", "MISDEMEANOR", "VIOLATION"]:
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

    check_col_func_dict = {
                        # valid text + within 5 district + mapping with ADDR_PCT_CD
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
                        # 3 digit pos int + mapping with PD_CD
                        "KY_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_KY, row, col_idx),
                        # any valid string + mapping with KY_CD
                        "OFNS_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_OFNS_DESC, row, col_idx),
                        # 3 digit pos int
                        "PD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_three_digit, row, col_idx),
                        # any valid string
                        "PD_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # completed/attempted
                        "CRM_ATPT_CPTD_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_CRM, row, col_idx),
                        # felony/misdemeanor/violation
                        "LAW_CAT_CD": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  check_valid_LAW, row, col_idx),
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

                        "CMPLNT_TO_TM": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                            check_TO_TM, row, col_idx),
                        # any valid string
                        "LOC_OF_OCCUR_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx),
                        # any valid string
                        "PREM_TYP_DESC": lambda row, col_idx: general_check_col_func(general_check_null_func,
                                                                                  format_re_dict["TEXT"], row, col_idx)}
                        
    # check each single ****ing cell in the data frame
    sanity_output = df.map(lambda x: check_row(x, check_col_func_dict)).collect()
    for x in sanity_output[0:100]:
        print(x)
