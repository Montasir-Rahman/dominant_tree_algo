import itertools


class FPNode(object):
    """
    A node in the FP tree.
    """

    def __init__(self, value, count, parent):
        """
        Create the node.
        """
        self.value = value
        self.count = count
        self.parent = parent
        #self.link = None
        self.children = []

    def has_child(self, value):
        """
        Check if node has a particular child node.
        """
        for node in self.children:
            if node.value == value:
                return True

        return False

    def get_child(self, value):
        """
        Return a child node with a particular value.
        """
        for node in self.children:
            if node.value == value:
                return node

        return None

    def add_child(self, value):
        """
        Add a node as a child node.
        """
        child = FPNode(value, 1, self)
        self.children.append(child)
        return child
    
    def disp(self, ind=1):
        print ('  '*ind, self.value, ' ', self.count)
        for child in self.children:
            child.disp(ind+1)  

class FPTree(object):
    """
    A frequent pattern tree.
    """

    def __init__(self, transactions, threshold, root_value, root_count):
        """
        Initialize the tree.
        """
        self.frequent = self.find_frequent_items(transactions, threshold)
        #print (self.frequent)
        #self.linkTable = self.build_header_table(self.frequent)
        self.linkTable = self.build_header_table(self.frequent)
        #print (self.linkTable)
        self.root = self.build_fptree(
            transactions, root_value,
            root_count, self.frequent, self.linkTable)

    @staticmethod
    def find_frequent_items(transactions, threshold):
        """
        Create a dictionary of items with occurrences above the threshold.
        """
        items = {}

        for transaction in transactions:
            for item in transaction:
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1

        #print (items)
        for key in list(items.keys()):
            if items[key] < threshold:
                del items[key]
        
        #print (items)
        return items

    @staticmethod
    def build_header_table(frequent):
        """
        Build the header table.
        """
        linkTable = {}
        for key in frequent.keys():
            linkTable[key] = None

        return linkTable

    def build_fptree(self, transactions, root_value,
                     root_count, frequent, linkTable):
        """
        Build the FP tree and return the root node.
        """
        root = FPNode(root_value, root_count, None)

        for transaction in transactions:
            sorted_items = [x for x in transaction if x in frequent]
            sorted_items.sort(key=lambda x: frequent[x], reverse=True)
            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, root, linkTable)
        return root

    def insert_tree(self, items, node, linkTable):
        """
        Recursively grow FP tree.
        """
        #print (items)
        first = items[0]
        child = node.get_child(first)
        if child is not None:
            child.count += 1
        else:
            # Add new child.
            child = node.add_child(first)

            # Link it to header structure.
            if linkTable[first] is None:
                linkTable[first] = [child]
            else:
                #print ("++" + str(linkTable[first].value))
                #current = linkTable[first]
                #print (current.value)
                #while current.link is not None:
                #    current = current.link
                #current.link = child
                linkTable[first].append(child)
                    
        # Call function recursively.
        remaining_items = items[1:]
        if len(remaining_items) > 0:
            self.insert_tree(remaining_items, child, linkTable)

    def tree_has_single_path(self, node):
        """
        If there is a single path in the tree,
        return True, else return False.
        """
        num_children = len(node.children)
        if num_children > 1:
            return False
        elif num_children == 0:
            return True
        else:
            return True and self.tree_has_single_path(node.children[0])

    def mine_patterns(self, threshold):
        """
        Mine the constructed FP tree for frequent patterns.
        """
        if self.tree_has_single_path(self.root):
            #print ("True")
            return self.generate_pattern_list()
        else:
            #print ("+True")
            return self.zip_patterns(self.mine_sub_trees(threshold))

    def zip_patterns(self, patterns):
        """
        Append suffix to patterns in dictionary if
        we are in a conditional FP tree.
        """
        suffix = self.root.value

        if suffix is not None:
            # We are in a conditional tree.
            new_patterns = {}
            for key in patterns.keys():
                new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

            return new_patterns

        return patterns

    def generate_pattern_list(self):
        """
        Generate a list of patterns with support counts.
        """
        patterns = {}
        items = self.frequent.keys()

        # If we are in a conditional tree,
        # the suffix is a pattern on its own.
        if self.root.value is None:
            suffix_value = []
        else:
            suffix_value = [self.root.value]
            patterns[tuple(suffix_value)] = self.root.count

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items, i):
                pattern = tuple(sorted(list(subset) + suffix_value))
                patterns[pattern] = \
                    min([self.frequent[x] for x in subset])

        return patterns

    def mine_sub_trees(self, threshold):
        """
        Generate subtrees and mine them for patterns.
        """
        patterns = {}
        mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])
        
        #print (mining_order)

        # Get items in tree in reverse order of occurrences.
        for item in mining_order:
            suffixes = []
            conditional_tree_input = []
            
            '''
            node = self.linkTable[item]

            # Follow node links to get a list of
            # all occurrences of a certain item.
            while node is not None:
                suffixes.append(node)
                node = node.link
            '''
            
            suffixes = self.linkTable[item]
            
            # For each occurrence of the item, 
            # trace the path back to the root node.
            for suffix in suffixes:
                frequency = suffix.count
                path = []
                parent = suffix.parent

                while parent.parent is not None:
                    path.append(parent.value)
                    parent = parent.parent
                
                #print (path)
                
                for i in range(frequency):
                    conditional_tree_input.append(path)
                    
                #print (conditional_tree_input)

            # Now we have the input for a subtree,
            # so construct it and grab the patterns.
            subtree = FPTree(conditional_tree_input, threshold,
                             item, self.frequent[item])
            #subtree.root.disp()
            subtree_patterns = subtree.mine_patterns(threshold)

            # Insert subtree patterns into main patterns dictionary.
            for pattern in subtree_patterns.keys():
                if pattern in patterns:
                    patterns[pattern] += subtree_patterns[pattern]
                else:
                    patterns[pattern] = subtree_patterns[pattern]

        return patterns


def find_frequent_patterns(transactions, support_threshold):
    """
    Given a set of transactions, find the patterns in it
    over the specified support threshold.
    """
    tree = FPTree(transactions, support_threshold, None, None)
    return tree.mine_patterns(support_threshold)


def generate_association_rules(patterns, confidence_threshold):
    """
    Given a set of frequent itemsets, return a dict
    of association rules in the form
    {(left): ((right), confidence)}
    """
    rules = {}
    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent = tuple(sorted(antecedent))
                consequent = tuple(sorted(set(itemset) - set(antecedent)))

                if antecedent in patterns:
                    lower_support = patterns[antecedent]
                    if lower_support >= upper_support:
                        confidence = float(upper_support) / lower_support
                    else:
                         # This is logically invalid, so skip
                         continue
                    #confidence = float(upper_support) / lower_support

                    if confidence >= confidence_threshold:
                        rules[antecedent] = (consequent, confidence)

    return rules

"""
# In[]:
    
import time
import os
import psutil
import gc

gc.collect()

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss

init_mem = get_process_memory()
init_time = time.perf_counter()


f = open('sample.dat','r')
records = []
for lines in f:
   content =lines.strip().split()
   records.append(content)

f = open("res_acc_colab_fpm.txt", "a+")
f.flush()
#f.write("percent" + ", " + "min_supp" + ", " + "exec_time" + ", " + "mem_used" + ", " + "pattern_count" + ", " + "rules_count")
#f.write("\n")


for i in range (100, 39, -10):
    min_supp = len(records) * (i / 100)
    patterns = find_frequent_patterns(records, min_supp)
    rules = generate_association_rules(patterns, 0.8)
 
    fin_mem = get_process_memory()
    fin_time = time.perf_counter()

    exec_time = fin_time - init_time
    mem_used = fin_mem - init_mem
    
    f.write(str(i) + ", " + str(min_supp) + ", " + str(exec_time) + ", " + str(mem_used) + ", " + str(len(patterns)) + ", " + str(len(rules)))
    print(str(i) + ", " + str(min_supp) + ", " + str(exec_time) + ", " + str(mem_used) + ", " + str(len(patterns)) + ", " + str(len(rules)))
    f.write("\n")
    
    print ("Execution Time (Seconds): ", exec_time)
    print ("Memory Used (Bytes): ", mem_used)
    gc.collect()

f.close()
gc.collect()
"""