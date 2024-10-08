import requests
from bs4 import BeautifulSoup
import string
import pandas as pd
import re
import urllib.parse

class ScientistInfoExtractor:
    def __init__(self):
        # Αρχικοποίηση λιστών για την αποθήκευση πληροφοριών
        self.surnames = []
        self.awards_counts = []
        self.awards_lists = []
        self.education_info_list = []
        self.dblp_list = []

    def extract_education_info(self, soup):
        # Εύρεση των επικεφαλίδων (headings) που περιέχουν τη λέξη "education"
        headings = soup.find_all('span', {'class': 'mw-headline'})
        for heading in headings:
            if re.search(r'\beducation\b', heading.text, flags=re.IGNORECASE):
                education_paragraphs = heading.find_all_next(['p', 'ul', 'h2'])
                education_info = ''
                for elem in education_paragraphs:
                    if elem.name == 'p':
                        education_info += elem.text.strip() + ' '
                    elif elem.name == 'ul':
                        education_info += ', '.join([li.text.strip() for li in elem.find_all('li')]) + ' '
                    elif elem.name == 'h2':
                        break
                return education_info.strip()
        return "Education information not found"

    def get_max_record_info(self,scientist_name):
        def extract_max_record_info(soup):
            max_record_info = soup.find('span', {'id': 'max-record-info'})
            if max_record_info:
                return max_record_info.text
            return "Max record information not found"

        try:
            # Δημιουργία URL για αναζήτηση στην DBLP με βάση το όνομα του επιστήμονα
            publication_url = f"https://dblp.org/search?q={'+'.join(scientist_name.split())}"

            # Αίτηση στη σελίδα αναζήτησης DBLP
            publication_response = requests.get(publication_url)

            if publication_response.status_code == 200:
                publication_soup = BeautifulSoup(publication_response.text, 'html.parser')

                # Εύρεση του σχετικού συνδέσμου (link)
                exact_match_link = publication_soup.find('a',
                                                         string=re.compile(re.escape(scientist_name), re.IGNORECASE))

                if exact_match_link:
                    # Selenium WebDriver, για Chrome browser, για την DBLP
                    driver = webdriver.Chrome()

                    try:
                        driver.get(exact_match_link['href'])

                        # Αναμονή για το φορτωμένο περιεχόμενο της σελίδας
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                        )

                        # Ανάκτηση πληροφοριών max record από τη σελίδα χρησιμοποιώντας Selenium
                        max_record_info = extract_max_record_info(BeautifulSoup(driver.page_source, 'html.parser'))
                        print(f"Max Record Info for {scientist_name}: {max_record_info}")
                        # Προσθήκη στη λίστα dblp
                        self.dblp_list.append(max_record_info)

                        return max_record_info

                    except Exception as e:
                        print(f"Error processing {scientist_name}: {str(e)}")
                        return f"Error processing {scientist_name}"

                    finally:
                        # Κλείσιμο του WebDriver για την DBLP
                        driver.quit()

                else:
                    print(f"Exact match link not found for {scientist_name}")
                    self.dblp_list.append(0)
                    return 0
            else:
                print(f"Failed to retrieve publication page for {scientist_name}")
                return "Failed to retrieve publication page"

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"

    def extract_scientist_info(self, scientist_name):
        name_parts = scientist_name.split()
        surname = name_parts[-1]
        self.surnames.append(surname)

        # Δημιουργία URL για αναζήτηση του επιστήμονα στη Wikipedia
        scientist_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(scientist_name.replace(' ', '_'))}"

        # Αίτηση στη σελίδα του επιστήμονα στη Wikipedia
        scientist_response = requests.get(scientist_url)
        if scientist_response.status_code == 200:
            scientist_soup = BeautifulSoup(scientist_response.text, 'html.parser')
            print(f"Processing: {scientist_name}")

            # Εξαγωγή πληροφοριών εκπαίδευσης
            education_info = self.extract_education_info(scientist_soup)
            self.education_info_list.append(education_info)

            # Αναζήτηση των επικεφαλίδων που περιέχουν τις λέξεις 'Award' ή 'award'
            awards_heading = scientist_soup.find(
                lambda tag: tag.name == 'span' and re.search(r'(Award|award)', tag.text, re.IGNORECASE))
            if awards_heading:
                print("Awards heading found")

                # Εύρεση του επόμενου στοιχείου, είτε ως <ul>, είτε ως <p>
                next_sibling = awards_heading.find_next(['ul', 'p'])

                # Δημιουργία λίστας για αποθήκευση των βραβείων
                awards_list = []

                # Υπολογισμός του αριθμού των βραβείων
                if next_sibling and next_sibling.name == 'ul':
                    awards_count = len(next_sibling.find_all('li'))
                    self.awards_counts.append(awards_count)
                    self.awards_lists.append([])  # Προσθήκη κενής λίστας για συνέπεια
                    print(f"Awards count from <ul>: {awards_count}")
                elif next_sibling and next_sibling.name == 'p':
                    # Εύρεση όλων των <p> που ακολουθούν τις επικεφαλίδες βραβείων
                    p_elements = awards_heading.find_all_next('p')

                    # Επεξεργασία των <p>
                    for p_element in p_elements:
                        # Εξαγωγή μοναδικών βραβείων από το κείμενο
                        awards_text = p_element.get_text()
                        unique_awards = set(re.findall(r'(Award|awarded)', awards_text))
                        awards_list.extend(unique_awards)

                    print(f"Unique Awards List: {awards_list}")

                    # Προσθήκη της λίστας στην κύρια λίστα βραβείων
                    self.awards_lists.append(awards_list)
                    self.awards_counts.append(len(awards_list))  # Προσθήκη του πλήθους
                else:
                    print("Invalid next sibling. Skipping.")
                    self.awards_counts.append(0)
                    self.awards_lists.append(0)  # Προσθήκη κενής λίστας για συνέπεια

            else:
                print("Awards heading not found")
                self.awards_counts.append(0)
                self.awards_lists.append(0)  # Προσθήκη κενής λίστας για συνέπεια

        else:
            print(f"Failed to retrieve page for {scientist_name}")
            self.awards_counts.append(0)
            self.education_info_list.append("Education information not found")

# Ορισμός του URL που θα κάνουμε scraping
url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

# Αίτηση GET για τη λήψη της ιστοσελίδας
response = requests.get(url)
max_record_infos = []

# Δημιουργία ενός αντικειμένου ScientistInfoExtractor
extractor = ScientistInfoExtractor()

# Έλεγχος αν η αίτηση ήταν επιτυχής
if response.status_code == 200:
    # Χρήση BeautifulSoup για την ανάλυση της HTML σελίδας
    soup = BeautifulSoup(response.text, 'html.parser')

    # Προσπέλαση των επικεφαλίδων για κάθε γράμμα του αλφαβήτου
    for letter in string.ascii_uppercase:
        span_element = soup.find('span', {'class': 'mw-headline', 'id': letter})
        if span_element:
            # Εύρεση της λίστας των επιστημόνων για το συγκεκριμένο γράμμα
            scientist_list = span_element.find_next('ul')
            # Προσπέλαση κάθε επιστήμονα στη λίστα
            for scientist in scientist_list.find_all('li'):
                scientist_name_element = scientist.find('a')
                if scientist_name_element:
                    scientist_name = scientist_name_element.text
                    # Εξαγωγή πληροφοριών για τον επιστήμονα με τον extractor
                    extractor.extract_scientist_info(scientist_name)
                    extractor.get_max_record_info(scientist_name)

# Αποθήκευση των δεδομένων που συλλέξαμε σε ένα DataFrame του pandas
data = {
    'Surname': extractor.surnames,
    'Awards': extractor.awards_counts,
    'Education': extractor.education_info_list,
    'Dblp': extractor.dblp_list
}
df = pd.DataFrame(data)

# Αποθήκευση των δεδομένων σε ένα αρχείο CSV
df.to_csv('scientists.csv', index=False, encoding='utf-8')
