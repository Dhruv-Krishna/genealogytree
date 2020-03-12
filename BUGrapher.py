# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 12:15:39 2019

@author: soupnook
"""

from graphviz import Digraph
import pandas as pd


def grab_name(row, group):
    name = ""
    for n in range(group):
        name += row[1][("Group" + str(n + 1))]
        if n == (group - 1):
            pass
        else:
            name += " | "
    return name

def make_graph(mega, df):
    fname = str(mega) + ".png"
    u = Digraph('unix', filename=fname,
                node_attr={'color': 'lightblue2',
                           'fontsize': '400!',
                           'style': 'filled'})
    u.attr(size='90,23!', ratio="fill", fixedsize="False")

    whitelist = []

    for row in df.iterrows():
        for i in range(5):
            parname = grab_name(row=row,group=i+1)
            chname = grab_name(row=row,group=i+2)
            if (parname.split()[-1] == chname.split()[-1]) or ("Under Review" in chname) or \
                    ("Under Review" in chname.split()[-1]):
                break
            else:
                whitelist.append((parname, chname))

                # if row[1][chname] in chlist:
                #     whitelist.append((str(parname) + " " + str(row[1][parname]), (str(chname) + " " + str(row[1][chname]))))
                #
                #             # TODO: MAKE LOOP TO RENAME IN CASE OF SAME NAME
                # continue


    rewhitelist = list(set(whitelist))
    for relation in rewhitelist:
        u.edge(relation[0], relation[1])
    u.view()

if __name__ == "__main__":
    # SKELETAL STRUCTURE - NEEDS REVISION
    masterdf = pd.read_excel("BusinessUnits.xlsx", header=0)
    for megagroup in masterdf["Group1"].unique():
        cutdf = masterdf[masterdf["Group1"] == megagroup]
        make_graph(megagroup, cutdf)


# Check if pair is blacklisted
# Make list of all relationships from unique-ing list / Chop and slice each row group into 4 pairs
# IF BOTH RELATIONSHIP ARE SAME, BREAK - keeps it at last unique
# Make sure to append grouping name to end of name to keep it unique in case of downstream similarity AFTER checking direct relation

