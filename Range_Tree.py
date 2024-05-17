import pandas as pd
import random
import time
from LSH import *


# δημιουργία κλάσης για κόμβο
class Node:
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right


# κλαση για δέντρο
class ThreeDTree:
    def __init__(self):
        self.root = None

    def create_tree(self, points, dim=0):
        if not points:
            return None

        dim %= 3  # επανάληψη κάθε φορά για αριθμό διάστασης απο 1 έως 3
        points.sort(key=lambda p: p[dim])  # ταξινόμησης της λίστας με τα σημεία σύμφωνα με την τρέχουσα διάσταση
        mid = int(len(points) // 2)  # το μέσο της λίστας
        root = Node(points[mid])  # κάνει το μέσο ρίζα

        root.left = self.create_tree(points[:mid], dim + 1)  # δημιουργία αριστερού υποδέντρου
        root.right = self.create_tree(points[mid + 1:], dim + 1)  # δημιουργία δεξιού υποδέντρου

        return root

    def insert_data_from_csv(self, csv_file_path):  # εισαγωγή δεδομένων απο το csv
        df = pd.read_csv(csv_file_path)  # δημιουργία df με το csv
        points = df[['Surname', 'Awards', 'Dblp']].apply(
            lambda row: (row['Surname'], row['Awards'], row['Dblp']),
            axis=1).tolist()  # τα points είναι οι στήλες Surname, Awards και Dblp
        self.root = self.create_tree(points)  # δημιουργία δέντρου για τα points αυτά

    def range_search(self, root, min_surname, max_surname, min_awards, max_awards, min_dblps, max_dblps,
                     dim=0, result=None):
        if result is None:
            result = []

        if root is None:  # αν το δέντρο είναι κενό
            return result

        dim %= 3

        # έλεγχος για το αν η ρίζα είναι μεταξύ του διαστήματος σε κάθε διάσταση
        if (
                (min_surname <= root.point[0] < max_surname or root.point[0].startswith(max_surname)) and
                (min_awards <= root.point[1] <= max_awards) and
                (min_dblps <= root.point[2] <= max_dblps)
        ):
            result.append(root)

        # εναλλαγή δεξιού και αριστερού υποδέντρου σύμφωνα με την τρέχουσα διάσταση
        if dim == 0:
            if min_surname < root.point[dim] or root.point[0].startswith(min_surname):
                self.range_search(root.left, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)
            if max_surname > root.point[dim] or root.point[0].startswith(max_surname):
                self.range_search(root.right, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)
        elif dim == 1:
            if min_awards <= root.point[dim]:
                self.range_search(root.left, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)
            if max_awards >= root.point[dim]:
                self.range_search(root.right, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)
        elif dim == 2:
            if min_dblps <= root.point[dim]:
                self.range_search(root.left, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)
            if max_dblps >= root.point[dim]:
                self.range_search(root.right, min_surname, max_surname, min_awards, max_awards,
                                  min_dblps, max_dblps, (dim + 1) % 3, result)

        return result

def main_Range_Tree():
    # δημιουργία δέντρου, αντικείμενο της κλάσης ThreeDTree
    tree = ThreeDTree()

    # εισαγωγή δεδομένων στο δέντρο απο το CSV αρχείο
    csv_file_path = 'scientists.csv'  # file path
    tree.insert_data_from_csv(csv_file_path)

    # ορισμός των διαστημάτων αναζήτησης
    min_surname = input("Press the first letter of the query (ex.A, B, C...):").upper()
    while not min_surname.isalpha():
        min_surname = input("Press the first letter you want in the right form:")
    max_surname = input("Press the second letter of the query (ex.A, B, C...):").upper()
    while not max_surname.isalpha():
        max_surname = input("Press the second letter you want in the right form:")
    min_awards = int(input("Press the minimum awards of the query (ex.0,1,2...) :"))
    min_dblps = int(input("Press the minimum DBLP records of the query (ex.0,1,2...) :"))
    max_dblps = int(input("Press the maximum DBLP records of the query (ex.0,1,2...) :"))
    threshold_education = float(input("Give the LSH percentage of similarity between the scientists (ex.0.5->50%):"))
    print("The query that you created is the following ! ")
    print(
        "Find the computer scientists from Wikipedia that their letters belongs in the interval [" + min_surname + "-" + max_surname + "],have won more than " + str(
            min_awards) + " prizes and their DBLP record belongs in the interval [" + str(
            min_dblps) + " ," + str(max_dblps) + "].")
    print("Generating Answer...")

    # start time
    start_time_1 = time.time()

    # αποθήκευση επιστρεφόμενων κόμβων
    results = tree.range_search(tree.root, min_surname, max_surname, min_awards, float('inf'), min_dblps, max_dblps)

    end_time_1 = time.time()

    # εμφάνιση των κόμβων μέσα στο διάστημα αναζήτησης
    print(f"Points within the specified range:")
    for node in results:
        print(node.point)

    # κενή λίστα για ανάκτηση των αντίστοιχων δεδομένων εκπαίδευσης για κάθε κόμβο
    df = pd.read_csv(csv_file_path)  # δημιουργία data frame από CSV αρχείο

    data = []  # λίστα για αποθήκευση κόμβων μαζί με εκπαίδευση
    unique_surnames = set()  # set για διαχείριση διπλότυπων

    for node in results:
        point = node.point
        surname = point[0]
        awards = point[1]
        dblp = point[2]

        # εισαγωγή ονομάτων, όχι διπλότυπων
        if surname in unique_surnames:
            continue

        # εξαγωγή δεδομένων εκπαίδευσης για το LSH
        education_text = df.loc[
            (df['Surname'] == surname) & (df['Awards'] == awards) & (df['Dblp'] == dblp),
            'Education'
        ].values[0]

        # ελεγχος για 'Education information not found'
        if education_text != 'Education information not found':
            unique_surnames.add(surname)  # πρόσθεση των επιστημόνων που έχουν δεδομένα εκπαίδευσης
            data.append([surname, awards, dblp, education_text])

    # μετατροπή του CSV σε DataFrame
    csv_columns = ['Surname', 'Awards', 'Dblp', 'Education']
    result_df = pd.DataFrame(data, columns=csv_columns)

    # LSH για 'Education'
    education_texts = result_df['Education'].tolist()
    education_texts_preprocessed = [preprocess_education(edu) for edu in education_texts]
    start_time_2 = time.time()
    similar_pairs_education = lsh_education(education_texts_preprocessed, result_df, threshold_education)

    # end time
    end_time_2 = time.time()

    # Υπολογισμός elapsed time
    elapsed_time_1 = end_time_1 - start_time_1
    elapsed_time_2 = end_time_2 - start_time_2

    total_elapsed_time = elapsed_time_1 + elapsed_time_2
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

            # μετατροπή αποτελεσμάτων results σε DataFrame
    result_df_education = pd.DataFrame(similar_pairs_education, columns=['Entry1', 'Entry2'])
    result_df_education.to_csv('Range_tree_results.csv', index=False)

    # εκτύπωση elapsed time
    print(f"Time taken for lsh: {total_elapsed_time} seconds")
