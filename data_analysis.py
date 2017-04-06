from __future__ import print_function

import sys
from operator import add
from pyspark import SparkContext
from csv import reader



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
    # filename = "/user/ys1001/data.csv"

    df = sc.textFile(filename, 1).mapPartitions(lambda x: reader(x))
    all_columns = df.first()
    col2idx = dict([(all_columns[i], i) for i in range(len(all_columns))])
    df = df.filter(lambda line: line != all_columns)

    # overview
    nrow = df.count()
    ncol = len(all_columns)
    print("dataset has {0} rows".format(nrow)) # 5101231
    print("dataset has {0} cols".format(ncol)) # 24

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


    # NULL values for each columns
    null_vals_dict = {"BORO_NM":[""],
                 "ADDR_PCT_CD":[""],
                 "PARKS_NM":[""],
                 "HADEVELOPT":[""],
                 "X_COORD_CD":[""],
                 "Y_COORD_CD":[""],
                 "Latitude":[""],
                 "Longitude":[""],
                 "Lat_Lon":[""]}


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
                                                                               check_valid_Lat_Lon, row, col_idx)}

    # check each single ****ing cell in the data frame
    sanity_output = df.map(lambda x: check_row(x, check_col_func_dict)).collect()
    print(sanity_output)





