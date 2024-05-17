import math
import pandas as pd
import time
from math import *
from LSH import *


# Δημιουργία της κλάσης Rect για την δημιουργία ορθογωνίων
class Rect:
    def __init__(self, id, x_low, y_low, z_low, x_high, y_high, z_high, full_name, education):
        # Αρχικοποίηση συντεταγμένων ορθογωνίου
        self.id = id
        self.x_low = ord(x_low[0]) - ord('A') + 1  # Αλφαριθμητική κανονικοποίηση
        self.y_low = y_low
        self.z_low = z_low
        self.x_high = ord(x_high[0]) - ord('A') + 1  # Αλφαριθμητική κανονικοποίηση
        self.y_high = y_high
        self.z_high = z_high
        # Αρχικοποίηση μεταβλητών για αποθήκευση τιμών για το Range-Search + LSH
        self.full_name = full_name
        self.education = education

    # Επιστροφή πλειάδας συντεταγμένων
    @property
    def get_points(self):
        return self.x_low, self.y_low, self.z_low, self.x_high, self.y_high, self.z_high


# Δημιουργία της κλάσης Node για την δημιουργία κόμβων στο δέντρο
class Node:
    def __init__(self, id: int):
        self.id = id  # Αναγνωριστικό κόμβου
        self.idx = []  # Λίστα αποθήκευσης δεικτών για τα MBR

    # δημιουργία και επιστροφή MBR κάθε κόμβου
    # και εύρεση μέγιστης και ελάχιστης τιμής για κάθε διάσταση (x, y, z)
    @property
    def mbr(self):
        min_xl = self.idx[0][1][0]
        min_yl = self.idx[0][1][1]
        min_zl = self.idx[0][1][2]
        max_xh = self.idx[0][1][3]
        max_yh = self.idx[0][1][4]
        max_zh = self.idx[0][1][5]

        for i in self.idx:
            min_xl = min(min_xl, i[1][0])
            min_yl = min(min_yl, i[1][1])
            min_zl = min(min_zl, i[1][2])
            max_xh = max(max_xh, i[1][3])
            max_yh = max(max_yh, i[1][4])
            max_zh = max(max_zh, i[1][5])

        return min_xl, min_yl, min_zl, max_xh, max_yh, max_zh

    # Προσθήκη ευρετηρίου στους αντίστοιχους κόμβους
    def add_idx(self, x):
        self.idx.append(x)


# δημιουργία τησ κλάσης LeafNode για την δημιουργία φύλλων στο δέντρο
class LeafNode:
    def __init__(self, id: int, entries: list):
        self.id = id  # Αναγνωριστικό φύλλου
        self.entries = entries  # Καταχωρήσεις στα φύλλα

    # δημιουργία και επιστροφή MBR κάθε φύλλου
    # και εύρεση μέγιστης και ελάχιστης τιμής για κάθε διάσταση (x, y, z)
    @property
    def mbr(self):
        min_x_l = min(e.x_low for e in self.entries)
        min_yl = min(e.y_low for e in self.entries)
        min_zl = min(e.z_low for e in self.entries)
        max_x_h = max(e.x_high for e in self.entries)
        max_y_h = max(e.y_high for e in self.entries)
        max_z_h = max(e.z_high for e in self.entries)

        return min_x_l, min_yl, min_zl, max_x_h, max_y_h, max_z_h


# δημιουργία της κλάσης RTree για την δημιουργία ολόκληρου του δέντρου μας
class RTree:
    def __init__(self, max_cap: int):
        self.root = None  # ρίζα δέντρου
        self.__id = 0  # Αναγνωριστικά κόμβων
        self.max_cap = max_cap  # Μέγιστος αριθμός εισόδων σε κόμβο
        self.childList = []  # Λίστα με παιδιά του δέντρου
        self.node_pool = []  # Λίστα με τους κόμβους του δέντρου

        self.leaf_counter = 0  # Αριθμός των leaf node που έχουν προστεθεί
        self.height = 1  # Ύψος του R-Tree

    # Συνάρτηση εισαγωγής φύλλων στο δέντρο
    def insert_leaf(self, entries):
        self.leaf_counter += 1  # Συνολικός αριθμός φύλλων στο δέντρο
        self.childList.append(self.getId())  # Προσθήκη αναγνωριστικού  νέου φύλλου στην λίστα
        self.node_pool.append(LeafNode(self.getId(), entries))  # Δημιουργία φύλλου
        self.__increment()  # Αύξηση αναγνωριστικών + 1

    # Συνάρτηση υπολογισμού νέων επιπέδων που χρειάζονται
    def create_upper_levels(self):
        x = ceil(len(self.childList) / self.max_cap)
        # περίπτωση εισαγωγής μόνο ενός κόμβου
        if x == 1:
            self.root = Node(self.getId())  # Δημιουργία ενός νέου κόμβου ρίζας
            for idx in self.childList:
                child = self.node_pool[idx]  # Ανάκτηση των παιδιών του επιπέδου αυτού
                self.root.add_idx((child.id, child.mbr))  # προσθήκη ως εγγόνια σε αυτόν τον κόμβο

            self.node_pool.append(self.root)  # προσθήκη του νέου κόμβου στην λίστα με τους νέους κόμβους
            self.height += 1  # Αύξηση του ύψους του δέντρου κατά ένα
        # περίπτωση εισαγωγής περισσότερων του ενούς κόμβου
        else:
            self.insert_nodes()  # κάλεσμα της μεθόδου του εισαγωγής κόμβων
            self.height += 1  # Αύξηση του ύψους του δέντρου κατά ένα
            self.create_upper_levels()  # επανάληψη τησ συνάρτησης

    # Συνάρτηση εισαγωγής κόμβων στα επίπεδα πάνοπ τα φύλλα
    def insert_nodes(self):
        buffer = []  # Αναγνωριστικά νέων κόμβων
        child_indexes = [self.childList[i: i + self.max_cap] for i in range(0, len(self.childList),
                                                                            self.max_cap)] # Θέτουμε την μέγιστη και ελάχιστη χωριτικότητα
        # Για κάθε τέτοιο κομμάτι δημιουργούμε ενάν νέο κόμβο και τον προσθέτουμε στο ευρετήριο node_pool
        for chunk in child_indexes:
            buffer.append(self.getId())
            new_node = Node(self.getId())

            for idx in chunk:
                child = self.node_pool[idx]
                new_node.add_idx((child.id, child.mbr))

            self.node_pool.append(new_node)
            self.__increment()

        self.childList = buffer

    # Αύξηση των αναγνωριστικών κόμβων
    def __increment(self):
        self.__id += 1

    # Επιστροφή των αναγνωριστικών κόμβων
    def getId(self):
        return self.__id

    # Συνάρτηση εκτύπωσης δέντρου
    def printTree(self):
        unique_mbrs = set()  # Ανίχνευση μοναδικών MBRs

        print('-' * 30 + "Printing Tree" + '-' * 27)
        # Ελέγχουμε τον τύπο του κόμβου και εκτυπώνουμε τις κατάλληλεσ πληροφορίες
        self.__printNode(self.root, 0, unique_mbrs, is_root=True)
        print('-' * 70 + '\n')

    def __printNode(self, node, depth, unique_mbrs, is_root=False):
        # Αν ο κόμβος είναι LeafNode, εκτυπώνει το MBR του και τις εγγραφές που περιέχει
        if isinstance(node, LeafNode):
            mbr = node.mbr
            if mbr not in unique_mbrs:
                # Αν ο κόμβος είναι ο root εκτύπωσε τον
                if is_root:
                    print(f"Root - MBR: {mbr}")
                # Αν όχι εκτύπωσε το φύλλο του δέντρου σαν MBR και τις αντίστοιχες εγγραφές του
                else:
                    print(f"{'  ' * depth}Leaf - MBR: {mbr}")
                unique_mbrs.add(mbr)
                for entry in node.entries:
                    print(f"{'  ' * (depth + 1)}Entry: {entry.full_name}, {entry.y_low}, {entry.z_low}")
        # Αν ο κόμβος είναι Node, εκτυπώνει το MBR του και αναδρομικά καλεί τον εαυτό του για κάθε παιδί του
        elif isinstance(node, Node):
            mbr = node.mbr
            if mbr not in unique_mbrs:
                if is_root:
                    print(f"Root - MBR: {mbr}")
                else:
                    print(f"{'  ' * depth}Node - MBR: {mbr}")
                unique_mbrs.add(mbr)
                for idx, (ptr, child_mbr) in enumerate(node.idx):
                    child = self.node_pool[ptr]
                    self.__printNode(child, depth + 2, unique_mbrs)
        # Αν ο κόμβος είναι Rect, εκτυπώνει τις κατάλληλες πληροφορίες που περιέχει
        elif isinstance(node, Rect):
            mbr = node.get_points
            if mbr not in unique_mbrs:
                print(f"{'  ' * depth}Entry: Surname: {node.full_name}, MBR: {mbr}")
                unique_mbrs.add(mbr)

    # Συνάρτηση υλοποίησης Range Search
    def range_search(self, query_rect, similarity):
        start1 = time.time()
        result_entries = set()  # Αποθήκευση αποτελεσμάτων Range Search
        self.__range_search_recursive(self.root, query_rect, result_entries,
                                      full_name='Root')  # Αναδρομική αναζήτηση στο δέντρο μασ για τα κατάλληλα διαστήματα
        end1 = time.time()
        elapsed_time1 = end1 - start1

        print(f"Performing range search with query rectangle: {query_rect.get_points}")
        for entry in result_entries:
            print(f"Entry: {entry.full_name}, {entry.y_low}, {entry.z_low}")

        # κενή λίστα για ανάκτηση των αντίστοιχων δεδομένων εκπαίδευσης για κάθε κόμβο
        file_path = "scientists.csv"
        df = pd.read_csv(file_path)  # δημιουργία data frame από CSV αρχείο

        data = []  # λίστα για αποθήκευση κόμβων μαζί με εκπαίδευση
        unique_surnames = set()  # set για διαχείριση διπλότυπων
        result_list = []
        for entry in result_entries:
            surname = entry.full_name
            awards = entry.y_low
            dblp = entry.z_low

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

        # Αρχικοποίηση του threshold με κατάλληλη τιμή
        threshold_education = similarity

        # LSH για 'Education'
        education_texts = result_df['Education'].tolist()
        education_texts_preprocessed = [preprocess_education(edu) for edu in education_texts]

        start2 = time.time()
        similar_pairs_education = lsh_education(education_texts_preprocessed, result_df, threshold_education)
        end2 = time.time()

        elapsed_time2 = end2 - start2

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
        result_df_education.to_csv('R_tree_results.csv', index=False)

        # Υπολογισμός συνολικής χρονομέτρησης
        print('Execution time:', str(elapsed_time1 + elapsed_time2), 'seconds')

    def __range_search_recursive(self, node, query_rect, result_entries, full_name=None):
        # Έλεγχος για το αν βρισκόμαστε σε φύλλο του δέντρου
        if isinstance(node, LeafNode):
            for entry in node.entries:
                # Έλεγχος καταχωρήσεων κόμβου
                if self.__is_entry_inside_query(entry, query_rect):
                    result_entries.add(entry)
        # Έλεγχος για το αν βρισκόμαστε κάπου αλλού στο δέντρο
        elif isinstance(node, Node):
            for idx, (ptr, child_mbr) in enumerate(node.idx):
                child = self.node_pool[ptr]
                # Έλεγχος MBR
                if self.__is_mbr_inside_query(child_mbr, query_rect):
                    child_full_name = f"{full_name} - Child {idx + 1}"
                    self.__range_search_recursive(child, query_rect, result_entries, full_name=child_full_name)

    # Συνάρτηση ελέγχου καταχωρήσεων κόμβου μέσα σε ένα καθορισμένο MBR του ερωτήος
    def __is_entry_inside_query(self, entry, query_rect):
        return (
                query_rect.x_low <= entry.x_low <= query_rect.x_high and
                query_rect.y_low <= entry.y_low <= query_rect.y_high and
                query_rect.z_low <= entry.z_low <= query_rect.z_high
        )

    # Συνάρτηση ελέγχου MBR αν είναι μέσα σε ένα καθορισμένο MBR του ερωτήος
    def __is_mbr_inside_query(self, mbr, query_rect):
        return (
                query_rect.x_low <= mbr[3] and
                query_rect.x_high >= mbr[0] and
                query_rect.y_low <= mbr[4] and
                query_rect.y_high >= mbr[1] and
                query_rect.z_low <= mbr[5] and
                query_rect.z_high >= mbr[2]
        )


# δημιουργία συνάρτησης calc
def calc(size):
    n = 4  # Μέγιστος αριθμός σε κάθε κόμβο
    leaf_level_pages = ceil(size / n)  # Μέγιστος αριθμός φύλλων
    s = ceil(sqrt(leaf_level_pages))  # Μέγιστος αριθμός διαμοιράσεων
    return n, s


def main_R_tree():
    data_set = set()
    file_path = "scientists.csv"  # Ανάγνωση δεδομένων εισαγωγής
    df = pd.read_csv(file_path)
    # Δημιουργία αντικειμένων RECT με βάση τα δεδομένα που διαβάσαμε
    for idx, row in df.iterrows():
        entry = Rect(
            id=idx,
            x_low=row['Surname'],
            y_low=row['Awards'],
            z_low=row['Dblp'],
            x_high=row['Surname'],
            y_high=row['Awards'],
            z_high=row['Dblp'],
            full_name=row['Surname'],
            education=row['Education']
        )
        data_set.add(entry)
    # Μετατροπή αντικειμένων RECT σε λίστα
    data = list(data_set)
    # ταξινόμηση των αντικειμένων με βάση τις διαστάσεις (x,y,z)
    data.sort(key=lambda entry: (
        entry.x_low, entry.y_low, entry.z_low, entry.x_high, entry.y_high, entry.z_high, entry.full_name))

    # Μέγιστη χωρητικότητα και slices
    max_cap, s = calc(len(data))
    # Διαχωρίζουμε τα ταξινομημένα δεδομένα με βάση τις προηγούμενες τιμές
    data = [data[x:x + (s * max_cap)] for x in range(0, len(data), s * max_cap)]
    # Αρχικοποιούμε την κλάση του δέντρου μας
    tree = RTree(max_cap)

    # Εισάγουμε τα διαχωρισμένα και ταξινομημένα αντικείμενα μας με βάση στο δέντρο μας
    for sublist in data:
        for i in range(0, len(sublist), max_cap):
            tree.insert_leaf(sublist[i: i + max_cap])
    tree.create_upper_levels()

    # εμφάνιση δέντρου
    # tree.printTree()

    first_letter = input("Press the first letter of the query (ex.A, B, C...):").upper()
    while not first_letter.isalpha():
        first_letter = input("Press the first letter you want in the right form:")
    second_letter = input("Press the second letter of the query (ex.A, B, C...):").upper()
    while not second_letter.isalpha():
        second_letter = input("Press the second letter you want in the right form:")
    min_awards = int(input("Press the minimum awards of the query (ex.0,1,2...) :"))
    max_awards = math.inf
    min_dblps = int(input("Press the minimum DBLP records of the query (ex.0,1,2...) :"))
    max_dblps = int(input("Press the maximum DBLP records of the query (ex.0,1,2...) :"))
    lsh_sim = float(input("Give the LSH percentage of similarity between the scientists (ex.0.5->50%):"))
    print("The query that you created is the following ! ")
    print(
        "Find the computer scientists from Wikipedia that their letters belongs in the interval [" + first_letter + "-" + second_letter + "],have won more than " + str(
            min_awards) + " awards and their DBLP record belongs in the interval [" + str(
            min_dblps) + " ," + str(max_dblps) + "] !")
    print("Generating Answer")
    # Υπολογισμός Range search
    query_rect = Rect(id=-1, x_low=first_letter, y_low=min_awards, z_low=min_dblps, x_high=second_letter,
                      y_high=max_awards, z_high=max_dblps, full_name='', education='')

    # Εμφάνιση αποτελεσμάτων Range search
    tree.range_search(query_rect, lsh_sim)
