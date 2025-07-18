#import math
#import csv
#import sys
import itertools
#import time
#import os
#import psutil
#import csv
#import gc

def find_frequent_patterns(datalist, minSupport):
    #print("Data Mininging begins using H-mine algorithm...")
    # The minimum support is calculated using the ceil function. 
    # min_support which is passed to this algorithm is in precentage(%). This is converted to number of transactions.
    
    #out_frequents_items = []                # Frequent Items generated by H-Mine are appended one by one to this list
    itemsetBuffer = [None] * 200            # This buffer variable is used to store the Items under recursion to generate the final frequent-itemset
    mapItemToSupport = {}   #This Dictionary will be used to store the support values of all the unique items in input dataset
    mapItemRow = {} #This Dict will help us build the H-Struct table.
    final_patterns = {}

     # This function is used to generate frequent items using values in itemsetBuffer and prefixlen and apped that value to output list out_frequents_items
    def writeOut (prefix, prefixlen, item, support):
        freq = []
        for val in range(prefixlen):
            freq.append(prefix[val])
        freq.append(item)

        out_set = ()
        for val in freq:
            out_set = out_set + (val,)

        keys = out_set
        keys = tuple(sorted(keys))
        final_patterns[keys] = support

    # Creating Class called Row to store the itemsets objects in form item, support of item, item pointer
    class Row:
        def __init__(self, item):
            self.item = item
            self.support = 0
            self.pointer = []


    #Building mapItemToSupport Dictionary with Unique Items in input dataset and it's support value
    for tran in datalist:
        for item in tran:
            if item not in mapItemToSupport.keys(): 
                mapItemToSupport[item] = 1
            else : 
                mapItemToSupport[item] += 1

    rowlist=[]      #This acts as a Header table storing the list of row objects

    for keys in mapItemToSupport.keys():
        if mapItemToSupport[keys] >= minSupport:
            rowItem = Row(keys);
            rowItem.support = mapItemToSupport[keys]
            rowlist.append(rowItem)
            mapItemRow[keys] = rowItem

    # This is used to find the frequent-item cell of the database.
    # All the other frequent-itemsets will be found using this cell.

    cell = []   #This variable stores all the frequent projections in all the transactions seperated by -1

    flist = sorted(mapItemRow.keys()) # f-list of frequent itemsets in sorted order

    idx = 0
    #This loop is used to append frequent projections in Cell list and append their respective pointers in mapItemRow dictionary 
    for tran in datalist:
        temp=[]
        for item in tran:
            if item in flist:
                if item not in temp: # checking double occurences in the list
                    temp.append(item)

        if temp:
            temp = sorted(temp, key = lambda x: mapItemToSupport[x])
            for x in temp:
                cell.append(x)
                mapItemRow[x].pointer.append(idx)
                idx += 1
            cell.append(-1)
            idx += 1


    # This function impletements this logic for H-mine algorithm and is called recursively 
    def hmine(prefix=[], prefixlen=0, rowlist=[]):

        for row in rowlist: #Traversing the header table (rowlist)
            newRowlist=[]
            mapItemRow.clear()

            #traversing all pointers of row object in row list and building new recursive sub-level header
            for pointer in row.pointer:
                pointer+=1

                if cell[pointer]==-1:
                    continue;

                #Generating the row objects and incresing the support for all the unique items in row objects    
                while cell[pointer] != -1 :
                    item=cell[pointer]
                    if mapItemRow.get(item,None) == None :
                        rowItem = Row(item)
                        rowItem.support = 1
                        rowItem.pointer.append(pointer)
                        mapItemRow[item] = rowItem

                    else:    
                        mapItemRow[item].support += 1
                        mapItemRow[item].pointer.append(pointer)

                    pointer += 1

            #Appending only those row objects which have support greater than min_support
            for entry in mapItemRow:
                currentRow = mapItemRow[entry]
                if currentRow.support >= minSupport:
                    newRowlist.append(currentRow)

            #Calling writeOut function to generate the frequent items and store in output list
            writeOut(itemsetBuffer, prefixlen, row.item, row.support)

            #Sorting newRowlist in lexical order
            if len(newRowlist) != 0 :
                newRowlist = sorted(newRowlist, key = lambda x : x.support)


                #Store current row item in buffer before recursion so that it can be used to build the frequent itemset values    
                itemsetBuffer[prefixlen] = row.item

                hmine(prefix, prefixlen+1, newRowlist)      #recursively calling Hmine algorithm
        

    hmine(itemsetBuffer, 0, rowlist)  #Calling Hmine algorithm for first time using empty Buffer and 0 as prefixlength and initial value of rowlist Header.

    #itemset_count = len(final_patterns) # Total number of frequent_items for given input_file dataset
    return final_patterns


    #print(f'Data Mining completed using H-Mine algorithm')
    #print("End of Program")
    
def generate_association_rules(patterns, confidence_threshold):

    rules = {}
    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent = tuple(sorted(antecedent))
                consequent = tuple(sorted(set(itemset) - set(antecedent)))

                if antecedent in patterns:
                    lower_support = patterns[antecedent]
                    confidence = float(upper_support) / lower_support

                    if confidence >= confidence_threshold:
                        rules[antecedent] = (consequent, confidence)
    return rules   

"""
    
def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss

def detailed_rules(rules):
    for antecd in rules.keys():
        tset = rules[antecd]
        cons = tset[0]
        confi = tset[1]
        print(antecd, " --> ", cons, ":", str(confi))

def detailed_patterns(patterns):
    for pattern in patterns.keys():
        val = patterns[pattern]
        print(pattern, ":", val)
    
gc.collect()

# Open file in append mode once, and keep it open throughout the loop

init_mem = get_process_memory()
init_time = time.perf_counter()

Dataset = 'chess.dat'
#Dataset = "Market_Basket_Optimisation.txt"


with open(Dataset, 'r') as f:
    records = [line.strip().split() for line in f]    
    
while(True):  
        min_supp = len(records) * 0.6
        #min_supp = 3
        print("Minimum Support: " + str(min_supp))
        
        patterns = find_frequent_patterns(records, min_supp)
        rules = generate_association_rules(patterns, 80)
        
        end_time = time.perf_counter()
        total_time = end_time - init_time
        
        end_mem = get_process_memory()
        total_mem = end_mem - init_mem
        
        #detailed_patterns(patterns)
        
        print("Hmine Memory used: ", total_mem)
        
        print("Hime time taken: ", total_time)
        
        #print(patterns)
        #detailed_rules(rules)
        #print(rules)
        
        print("Hmine Pattern found: ", len(patterns))
        
        print("Hmine rule found: ", len(rules))
        break
    
    
# Below Code returns the memory usage of this algorithm. This section was used to generate metrics used for experimental analysys.
# processid = os.getpid()
# process = psutil.Process(processid)
# memoryUse = process.memory_info()
# return memoryUse.rss
"""