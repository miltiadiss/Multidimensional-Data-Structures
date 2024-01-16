import pandas as pd
import numpy as np
import random
import time
import matplotlib.pyplot as plt

class Node:
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right

def build_kdtree(points, depth=0):
    if not points:
        return None

    axis = depth % 3
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

    # Determine if we need to search the left and/or right branch
    search_left = query_point[axis][0] <= node.point[axis]
    search_right = node.point[axis] <= query_point[axis][1]

    # Recursively search left branch if necessary
    if search_left and node.left is not None:
        result.extend(range_search(node.left, query_point, depth + 1))

    # Check if the current node is within the range
    in_range = True
    for i in range(k):
        lower_bound = query_point[i][0]
        upper_bound = query_point[i][1]

        # Adjust the upper bound for string comparisons
        if isinstance(node.point[i], str) and isinstance(upper_bound, str):
            in_range = in_range and lower_bound <= node.point[i] <= upper_bound + chr(255)
        else:
            in_range = in_range and lower_bound <= node.point[i] <= upper_bound

    if in_range:
        result.append(node.point)

    # Recursively search right branch if necessary
    if search_right and node.right is not None:
        result.extend(range_search(node.right, query_point, depth + 1))

    return result

def shingle_education(text, k=2):
    # Tokenize the text into words
    words = text.split()

    # Create shingles by combining consecutive words
    shingles = [tuple(words[i:i + k]) for i in range(len(words) - k + 1)]

    return set(shingles)

def jaccard(s1, s2):
    intersect_size = len(s1.intersection(s2))
    union_size = len(s1.union(s2))
    return intersect_size / union_size

def func_hash(a, b, modulo):
    return lambda x: (a * x + b) % modulo

def bucket_creator(sign, bands, rows):
    buckets = []
    for band in range(bands):
        start = band * rows
        end = (band + 1) * rows
        buckets.append(hash(tuple(sign[start:end])))
    return buckets

def minhash_education(shingles, hashes=95):
    max_hash = 2 ** 32 - 1
    modulo = 2 ** 32
    random.seed(42)
    funcs = [(random.randint(0, max_hash), random.randint(0, max_hash)) for _ in range(hashes)]
    hash_functions = [lambda x, a=a, b=b: (a * hash(x) + b) % modulo for a, b in funcs]
    sign_x = [min(func(shingle) for shingle in shingles) for func in hash_functions]
    return sign_x

def lsh_education(query, df, threshold):
    # Filter out entries with "Education information not found"
    valid_entries = [(entry, surname) for entry, surname in zip(query, df['Surname']) if "Education information not found" not in entry]

    shingles_education = [shingle_education(entry) for entry, _ in valid_entries]

    signatures = [minhash_education(s) for s in shingles_education]

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

    final_pairs = []
    for i, j in pairs:
        similarity = jaccard(shingles_education[i], shingles_education[j])
        if similarity >= threshold:
            entry1, surname1 = valid_entries[i]
            entry2, surname2 = valid_entries[j]
            final_pairs.append(((entry1, surname1), (entry2, surname2)))

    return final_pairs


def result(kdtree, query_surname_range, query_award_range, query_publication_range, threshold_education):
    # Perform range search
    query_point = (query_surname_range, query_award_range, query_publication_range)
    start_time = time.perf_counter()  # Start timing
    points_in_range = range_search(kdtree, query_point)

    # Create a list to store the data for the CSV
    csv_data = []
    unique_surnames = set()  # To track unique surnames with valid education

    for point in points_in_range:
        surname, awards, dblp = point

        # Check if we've already added a valid entry for this surname
        if surname in unique_surnames:
            continue

        # Extract the education text for LSH
        education_text = df.loc[
            (df['Surname'] == surname) & (df['Awards'] == awards) & (df['Dblp'] == dblp),
            'Education'
        ].values[0]

        # Check if education text isn't 'Education information not found'
        if education_text != 'Education information not found':
            unique_surnames.add(surname)  # Add to the set of unique surnames
            csv_data.append([surname, awards, dblp, education_text])

    # Convert the CSV data to a DataFrame
    csv_columns = ['Surname', 'Awards', 'Dblp', 'Education']
    result_df = pd.DataFrame(csv_data, columns=csv_columns)
    result_df.to_csv('query_results.csv', index=False)

    # Example LSH usage for 'Education' field
    education_texts = result_df['Education'].tolist()
    similar_pairs_education = lsh_education(education_texts, result_df, threshold_education)

    end_time = time.perf_counter()  # End timing
    elapsed_time = end_time - start_time  # Calculate elapsed time

    for pair in similar_pairs_education:
        (entry1, surname1), (entry2, surname2) = pair
        print(f"Surname: {surname1} - Education: {entry1}")
        print(f"Surname: {surname2} - Education: {entry2}")
        print("---")

    # Convert results to DataFrame
    result_df_education = pd.DataFrame(similar_pairs_education, columns=['Entry1', 'Entry2'])
    result_df_education.to_csv('kd_similar_pairs.csv', index=False)
    return elapsed_time

# main
csv_file_path = 'scientists.csv'
df = pd.read_csv(csv_file_path)
points = df[['Surname', 'Awards', 'Dblp']].apply(lambda row: (row['Surname'], row['Awards'], row['Dblp']),
                                                 axis=1).tolist()

query_times = []
# Build KD-tree
kdtree = build_kdtree(points)

# Define query points for the range search
query_parameters = [
    (('A', 'T'), (0, 500), (0, 100), 0.2),
    (('K', 'V'), (0, 500), (0, 100), 0.2),
    (('B', 'S'), (1, 500), (1, 100), 0.1),
    (('D', 'W'), (2, 500), (2, 100), 0.15),
    (('J', 'T'), (0, 500), (2, 100), 0.1)
]

count = 0
query_count = []
# Call the function to perform range search, LSH similarity queries, and save results
for surname_range, award_range, publication_range, threshold in query_parameters:
    count = count + 1
    elapsed_time = result(kdtree, surname_range, award_range, publication_range, threshold)
    query_times.append(elapsed_time)
    query_count.append(count)

plt.figure(figsize=(10, 6))
plt.plot(query_count, query_times, color='blue')
plt.xlabel('Queries')
plt.ylabel('Time (seconds)')
plt.title('Time Taken for Different Queries')
plt.xticks(rotation=45)
plt.show()
