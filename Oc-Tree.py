import pandas as pd
import time
from LSH import *


# συνάρτηση για την μετατροπή των γραμμάτων σε αριθμό
def letter_normalization(letter):
    return max(ord(letter.upper()) - 65, 0)


# κλάση που αναπαριστά ένα 3D σημείο
class Point:
    def __init__(self, x, y, z, data=None):
        self.x = x
        self.y = y
        self.z = z
        self.data = data


# κλάση που αναπαριστά έναν κόμβο μέσα στο Octree δέντρο
class OctreeNode:
    def __init__(self, x, y, z, w, h, d):
        self.x = x  # συντεταγμένη x
        self.y = y  # συντεταγμένη y
        self.z = z  # συντεταγμένη z
        self.w = w  # πλάτος
        self.h = h  # ύψος
        self.d = d  # βάθος
        self.points = []  # λίστα να αποθηκεύει όλα τα σημεία του κόμβου
        self.subnodes = [None] * 8  # λίστα με τους υπο-κόμβους

        # οριοθέτηση των ορίων του κύβου με βάση τις συντεταγμένες (x, y, z) και τις διαστάσεις (w, h, d)
        self.left = x - w / 2
        self.right = x + w / 2
        self.bottom = y - h / 2
        self.top = y + h / 2
        self.back = z - d / 2
        self.front = z + d / 2

    def insert(self, point):
        # έλεγχος αν το σημείο είναι μέσα στα όρια του κόμβου
        if not self.boundary(point):
            return

        # αν υπάρχει χώρος στον τρέχοντα κόμβο (points<8), προσθέτουμε το σημείο
        if len(self.points) < 8:
            self.points.append(point)

        else:
            # άμα ο κόμβος είναι γεμάτος και δεν έχει διασπαστεί τον διασπάμε
            if self.subnodes[0] is None:
                self.divide()

            # εισαγωγή του σημείου στον κατάλληλο υπο-κόμβο
            for subnode in self.subnodes:
                subnode.insert(point)

    # συνάρτηση που χρησιμοποιείται για την διαίρεση ενός κόμβου σε 8 υπο-κομβους
    def divide(self):
        x, y, z = self.x, self.y, self.z
        w, h, d = self.w / 2, self.h / 2, self.d / 2  # Κάθε υπο-κόμβος θα έχει διαστάσεις ίσες με το μισό του αρχικού κόμβου

        # δημιουργία των 8 υπο-κόμβων με τις κατάλληλες διαστάσεις
        self.subnodes[0] = OctreeNode(x - w / 2, y - h / 2, z - d / 2, w, h, d)
        self.subnodes[1] = OctreeNode(x + w / 2, y - h / 2, z - d / 2, w, h, d)
        self.subnodes[2] = OctreeNode(x + w / 2, y + h / 2, z - d / 2, w, h, d)
        self.subnodes[3] = OctreeNode(x - w / 2, y + h / 2, z - d / 2, w, h, d)
        self.subnodes[4] = OctreeNode(x - w / 2, y - h / 2, z + d / 2, w, h, d)
        self.subnodes[5] = OctreeNode(x + w / 2, y - h / 2, z + d / 2, w, h, d)
        self.subnodes[6] = OctreeNode(x + w / 2, y + h / 2, z + d / 2, w, h, d)
        self.subnodes[7] = OctreeNode(x - w / 2, y + h / 2, z + d / 2, w, h, d)

    # συνάρτηση για να ελέγχει αν το σημείο είναι μέσα στα όρια του κόμβου
    def boundary(self, point):
        return (
                self.left <= point.x < self.right and
                self.bottom <= point.y < self.top and
                self.back <= point.z < self.front
        )


# συνάρτηση για την ανάγνωση των δεδομένων απο το csv
def read_data():
    df = pd.read_csv("scientists.csv")
    points = []

    for i in range(len(df)):
        x = letter_normalization(df.iloc[i]['Surname'][0])
        y = df.iloc[i]['Awards']
        z = df.iloc[i]['Dblp']
        data = {
            'Surname': df.iloc[i]['Surname'],
            'Awards': df.iloc[i]['Awards'],
            'Dblp': df.iloc[i]['Dblp'],
            'Education': df.iloc[i]['Education']
        }
        point = Point(x, y, z, data)
        points.append(point)

    return points


# συνάρτηση για την κατασκευή του δέντρου
def build_octree():
    points = read_data()

    # εύρεση της μέγιστης και της ελάχιστης τιμής σε κάθε διάσταση
    min_values = {'x': min(point.x for point in points),
                  'y': min(point.y for point in points),
                  'z': min(point.z for point in points)}
    max_values = {'x': max(point.x for point in points),
                  'y': max(point.y for point in points),
                  'z': max(point.z for point in points)}

    # εύρεση πλάτους, ύψους, βάθους
    octree_width = max(0, max_values['x'] - min_values['x'])
    octree_height = max(0, max_values['y'] - min_values['y'])
    octree_depth = max(0, max_values['z'] - min_values['z'])

    # δημιουργία της ρίζας του Octree
    octree = OctreeNode(
        min_values['x'] + octree_width / 2,
        min_values['y'] + octree_height / 2,
        min_values['z'] + octree_depth / 2,
        octree_width,
        octree_height,
        octree_depth
    )

    # εισαγωγή των σημείων μέσα στο δέντρο
    for point in points:
        point.x = max(min(point.x, octree.right - 0.001), octree.left + 0.001)
        point.y = max(min(point.y, octree.top - 0.001), octree.bottom + 0.001)
        point.z = max(min(point.z, octree.front - 0.001), octree.back + 0.001)
        octree.insert(point)

    return octree


# συνάρτηση για αναζήτηση στο δέντρο σημείων που ικανοποιούν κάποια όρια
def query_octree(node, min_letter, max_letter, min_awards, min_dblp, max_dbpl):
    results = []
    if node is not None:
        for point in node.points:
            # έλεγχος αν το σημείο είναι μέσα στα όρια
            if (
                    min_letter <= point.x <= max_letter and
                    min_awards <= point.y and
                    min_dblp <= point.z <= max_dbpl
            ):
                results.append(point.data)

        # αναζήτηση στους υποκόμβους
        for subnode in node.subnodes:
            results.extend(query_octree(subnode, min_letter, max_letter, min_awards, min_dblp, max_dbpl))
    return results


def main_Oc_Tree():
    # κατασκευή του Octree
    octree = build_octree()

    # εισαγωγή από τον χρήστη των σηεμίων αναζήτησης
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
    print("The query that you created is the following ! ")
    print(
        "Find the computer scientists from Wikipedia that their letters belongs in the interval [" + min_letter + "-" + max_letter + "],have won more than " + str(
            min_awards) + " prizes and their DBLP record belongs in the interval [" + str(
            min_dblps) + " ," + str(max_dblps) + "] !")
    print("Generating Answer")

    # μετατροπή των γραμμάτων σε αριθμούς
    min_letter = letter_normalization(min_letter)
    max_letter = letter_normalization(max_letter)

    # έναρξη χρόνου
    start_time_1 = time.time()

    # αναζήτηση
    query_results = query_octree(octree, min_letter, max_letter, min_awards, min_dblps, max_dblps)

    # λήξη χρόνου
    end_time_1 = time.time()
    # υπολογισμός συνολικού χρόνου για αναζήτηση
    elapsed_time_1 = end_time_1 - start_time_1

    # εκτυπωση αποτελεσμάτων αναζήτησης
    for result in query_results:
        print(f"{result['Surname']},{result['Awards']},{result['Dblp']}")

    # φιλτραρουμε τα αποτελέσματα ώστε στο result να υπάρχουν μόνο αυτοί που έχουν education
    results = [result for result in query_results if "Education information not found" not in result['Education']]

    # αποθήκευση των αποτελεσμάτων σε dataframe
    result_df = pd.DataFrame(results)

    # εξαγωγή 'Education' από τα παραπάνω αποτελέσματα
    education_data = [result['Education'] for result in results]
    education_data_preprocessed = [preprocess_education(edu) for edu in education_data]

    # έναρξη χρόνου
    start_time_2 = time.time()
    # εκτέλεση lsh ομοιότητας
    similar_pairs_education = lsh_education(education_data_preprocessed, result_df, lsh_sim)

    # λήξη χρόνου
    end_time_2 = time.time()

    # υπολογισμός συνολικού χρόνου για lsh
    elapsed_time_2 = end_time_2 - start_time_2

    # Αποθηκεύουμε τα μοναδικά ονόματα από όλα τα ζευγάρια με κοινή εκπαίδευση
    unique_surnames_in_pairs = set()

    # εκτύπωση αποτελεσμάτων ομοιότητας
    if len(similar_pairs_education) == 0:
        print("\nThere are no scientists with similarity " + str(int(lsh_sim * 100)) + "%.")
    else:
        print("\nThe scientists with similarity " + str(int(lsh_sim * 100)) + "% are the following:\n")
        for pair in similar_pairs_education:
            (entry1, surname1), (entry2, surname2) = pair
            if surname1 in [result['Surname'] for result in results] and surname1 not in unique_surnames_in_pairs:
                awards1, dblp1 = result_df.loc[result_df['Surname'] == surname1, ['Awards', 'Dblp']].iloc[0]
                print(f"Surname: {surname1}, #Awards: {awards1}, #DBLP_Record: {dblp1}")
                unique_surnames_in_pairs.add(surname1)
            if surname2 in [result['Surname'] for result in results] and surname2 not in unique_surnames_in_pairs:
                awards2, dblp2 = result_df.loc[result_df['Surname'] == surname2, ['Awards', 'Dblp']].iloc[0]
                print(f"Surname: {surname2}, #Awards: {awards2}, #DBLP_Record: {dblp2}")
                unique_surnames_in_pairs.add(surname2)

    # αποθήκευση των αποτελεσμάτων σε dataframe
    result_df_education = pd.DataFrame(similar_pairs_education, columns=['Entry1', 'Entry2'])
    result_df_education.to_csv('Oc_tree_results.csv', index=False)

    # συνολικός χρόνος για αναζητηση και lsh
    elapsed_time = elapsed_time_1 + elapsed_time_2

    # εκτύπωση του χρόνου
    print(f"Time taken for lsh {elapsed_time} seconds")
