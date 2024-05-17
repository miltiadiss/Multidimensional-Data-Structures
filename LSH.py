import random
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
nltk.download('stopwords')


def shingle_education(text, k=2):
    shingle_set = []
    for i in range(len(text) - k + 1):
        shingle_set.append(text[i:i + k])
    return set(shingle_set)


def jaccard(s1, s2):
    # υπολογισμός |s1∩s2|
    # υπολογισμός |s1∪s2|
    # υπολογισμός Jaccard similarity
    return len(s1.intersection(s2)) / len(s1.union(s2))


def bucket_creator(sign, bands, rows):
    buckets = []
    for band in range(bands):
        # Υπολογισμός αρχής συνάφειας του Band
        start = band * rows
        # Υπολογισμός τέλους συνάφειας του Band
        end = (band + 1) * rows
        # Αποθήκευση των buckets στην λίστα
        buckets.append(hash(tuple(sign[start:end])))
    return buckets


def minhash_education(shingles, hashes=95):
    # Υπολογισμός μέγιστου δυνατού hash value
    max_hash = 2 ** 32 - 1
    modulo = 2 ** 32
    # γεννήτρια τυχαίων αριθμών για την αναπαραγωγή των αποτελεσμάτων.
    random.seed(42)
    # Δημιουργία ζευγαριών Hash Functions
    funcs = [(random.randint(0, max_hash), random.randint(0, max_hash)) for _ in range(hashes)]
    # Δημιουργία hash Values απο τα hash functions
    hash_functions = [lambda x, a=a, b=b: (a * hash(x) + b) % modulo for a, b in funcs]
    # Δημιουργία signature απο τα Hash Values
    sign_x = [min(func(shingle) for shingle in shingles) for func in hash_functions]
    return sign_x


def lsh_education(query, df, threshold):
    # φιλτράρισμα εισαγωγών αν έχουν σαν εγγραφή στο education το "Education information not found"
    valid_entries = [(entry, surname) for entry, surname in zip(query, df['Surname']) if
                     "Education information not found" not in entry]
    # Μετατροπή εγγραφών σε shingles
    shingles_education = [shingle_education(entry) for entry, _ in valid_entries]
    # Δημιουργία κατάλληλων υπογραφών για τα shingles μας
    signatures = [minhash_education(s) for s in shingles_education]
    # Ανάθεση των υπογραφών αυτών σε κατάλληλα Buckets
    bands = 15
    rows = 12
    buckets = [bucket_creator(sign, bands, rows) for sign in signatures]

    pairs = set()
    for i, buckets1 in enumerate(buckets):
        for j, buckets2 in enumerate(buckets):
            if i != j and any(b1 == b2 for b1, b2 in zip(buckets1, buckets2)):
                if i < j:
                    pairs.add((i, j))
                else:
                    pairs.add((j, i))
    # Υπολογισμός των πιθανοτήτων ομοιότητας των ζευγαριών με χρηση της jaccard
    # και επιστροφή κατάλληλων ζευγαριών με ομοιότητα μεγαλύτερη από ή ίση με το threshold μας
    final_pairs = []
    for i, j in pairs:
        similarity = jaccard(shingles_education[i], shingles_education[j])
        if similarity >= threshold:
            entry1, surname1 = valid_entries[i]
            entry2, surname2 = valid_entries[j]
            final_pairs.append(((entry1, surname1), (entry2, surname2)))

    return final_pairs


def preprocess_education(education_text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()

    # μετατροπή όλων των γραμμάτων σε μικρά
    education_text = education_text.lower()

    # Tokenize το κείμενο σε λέξεις
    words = education_text.split()

    # εφαρμογή stemming and αφαίρεση stopwords
    processed_words = [stemmer.stem(word) for word in words if word not in stop_words]

    # σύνδεση στοιχείων λίστας ως μεμονωμένο string 
    processed_text = ' '.join(processed_words)

    return processed_text
