from R_Tree import *
from Range_Tree import *
from Oc_Tree import *
from KD_Tree import *

def switch(tree):
    if tree == "1":
        print("\n")
        return main_R_tree()
    elif tree == "2":
        print("\n")
        return main_Range_Tree()
    elif tree == "3":
        print("\n")
        return main_Oc_Tree()
    elif tree == "4":
        print("\n")
        return main_KD_Tree()

print("If you want to search with R-Tree press 1")
print("If you want to search with Range-Tree press 2")
print("If you want to search with Oc-Tree press 3")
print("If you want to search with KD-Tree press 4")
Decision = switch(input("\nChoose a number:"))
