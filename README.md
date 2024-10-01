# Overview
This project is part of **Multidimensional Data Strucrures & Computational Geometry** elective course in Computer Engineering & Informatics Department of University of Patras for Winter Semester 2023-2024 (Semester 7).

## Dataset
The Scientists Dataset that we will be using for this project is created with the aid of a web crawler that scans data form this link: https://en.wikipedia.org/wiki/List_of_computer_scientists and creates a CSV file.

Every tuple of the final CSV file will have this format: (**Surname**:String, **#Awards**:Integer, **Education**:text-vector, **#DBLP_Record**). The 3 features **Surname**, **#Awards** and **#DBLP_Record** will be used for the indexing that will be performed by the Multidimensional Structures. Also, we will implement **Locality Sensitive Hashing (LSH)** on the text vectors of the feature **Education** in order to find common semantic content between the different scientists. 

## Goals
Our goal is to build the following Multidimensional Data Structures: **kd-Tree**, **Quad-Tree**, **R-Tree** and **Range Tree** and implement them on the initial Dataset in order to answer to spatial range, interval or similarity queries. For each query the user must enter:
1. the range (A-Z) of the first letter of the scientists **Surname**
2. the minimum threshold of the **#Awards** of the scientists
3. the range of the **#DBLP_Record** of the scientists.

Then, we will use the **LSH** method in order to filter the results returned by the trees and keep only those scientists that share common **Education** in a percentage greater than a user defined threshold.

Finally, we will compare the average case complexity and speed of the 4 structures in order to find which one is the most efficient.

![Στιγμιότυπο οθόνης 2024-10-01 165405](https://github.com/user-attachments/assets/ce8d2f0e-a551-4d02-9f9f-e76e6e3411f3)

