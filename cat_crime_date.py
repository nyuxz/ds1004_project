from __future__ import print_function

import sys
from operator import add
from pyspark import SparkContext
from csv import reader

def date_crime(x):
    return '\t'.join((x[5],x[7]))

if __name__ == "__main__":
    sc = SparkContext()
    lines = sc.textFile(sys.argv[1], 1)
    lines = lines.mapPartitions(lambda x: reader(x))    
    counts = lines.map(lambda x: (date_crime(x), 1)) \
                  .reduceByKey(add)
    counts = counts.map(lambda x: "%s\t%s" %(x[0],x[1]))
    counts.saveAsTextFile("cat_crime_date.out")

    sc.stop()
