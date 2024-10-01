![Στιγμιότυπο οθόνης 2024-09-08 194529](https://github.com/user-attachments/assets/bc6eed92-0511-4625-8c9e-7cab1ad37896)

# Overview
This project is part of **Multidimensional Data Strucrures & Computational Geometry** elective course in Computer Engineering & Informatics Department of University of Patras for Winter Semester 2023-2024 (Semester 7).

## Dataset
The Scientists Dataset that we will be using for this project is created with the aid of a web crawler that scans data form this link: https://en.wikipedia.org/wiki/List_of_computer_scientists and creates a CSV file.

Every tuple of the final CSV file will have this format: (**Surname**:String, **#Awards**:Integer, **Education**:text-vector, **#DBLP_Record**). The 3 features **Surname**, **#Awards** and **#DBLP_Record** will be used for the indexing that will be performed by the Multidimensional Structures. Also, we will implement **Locality Sensitive Hashing (LSH)** on the text vectors of the feature **Education** in order to find common semantic content between the different scientists. 

## Goals
Our goal is to build the following Multidimensional Data Structures: **kd-Tree**, **Quad-Tree**, **R-Tree** and **Range Tree** and implement them on the initial Dataset in order to answer to spatial range, interval or similarity queries. For each query the user must enter:
1. the range (A-Z) of the first letter of the scientists **Surname**  
