# -*- coding: utf-8 -*-
"""
Created on Fri Nov 08 16:09:16 2019

@author: soupnook

Algorithm to prep data in order for validation on the minimum number of rolling day
to average the data

Outputs a csv file (called reported.csv) in the same directory

"""


# Import dependencies and set parameters for seaborn settings
import pandas as pd
import datetime
import argparse
from PullDataBT import *


parser = argparse.ArgumentParser(description='Parameterisation analysis')
parser.add_argument("--servernameEDW", required=True, help="provide SQL server name for EDWPre")
parser.add_argument("--databasenameEDW", required=True, help="provide DB name for EDWPre")


def Select_Table(fulldf, prd_num, reg_num, startdt):
    """
    Function to calculate the moving average (over 16 weeks) values for every tranche of region and product

    :param fulldf: The full dataframe of all results
    :param prd_num: Index number for which product the data is being split by
    :param reg_num: Index number for which region the data is being split by
    :return: Returns both a shrunk version of the tranche dataframe and the moving average dataframe
    """
    filterdf = fulldf.where((fulldf["BusinessType"] == products[prd_num]) &
                            (fulldf["Geography"] == regions[reg_num]) &
                            (fulldf["DOTY"] < datetime.date(2019, 1, 1)))
    idx = pd.date_range(startdt, '01-01-2019')
    filterdf.dropna(axis=0, how="any", inplace=True)
    dfmini = filterdf[["DOTY", "NumberOfPolicies"]]
    dfmini.set_index("DOTY", inplace=True)
    dfmini = dfmini.reindex(idx, fill_value=0)
    return dfmini


def Datefix(splitdatedf):
    # Making date format consistent with datetime -- CHANGE FOR EACH INDEX
    redate = []
    for y, m, d in zip(splitdatedf.loc[:, "InceptionYear"],
                       splitdatedf.loc[:, "InceptionMonth"],
                       splitdatedf.loc[:, "InceptionDay"]):
        redate.append(datetime.date(y, m, d))
    splitdatedf["DOTY"] = redate
    return splitdatedf


def ReportBuild(df, i, stdate, rep):
    # STILL NOT A TRULY INDEPENDENT FUNCTION - CONSIDER REVISION
    reg = i // len(products)  # Floor Division
    prd = i % len(products)  # Remainder
    dfmini = Select_Table(df, prd_num=prd, reg_num=reg, startdt=stdate)
    rollsum = dfmini.rolling(rollnum).sum()
    rollsum.dropna(axis=0, how="any", inplace=True)
    rep["Region"].append(regions[reg])
    rep["Product"].append(products[prd])
    rep["Roll"].append(rollnum)
    rep["StartYear"].append(stdate)
    rep["StatViable"].append(float(
        (rollsum[rollsum['NumberOfPolicies'] > 29].count()) / (rollsum['NumberOfPolicies'].count())) * 100)
    rep["Average"].append(rollsum["NumberOfPolicies"].mean())
    return rep

###################################################################################################################

#def ParameterTest():


if __name__ == "__main__":

    # Import the Dataframe from Excel doc
    dataframe = GetInputFromDB().fetch_ROL(server_name=args.servernameEDW, database_name=args.databasenameEDW)
    #pd.read_excel("RollingDayAllParams.xlsx", sheet_name="Sheet1", index=1)
    dataframe = Datefix(dataframe)

    # Setting up the parameters
    products = dataframe["BusinessType"].unique()
    regions = dataframe["Geography"].unique()
    rolldays = [1, 5, 7, 10, 14, 20, 30, 45, 60, 90, 120, 180]
    yr_start = ["01-01-2010", "01-01-2011", "01-01-2012", "01-01-2013", "01-01-2014", "01-01-2015",
                "01-01-2016", "01-01-2017", "01-01-2018", "01-01-2019"]

    # Take only the relevant fields in case of extended query
    reldf = dataframe[["DOTY", "Geography", "BusinessType", "NumberOfPolicies"]]

    report = {"Region": [], "Product": [], "Roll": [], "StartYear": [], "PercentageViable": [], "AverageNumData": []}

    # Looping through every iteration of roll-days, product, region to find out the change in viability as
    # rolling number increases
    for startdate in yr_start:
        for rollnum in rolldays:
            for i in range(len(products) * len(regions)):
                report = ReportBuild(df=dataframe, i=i, stdate=startdate, rep=report)
                print("Running."+("."*(i%3)))

    print("Saving Report...")
    reportdf = pd.DataFrame(report)

    reportdf.to_csv("AllRegReport.csv")
