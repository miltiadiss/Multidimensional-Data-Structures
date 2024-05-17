import pandas as pd
import numpy as np
import random
import time
import matplotlib.pyplot as plt
from LSH import *

class Node:
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right

def build_kdtree(points, depth=0):
    if not points:
        return None

    k = len(points[0])
    axis = depth % k

    points.sort(key=lambda x: x[axis])

    median = len(points) // 2

    return Node(
        point=points[median],
        left=build_kdtree(points[:median], depth + 1),
        right=build_kdtree(points[median + 1:], depth + 1)
    )

def range_search(node, query_point, depth=0):
    if node is None:
        return []

    k = len(query_point)
    axis = depth % k
    result = []

    # Καθορίζουμε αν χρειάζεται να ψάξουμε στο αριστερό ή δεξί υποδέντρο
    search_left = query_point[axis][0] <= node.point[axis] # Γίνεται True όταν
    search_right = node.point[axis] <= query_point[axis][1]

    #  Αναδρομική αναζήτηση στο αριστερό υποδέντρο αν είναι απαραίτητο
    if search_left and node.left is not None:
        result.extend(range_search(node.left, query_point, depth + 1))

    # Ελέγχουμε αν ο τρέχων κόμβος είναι εντός του εύρους
    in_range = True
    for i in range(k):
        lower_bound = query_point[i][0] # Κάτω όριο
        upper_bound = query_point[i][1] # Άνω όριο

        # Προσαρμογή του ανωτάτου ορίου για συγκρίσεις ανάμεσα σε συμβολοσειρές
        if isinstance(node.point[i], str) and isinstance(upper_bound, str):
            in_range = in_range and lower_bound <= node.point[i] <= upper_bound + chr(255)
        else:
            in_range = in_range and lower_bound <= node.point[i] <= upper_bound

    if in_range:
        result.append(node.point)

    # Αναδρομική αναζήτηση στο δεξί υποδέντρο αν είναι απαραίτητο
    if search_right and node.right is not None:
        result.extend(range_search(node.right, query_point, depth + 1))

    return result

def main_KD_Tree():
    def result(kdtree, query_surname_range, query_award_range, query_publication_range, threshold_education):
        # Εκτέλεση αναζήτησης εύρους
        query_point = (query_surname_range, query_award_range, query_publication_range)
        # Έναρξη χρονομέτρησης range search
        start_time_1 = time.time()
        points_in_range = range_search(kdtree, query_point)
        # Λήξη χρονομέτρησης range search
        end_time_1 = time.time()
        # Υπολογισμός συνολικού χρόνου για αναζήτηση
        elapsed_time_1 = end_time_1 - start_time_1

        # Δημιουργία λίστας για αποθήκευση δεδομένων για το CSV
        csv_data = []
        unique_surnames = set()  # Κρατάμε τα επώνυμα τα οποία διαθέτουν κάποια εκπαίδευση

        for point in points_in_range:
            surname, awards, dblp = point

            # Ελέγχουμε αν έχουμε προσθέσει ήδη μια έγκυρη εγγραφή με αυτό το επώνυμο για να αφαιρέσουμε τα διπλότυπα
            if surname in unique_surnames:
                continue

            # Εξάγουμε το κείμενο που αφορά την εκπαίδευση για κάθε επιστήμονα
            education_text = df.loc[
                (df['Surname'] == surname) & (df['Awards'] == awards) & (df['Dblp'] == dblp),
                'Education'
            ].values[0]

            # Ελέγχουμε αν το κείμενο δεν είναι 'Education information not found'
            if education_text != 'Education information not found':
                unique_surnames.add(surname)  # Add to the set of unique surnames
                csv_data.append([surname, awards, dblp, education_text])

        # Μετατρέπουμε τα συνολικά δεδομένα του ολικου CSV σε DataFrame
        csv_columns = ['Surname', 'Awards', 'Dblp', 'Education']
        result_df = pd.DataFrame(csv_data, columns=csv_columns)

        # Εκτελούμε LSH ως προς τη στήλη 'Education'
        education_texts = result_df['Education'].tolist()
        education_texts_preprocessed = [preprocess_education(edu) for edu in education_texts]
        # Έναρξη χρονομέτρησης LSH
        start_time_2 = time.time()
        similar_pairs_education = lsh_education(education_texts_preprocessed, result_df, threshold_education)
        # Λήξη χρονομέτρησης LSH
        end_time_2 = time.time()
        # Υπολογισμός συνολικού χρόνου για LSH
        elapsed_time_2 = end_time_2 - start_time_2

        # Αποθηκεύουμε τα μοναδικά ονόματα από όλα τα ζευγάρια με κοινή εκπαίδευση
        unique_surnames_in_pairs = set()

        for pair in similar_pairs_education:
            (entry1, surname1), (entry2, surname2) = pair
            if surname1 in unique_surnames and surname1 not in unique_surnames_in_pairs:
                awards1, dblp1 = df.loc[df['Surname'] == surname1, ['Awards', 'Dblp']].iloc[0]
                print(f"Surname: {surname1}, #Awards: {awards1}, #DBLP_Record: {dblp1}")
                unique_surnames_in_pairs.add(surname1)
            if surname2 in unique_surnames and surname2 not in unique_surnames_in_pairs:
                awards2, dblp2 = df.loc[df['Surname'] == surname2, ['Awards', 'Dblp']].iloc[0]
                print(f"Surname: {surname2}, #Awards: {awards2}, #DBLP_Record: {dblp2}")
                unique_surnames_in_pairs.add(surname2)  

        result_df_education = pd.DataFrame(similar_pairs_education, columns=['Entry1', 'Entry2'])
        result_df_education.to_csv('Kd_tree_results.csv', index=False)

        # Συνολικός χρόνος για αναζήτηση και LSH
        elapsed_time = elapsed_time_1 + elapsed_time_2
        print(f"Time taken for range search with LSH: {elapsed_time} seconds")

    # Εξάγουμε όλα τα σημεία, δηλαδή τους κόμβους του δέντρου
    csv_file_path = 'scientists.csv'
    df = pd.read_csv(csv_file_path)
    points = df[['Surname', 'Awards', 'Dblp']].apply(lambda row: (row['Surname'], row['Awards'], row['Dblp']),
                                                     axis=1).tolist()

    # Κατασκευάζουμε το KD-tree από τα σημεία που προκύπτουν
    kdtree = build_kdtree(points)

    # Eισαγωγή από τον χρήστη των σημeίων αναζήτησης
    min_letter = input("Press the first letter of the query (ex.A, B, C...):").upper()
    while not min_letter.isalpha():
        min_letter = input("Press the first letter you want in the right form:")
    max_letter = input("Press the second letter of the query (ex.A, B, C...):").upper()
    while not max_letter.isalpha():
        max_letter = input("Press the second letter you want in the right form:")
    min_awards = int(input("Press the minimum awards of the query (ex.0,1,2...) :"))
    min_dblps = int(input("Press the minimum DBLP records of the query (ex.0,1,2...) :"))
    max_dblps = int(input("Press the maximum DBLP records of the query (ex.0,1,2...) :"))
    lsh_sim = float(input("Give the LSH percentage of similarity between the scientists (ex.0.5->50%):"))
    print("The query that you created is the following: ")
    print(
        "Find the computer scientists from Wikipedia that their surname first letter belongs in the interval [" + min_letter + "-" + max_letter + "],have won more than " + str(
            min_awards) + " prizes and their DBLP record belongs in the interval [" + str(
            min_dblps) + " ," + str(max_dblps) + "].")
    print("Generating Answer...")

    # Συγκεντρώνουμε όλα τα εύρη του ερωτήματος
    query_parameters = [
            ((min_letter, max_letter), (min_awards, np.Inf), (min_dblps, max_dblps), lsh_sim)
    ]

    # Καλούμε τη συνάρτηση result( ) για να εκτελέσουμε range search στο κατασκευασμένο δέντρο και μετά LSH στα τελικά σημεία που επιστράφηκαν
    for surname_range, award_range, publication_range, threshold in query_parameters:
        result(kdtree, surname_range, award_range, publication_range, threshold)
