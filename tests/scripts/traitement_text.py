import PyPDF2
from elasticsearch import Elasticsearch, ConnectionError
from elasticsearch.helpers import bulk
import spacy
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV

nlp = spacy.load("fr_core_news_sm")
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

try:
    es = Elasticsearch(["http://localhost:9200"], timeout=60)
    # Suppression de l'index, par exemple:
    es.indices.delete(index='nom_de_l_index', ignore=[400, 404])
except ConnectionError as e:
    print(f"Erreur de connexion: {e}")


def extract_text_from_pdf_path(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return ADJ
    elif tag.startswith('V'):
        return VERB
    elif tag.startswith('N'):
        return NOUN
    elif tag.startswith('R'):
        return ADV
    else:
        return NOUN

# def preprocess_text_cv(text):
#     text = text.lower()
#     text = re.sub(r'\S+@\S+', '', text)
#     text = re.sub(r'http\S+|www\S+|https\S+', '', text)
#     text = re.sub(r'\b\d{10,13}\b', '', text)
#     text = re.sub(r'page \d+ of \d+', '', text)
#     text = re.sub(r'page \d+ de \d+', '', text)
#     text = re.sub(r'page \d+ sur \d+', '', text)
#     text = re.sub(r'\b\d{4}\b', '', text)
#     months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
#     month_pattern = re.compile(r'\b(' + '|'.join(months) + r')\b', re.IGNORECASE)
#     text = month_pattern.sub('', text)
#     text = re.sub(r'\W', ' ', text)
#     text = re.sub(r'\d+', '', text)
#     words = nltk.word_tokenize(text)
#     pos_tags = nltk.pos_tag(words)
#     lemmatizer = WordNetLemmatizer()
#     lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in pos_tags]
#     lemmatized_text = ' '.join(lemmatized_words)
#     sensitive_words = ['marié', 'mariée', 'enfant', 'enfants', 'âge', 'ans', 'nom', 'prénom', 'adresse', 'téléphone', 'tél', 'portable', 'mobile', 'email', 'page', 'coordonnées', 'autres', 'plus', 'autre', 'maintenant', 'aujourd\'hui', 'but', 'd\'usage', 'depuis', 'ainsi', 'aussi', 'donc', 'alors', 'comme', 'leur', 'moins', 'mes', 'ton', 'ta', 'tes', 'ma', 'mon', 'ses', 'son', 'sa', 'principal', 'or', 'and', 'principal', 'principaux', 'principal', 'principales', 'nouvelles', 'nouveaux', 'nouvelle', 'nouveau', 'chaque', 'il', 'y a']
#     pattern = re.compile(r'\b(' + '|'.join(sensitive_words) + r')\b', re.IGNORECASE)
#     lemmatized_text = pattern.sub('', lemmatized_text)
#     words = nltk.word_tokenize(lemmatized_text)
#     pos_tags = nltk.pos_tag(words)
#     words = [word for word, pos in pos_tags if pos not in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'PRP', 'PRP$', 'WP', 'WP$', 'IN', 'MD', 'DT']]
#     words = words[3:]
#     french_stopwords = set(stopwords.words('french'))
#     words = [word for word in words if word not in french_stopwords]
#     text = ' '.join(words)
#     doc = nlp(text)
#     lemmatized_words = []
#     for token in doc:
#         if token.pos_ not in ["VERB", "ADJ"]:
#             lemmatized_words.append(token.lemma_)
#     lemmatized_text = ' '.join(lemmatized_words)
#     return lemmatized_text



def index_document(index_name, doc_id, document):
    es.index(index=index_name, id=doc_id, document=document)



def search_matching_cvs(mission_text, top_n=5):
    preprocessed_mission_text = mission_text
    query = {
        "query": {
            "match": {
                "content": preprocessed_mission_text
            }
        }
    }
    results = es.search(index="cvs", body=query, size=top_n)
    return results['hits']['hits']

# create_index("cvs")
# create_index("missions")

def print_index_content(index_name):
    try:
        response = es.search(index=index_name, body={"query": {"match_all": {}}})
        hits = response['hits']['hits']
        print(f"Index content for '{index_name}':")
        for hit in hits:
            print(f"ID: {hit['_id']}")
            print(f"Source: {hit['_source']}")
            print("------------")
    except Exception as e:
        print(f"Error: {e}")

def create_index(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "standard"
                        }
                    }
                }
            }
        })
        print(f"Index '{index_name}' created.")



def delete_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

def process_and_index_cvs(cv_texts): # ici cv_texts est une liste de tuples ( cv_filename,cv_text)
    for cv_filename, cv_text in cv_texts:
        index_document("cvs", cv_filename, {"filename": cv_filename, "content": cv_text})



# def display_matching_cvs(results):
#     for i, result in enumerate(results):
#         score = result['_score']
#         filename = result['_source']['filename']
#         content = result['_source']['content']
        


# mission_text = 'SONARQUBE'
# matching_cvs = search_matching_cvs(mission_text)
# display_matching_cvs(matching_cvs)



'''Suppression des espaces blancs superflus : Utilisez strip() et split() pour enlever les espaces en trop.

1-Suppression des mots courts : Filtrez les mots qui sont trop courts pour être significatifs.
2-Suppression des doublons : Évitez les mots dupliqués.
3-Correction orthographique : Vous pouvez utiliser des bibliothèques comme spellchecker pour corriger les fautes d'orthographe.
4-Traitement des n-grams : Utiliser des n-grams pour capturer le contexte pourrait améliorer certains cas d'utilisation.
5-Reconnaissance d'entités nommées (NER) : Si pertinent pour votre cas, NER peut être utile pour extraire les informations importantes.'''

import PyPDF2
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import spacy
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher
from spacy.language import Language


nlp = spacy.load("fr_core_news_sm")
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

es = Elasticsearch(["http://localhost:9200"], timeout=60)


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return ADJ
    elif tag.startswith('V'):
        return VERB
    elif tag.startswith('N'):
        return NOUN
    elif tag.startswith('R'):
        return ADV
    else:
        return NOUN

liste_entreprise=['orange','bouygues telecom','alten','capgemeini','sopra steria','bnp paribas' ,'bpce',"société générale","caisse d\'épargne","lcl",'valeo','ESN','banque','université','master','école d\'ingénieurs'
'sfr','free','société','sncf','ratp','auchan','carrefour','intermarché','grande distribution','esn','open classrooms']

liste_mots_cle = [
    'Python', 'Java','RESTAPI' ,'JavaScript', 'langage C', 'C++','c++', 'C#', 'Ruby', 'PHP', 'Swift', 'Objective-C', 
    'Kotlin', 'Go', 'Rust', 'Perl', 'Scala', 'Haskell', 'langage R', 'MATLAB', 'SQL', 'TypeScript', 
    'Shell','Hibernate' ,'Dart', 'Lua','Visual Code Studio','VS code' ,'Visual Basic', 'Fortran', 'COBOL', 'React', 'Angular', 'VueJs', 
    'Django', 'Flask', 'Spring', 'Laravel', 'Ruby on Rails', 'Express', '.NET', 'TensorFlow', 
    'PyTorch', 'Keras', 'Scikit-Learn', 'Pandas', 'NumPy', 'Matplotlib', 'Bootstrap', 'jQuery', 
    'Node.js','nodejs','lambda','eks','ec2','ecs','gce','shell', 'ASP.NET', 'SASS', 'LESS', 'Kubernetes', 'Docker', 'Jenkins', 'Ansible', 'Chef', 
    'Puppet', 'Terraform', 'Nagios', 'Prometheus', 'Grafana', 'Git', 'GitHub', 'GitLab', 
    'Bitbucket', 'CircleCI', 'Travis CI', 'MySQL', 'PostgreSQL', 'SQLite', 'MongoDB', 
    'Cassandra', 'Redis', 'MariaDB', 'Oracle', 'SQL Server', 'DB2', 'Elasticsearch', 'Firebase', 
    'CouchDB', 'DynamoDB', 'Hadoop', 'Spark', 'Kafka', 'Flink', 'Hive', 'HBase', 'Storm', 
    'Pig', 'Sqoop', 'SSL/TLS', 'VPN', 'Firewall', 'IDS/IPS', 'Penetration Testing', 'OWASP', 
    'SIEM', 'DLP', 'MFA', 'Zero Trust', 'IAM', 'SSO', 'Linux', 'Ubuntu', 'CentOS', 'Fedora', 
    'Debian', 'Red Hat', 'Windows', 'macOS', 'Android', 'iOS', 'CISSP', 'CEH', 'CompTIA Security+', 
    'AWS Certified Solutions Architect', 'Google Cloud Professional', 'Microsoft Certified Azure Solutions Architect', 
    'PMP','azure','css' ,'Scrum Master', 'ITIL', 'CCNA', 'CCNP', 'RHCE', 'SEO', 'SEM', 'PPC', 'Content Marketing', 
    'Social Media Marketing', 'Email Marketing', 'Influencer Marketing', 'Google Analytics', 
    'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads', 'Google', 'Amazon', 'Microsoft', 'Apple', 
    'Facebook', 'IBM', 'Oracle', 'SAP', 'Salesforce', 'Uber', 'Airbnb', 'Netflix', 'Tesla', 'SpaceX', 
    'Bouygues', 'Cisco', 'Dell', 'HP', 'Intel', 'AMD', 'Nvidia', 'Samsung', 'Sony',
    'Bash', 'PowerShell', 'Zsh', 'Ksh', 'Tcsh', 'Fish', 'Elixir', 'Erlang', 'Julia', 'Solidity',
    'Chef de projet', 'Architecte', 'Testeur','ARM','arm cortex','stm32' ,'Analyste', 'Développeur', 'Ingénieur', 'Administrateur',
    'Consultant', 'Sysadmin', 'DevOps', 'Technicien', 'Technologie', 'Big Data', 'Data Scientist',
    'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Blockchain', 'Cryptocurrency',
    'Cybersecurity', 'Sécurité', 'Réseau', 'Informatique', 'Programmation', 'Codage', 'Développement',
    'Frontend', 'Backend', 'Fullstack', 'UI/UX', 'Web', 'Mobile', 'Cloud', 'IAAS', 'PAAS', 'SAAS',
    'Microservices', 'Containers', 'Orchestration', 'CICD', 'Infrastructure', 'Automation', 'Scripts',
    'API', 'SDK', 'IDE', 'Versioning', 'Continuous Integration', 'Continuous Deployment', 'Testing','cicd','ci cd'
    'QA', 'Quality Assurance', 'Performance', 'Scalability', 'Reliability', 'Availability', 'Disaster Recovery',
    'Backup', 'Compliance', 'GDPR', 'Data Protection', 'Privacy', 'Ethics', 'Hacking', 'Penetration Testing',
    'Incident Response', 'Threat Hunting', 'Vulnerability Management', 'Patch Management', 'Risk Assessment',
    'Network Security', 'Endpoint Security', 'Application Security', 'Cloud Security', 'Security Operations',
    'Forensics', 'Encryption', 'Decryption', 'Key Management', 'Public Key Infrastructure', 'Access Control','thales','devops','software',
    'Identity Management', 'Single Sign-On', 'Multi-Factor Authentication', 'Security Information and Event Management',
    'Security Operations Center', 'Firewalls', 'Intrusion Detection', 'Intrusion Prevention', 'Antivirus',
    'Malware', 'Spyware', 'Adware', 'Ransomware', 'Phishing', 'Social Engineering', 'Zero-Day', 'Zero Trust',
    'Red Team', 'Blue Team', 'Purple Team', 'Security Awareness', 'Training', 'Education', 'Certification',
    'Diplôme', 'Université', 'Master', 'Bachelor', 'Licence', 'Doctorat', 'PhD', 'Professor', 'Research',
    'Thesis', 'Dissertation', 'Academic', 'Study', 'Publication', 'Conference', 'Workshop', 'Seminar',
    'Lecture', 'Course', 'Curriculum', 'Training Program', 'Bootcamp', 'Online Course', 'MOOC',
    'Udemy', 'Coursera', 'edX', 'Khan Academy', 'LinkedIn Learning', 'Pluralsight', 'Codecademy',
    'FreeCodeCamp', 'DataCamp', 'Treehouse', 'Skillshare', 'Google Certifications', 'AWS Certifications',
    'Microsoft Certifications', 'Cisco Certifications', 'Oracle Certifications', 'CompTIA Certifications',
    'Certified Ethical Hacker', 'Certified Information Systems Security Professional', 'Certified Information Security Manager',
    'Certified Information Systems Auditor', 'Certified in Risk and Information Systems Control',
    'Certified Cloud Security Professional', 'Certified Data Privacy Solutions Engineer', 'Certified Information Privacy Professional',
    'Certified Information Privacy Manager', 'Certified Information Privacy Technologist', 'Certified Blockchain Professional',
    'Certified Artificial Intelligence Practitioner', 'Certified Data Scientist', 'Certified Data Engineer',
    'Certified Business Intelligence Professional', 'Certified ScrumMaster', 'Professional Scrum Master',
    'Agile Certified Practitioner', 'Lean Six Sigma', 'Project Management Professional', 'Certified Associate in Project Management',
    'Certified Scrum Product Owner', 'Certified Agile Leadership', 'Agile Project Management', 'Scaled Agile Framework',
    'Kanban', 'Extreme Programming', 'Feature-Driven Development', 'Crystal', 'Dynamic Systems Development Method',
    'Test-Driven Development', 'Behavior-Driven Development', 'Acceptance Test-Driven Development',
    'Domain-Driven Design', 'Event-Driven Architecture', 'Microservices Architecture', 'Service-Oriented Architecture',
    'Monolithic Architecture', 'Serverless Architecture', 'Cloud-Native Architecture', 'Edge Computing',
    'Fog Computing', 'Internet of Things', 'Industrial Internet of Things', 'Smart Cities', 'Smart Grid',
    'Smart Home', 'Smart Health', 'Smart Manufacturing', 'Smart Agriculture', 'Smart Transportation',
    'Autonomous Vehicles', 'Connected Devices', 'Wearables', 'Augmented Reality', 'Virtual Reality',
    'Mixed Reality', 'Extended Reality', 'Computer Vision', 'Natural Language Processing', 'Speech Recognition',
    'Robotics', 'Automation', 'Industrial Automation', 'Process Automation', 'Robotic Process Automation',
    'Digital Transformation', 'Digital Twin', 'Industry 4.0', 'Supply Chain', 'Logistics', 'Procurement',
    'Manufacturing', 'Production', 'Quality Control', 'Maintenance', 'Asset Management', 'Facilities Management',
    'Building Management', 'Energy Management', 'Water Management', 'Waste Management', 'Environmental Management',
    'Sustainability', 'Green Technology', 'Renewable Energy', 'Solar Power', 'Wind Power', 'Hydropower',
    'Geothermal Energy', 'Biomass', 'Biofuels', 'Hydrogen', 'Energy Storage', 'Battery Technology',
    'Electric Vehicles', 'Charging Infrastructure', 'Smart Grid', 'Distributed Energy Resources', 'Demand Response',
    'Energy Efficiency', 'Carbon Footprint', 'Carbon Neutral', 'Net Zero', 'Circular Economy', 'Climate Change',
    'Environmental Impact', 'Life Cycle Assessment', 'Environmental Reporting', 'Corporate Social Responsibility',
    'Sustainable Development Goals', 'United Nations', 'Global Reporting Initiative', 'ISO Standards',
    'Environmental Management System', 'Energy Management System', 'Occupational Health and Safety',
    'Health and Safety Management System', 'Quality Management System', 'Risk Management System',
    'Business Continuity', 'Crisis Management', 'Emergency Management', 'Disaster Recovery Plan',
    'Incident Management', 'Problem Management', 'Change Management', 'Configuration Management',
    'Release Management', 'Service Level Management', 'Capacity Management', 'Availability Management',
    'Financial Management', 'IT Service Management', 'IT Infrastructure Library', 'Enterprise Architecture',
    'Business Architecture', 'Information Architecture', 'Technology Architecture', 'Security Architecture',
    'Solution Architecture', 'Application Architecture', 'Data Architecture', 'Cloud Architecture',
    'Infrastructure Architecture', 'Integration Architecture', 'DevOps Architecture', 'AI Architecture',
    'Blockchain Architecture', 'IoT Architecture', 'Microservices Architecture', 'Serverless Architecture',
    'Edge Computing Architecture', 'Digital Twin Architecture', 'Smart Cities Architecture', 'Industry 4.0 Architecture',
    '5G', 'Network', 'Network Architecture', 'Network Design', 'Network Implementation', 'Network Management',
    'Network Monitoring', 'Network Security', 'Network Performance', 'Network Optimization', 'Network Troubleshooting',
    'LAN', 'WAN', 'MAN', 'PAN', 'SAN', 'VLAN', 'VPN', 'MPLS', 'SD-WAN', 'Wi-Fi', 'Wireless', 'Mobile Network',
    'Cellular Network', 'Satellite Network', 'Fiber Optic Network', 'Ethernet', 'IP', 'TCP/IP', 'IPv4', 'IPv6',
    'DNS', 'DHCP', 'NAT', 'Routing', 'Switching', 'Firewall', 'Proxy', 'Load Balancer', 'Content Delivery Network',
    'Network Address Translation', 'Access Control List', 'Network Security Group', 'Virtual Private Network',
    'Network Management System', 'Network Monitoring System', 'Network Operations Center', 'Service Provider',
    'Internet Service Provider', 'Telecommunications', 'Broadband', 'Voice over IP', 'Video Conferencing',
    'Unified Communications', 'Collaboration Tools', 'Remote Work', 'Telecommuting', 'Digital Workplace',
    'Office 365', 'Google Workspace', 'Slack', 'Microsoft Teams', 'Zoom', 'WebEx', 'GoToMeeting', 'Trello',
    'Asana', 'Basecamp', 'Jira', 'Confluence', 'Miro', 'Notion', 'ClickUp', 'Monday.com', 'Smartsheet',
    'Wrike', 'Airtable', 'Zapier', 'IFTTT', 'Automation Tools', 'Task Management', 'Project Management',
    'Product Management', 'Agile Management', 'Kanban Board', 'Scrum Board', 'Gantt Chart', 'Timeline',
    'Roadmap', 'Milestones', 'Deliverables', 'Dependencies', 'Risk Management', 'Issue Tracking',
    'Bug Tracking', 'Feature Tracking', 'Time Tracking', 'Resource Management', 'Capacity Planning',
    'Workload Management', 'Team Collaboration', 'Communication Tools', 'Chat Tools', 'Video Tools',
    'Screen Sharing', 'File Sharing', 'Document Collaboration', 'Knowledge Management', 'Learning Management',
    'Performance Management', 'Employee Engagement', 'Employee Experience', 'Human Resources',
    'Recruitment', 'Onboarding', 'Training and Development', 'Payroll', 'Compensation', 'Benefits',
    'Employee Relations', 'Labor Relations', 'Compliance', 'Workplace Safety', 'Diversity and Inclusion',
    'Culture and Values', 'Employee Wellbeing', 'Remote Work', 'Flexible Work', 'Hybrid Work',
    'Work-Life Balance', 'Employee Recognition', 'Employee Feedback', 'Employee Surveys', 'Exit Interviews',
    'Employee Retention', 'Talent Management', 'Succession Planning', 'Leadership Development',
    'Organizational Development', 'Change Management', 'Performance Improvement', 'Process Improvement',
    'Continuous Improvement', 'Lean', 'Six Sigma', 'Kaizen', 'Business Process Management', 'Workflow Automation',
    'Robotic Process Automation', 'Digital Transformation', 'Innovation Management', 'Idea Management',
    'Knowledge Management', 'Information Management', 'Document Management', 'Content Management',
    'Records Management', 'Data Management', 'Master Data Management', 'Metadata Management', 'Data Governance',
    'Data Quality', 'Data Integration', 'Data Migration', 'Data Warehousing', 'Data Lake', 'Big Data',
    'Data Analytics', 'Business Intelligence', 'Reporting', 'Dashboard', 'Data Visualization', 'Data Mining',
    'Machine Learning', 'Artificial Intelligence', 'Predictive Analytics', 'Prescriptive Analytics',
    'Cognitive Computing', 'Natural Language Processing', 'Computer Vision', 'Speech Recognition',
    'Chatbot', 'Virtual Assistant', 'Robotic Process Automation', 'Automation', 'Digital Workforce',
    'Smart Automation', 'Intelligent Automation', 'Autonomous Systems', 'Smart Systems', 'Cyber-Physical Systems',
    'Internet of Things', 'Industrial Internet of Things', 'Smart Cities', 'Smart Grid', 'Smart Home',
    'Smart Health', 'Smart Manufacturing', 'Smart Agriculture', 'Smart Transportation', 'Autonomous Vehicles',
    'Connected Devices', 'Wearables', 'Augmented Reality', 'Virtual Reality', 'Mixed Reality', 'Extended Reality',
    '3D Printing', 'Additive Manufacturing', 'Advanced Manufacturing', 'Industry 4.0', 'Digital Twin',
    'Digital Thread', 'Supply Chain', 'Logistics', 'Procurement', 'Manufacturing', 'Production', 'Quality Control',
    'Maintenance', 'Asset Management', 'Facilities Management', 'Building Management', 'Energy Management',
    'Water Management', 'Waste Management', 'Environmental Management', 'Sustainability', 'Green Technology',
    'Renewable Energy', 'Solar Power', 'Wind Power', 'Hydropower', 'Geothermal Energy', 'Biomass', 'Biofuels',
    'Hydrogen', 'Energy Storage', 'Battery Technology', 'Electric Vehicles', 'Charging Infrastructure',
    'Smart Grid', 'Distributed Energy Resources', 'Demand Response', 'Energy Efficiency', 'Carbon Footprint',
    'Carbon Neutral', 'Net Zero', 'Circular Economy', 'Climate Change', 'Environmental Impact', 'Life Cycle Assessment',
    'Environmental Reporting', 'Corporate Social Responsibility', 'Sustainable Development Goals', 'United Nations',
    'Global Reporting Initiative', 'ISO Standards', 'Environmental Management System', 'Energy Management System',
    'Occupational Health and Safety', 'Health and Safety Management System', 'Quality Management System',
    'Risk Management System', 'Business Continuity', 'Crisis Management', 'Emergency Management', 'Disaster Recovery Plan',
    'Incident Management', 'Problem Management', 'Change Management', 'Configuration Management', 'Release Management',
    'Service Level Management', 'Capacity Management', 'Availability Management', 'Financial Management',
    'IT Service Management', 'IT Infrastructure Library', 'Enterprise Architecture', 'Business Architecture',
    'Information Architecture', 'Technology Architecture', 'Security Architecture', 'Solution Architecture',
    'Application Architecture', 'Data Architecture', 'Cloud Architecture', 'Infrastructure Architecture',
    'Integration Architecture', 'DevOps Architecture', 'AI Architecture', 'Blockchain Architecture', 'IoT Architecture',
    'Microservices Architecture', 'Serverless Architecture', 'Edge Computing Architecture', 'Digital Twin Architecture',
    'Smart Cities Architecture', 'Industry 4.0 Architecture', '5G', 'Network', 'Network Architecture', 'Network Design',
    'Network Implementation', 'Network Management', 'Network Monitoring', 'Network Security', 'Network Performance',
    'Network Optimization', 'Network Troubleshooting', 'LAN', 'WAN', 'MAN', 'PAN', 'SAN', 'VLAN', 'VPN', 'MPLS',
    'SD-WAN', 'Wi-Fi', 'Wireless', 'Mobile Network', 'Cellular Network', 'Satellite Network', 'Fiber Optic Network',
    'Ethernet', 'IP', 'TCP/IP', 'IPv4', 'IPv6', 'DNS', 'DHCP', 'NAT', 'Routing', 'Switching', 'Firewall', 'Proxy',
    'Load Balancer', 'Content Delivery Network', 'Network Address Translation', 'Access Control List', 'Network Security Group',
    'Virtual Private Network', 'Network Management System', 'Network Monitoring System', 'Network Operations Center',
    'Service Provider', 'Internet Service Provider', 'Telecommunications', 'Broadband', 'Voice over IP', 'Video Conferencing',
    'Unified Communications', 'Collaboration Tools', 'Remote Work', 'Telecommuting', 'Digital Workplace', 'Office 365',
    'Google Workspace', 'Slack', 'Microsoft Teams', 'Zoom', 'WebEx', 'GoToMeeting', 'Trello', 'Asana', 'Basecamp', 'Jira',
    'Confluence', 'Miro', 'Notion', 'ClickUp', 'Monday.com', 'Smartsheet', 'Wrike', 'Airtable', 'Zapier', 'IFTTT',
    'Automation Tools', 'Task Management', 'Project Management', 'Product Management', 'Agile Management', 'Kanban Board',
    'Scrum Board', 'Gantt Chart', 'Timeline', 'Roadmap', 'Milestones', 'Deliverables', 'Dependencies', 'Risk Management',
    'Issue Tracking', 'Bug Tracking', 'Feature Tracking', 'Time Tracking', 'Resource Management', 'Capacity Planning',
    'Workload Management', 'Team Collaboration', 'Communication Tools', 'Chat Tools', 'Video Tools', 'Screen Sharing',
    'File Sharing', 'Document Collaboration', 'Knowledge Management', 'Learning Management', 'Performance Management',
    'Employee Engagement', 'Employee Experience', 'Human Resources', 'Recruitment', 'Onboarding', 'Training and Development',
    'Payroll', 'Compensation', 'Benefits', 'Employee Relations', 'Labor Relations', 'Compliance', 'Workplace Safety',
    'Diversity and Inclusion', 'Culture and Values', 'Employee Wellbeing', 'Remote Work', 'Flexible Work', 'Hybrid Work',
    'Work-Life Balance', 'Employee Recognition', 'Employee Feedback', 'Employee Surveys', 'Exit Interviews', 'Employee Retention',
    'Talent Management', 'Succession Planning', 'Leadership Development', 'Organizational Development', 'Change Management',
    'Performance Improvement', 'Process Improvement', 'Continuous Improvement', 'Lean', 'Six Sigma', 'Kaizen',
    'Business Process Management', 'Workflow Automation', 'Robotic Process Automation', 'Digital Transformation',
    'Innovation Management', 'Idea Management', 'Knowledge Management', 'Information Management', 'Document Management',
    'Content Management', 'Records Management', 'Data Management', 'Master Data Management', 'Metadata Management',
    'Data Governance', 'Data Quality', 'Data Integration', 'Data Migration', 'Data Warehousing', 'Data Lake', 'Big Data',
    'Data Analytics', 'Business Intelligence', 'Reporting', 'Dashboard', 'Data Visualization', 'Data Mining', 'Machine Learning',
    'Artificial Intelligence', 'Predictive Analytics', 'Prescriptive Analytics', 'Cognitive Computing', 'Natural Language Processing',
    'Computer Vision', 'Speech Recognition', 'Chatbot', 'Virtual Assistant', 'Robotic Process Automation', 'Automation',
    'Digital Workforce', 'Smart Automation', 'Intelligent Automation', 'Autonomous Systems', 'Smart Systems',
    'Cyber-Physical Systems', 'Internet of Things', 'Industrial Internet of Things', 'Smart Cities', 'Smart Grid', 'Smart Home',
    'Smart Health', 'Smart Manufacturing', 'Smart Agriculture', 'Smart Transportation', 'Autonomous Vehicles', 'Connected Devices',
    'Wearables', 'Augmented Reality', 'Virtual Reality', 'Mixed Reality', 'Extended Reality', '3D Printing', 'Additive Manufacturing',
    'Advanced Manufacturing', 'Industry 4.0', 'Digital Twin', 'Digital Thread', 'Supply Chain', 'Logistics', 'Procurement',
    'Manufacturing', 'Production', 'Quality Control', 'Maintenance', 'Asset Management', 'Facilities Management', 'Building Management',
    'Energy Management', 'Water Management', 'Waste Management', 'Environmental Management', 'Sustainability', 'Green Technology',
    'Renewable Energy', 'Solar Power', 'Wind Power', 'Hydropower', 'Geothermal Energy', 'Biomass', 'Biofuels', 'Hydrogen', 'Energy Storage',
    'Battery Technology', 'Electric Vehicles', 'Charging Infrastructure', 'Smart Grid', 'Distributed Energy Resources', 'Demand Response',
    'Energy Efficiency', 'Carbon Footprint', 'Carbon Neutral', 'Net Zero', 'Circular Economy', 'Climate Change', 'Environmental Impact',
    'Life Cycle Assessment', 'Environmental Reporting', 'Corporate Social Responsibility', 'Sustainable Development Goals', 'United Nations',
    'Global Reporting Initiative', 'ISO Standards', 'Environmental Management System', 'Energy Management System', 'Occupational Health and Safety',
    'Health and Safety Management System', 'Quality Management System', 'Risk Management System', 'Business Continuity', 'Crisis Management',
    'Emergency Management', 'Disaster Recovery Plan', 'Incident Management', 'Problem Management', 'Change Management', 'Configuration Management',
    'Release Management', 'Service Level Management', 'Capacity Management', 'Availability Management', 'Financial Management', 'IT Service Management',
    'IT Infrastructure Library', 'Enterprise Architecture', 'Business Architecture', 'Information Architecture', 'Technology Architecture',
    'Security Architecture', 'Solution Architecture', 'Application Architecture', 'Data Architecture', 'Cloud Architecture', 'Infrastructure Architecture',
    'Integration Architecture', 'DevOps Architecture', 'AI Architecture', 'Blockchain Architecture', 'IoT Architecture', 'Microservices Architecture',
    'Serverless Architecture', 'Edge Computing Architecture', 'Digital Twin Architecture', 'Smart Cities Architecture', 'Industry 4.0 Architecture',
    '5G', 'Network', 'Network Architecture', 'Network Design', 'Network Implementation', 'Network Management', 'Network Monitoring',
    'Network Security', 'Network Performance', 'Network Optimization', 'Network Troubleshooting', 'LAN', 'WAN', 'MAN', 'PAN', 'SAN', 'VLAN', 'VPN', 'MPLS',
    'SD-WAN', 'Wi-Fi', 'Wireless', 'Mobile Network', 'Cellular Network', 'Satellite Network', 'Fiber Optic Network', 'Ethernet', 'IP', 'TCP/IP', 'IPv4', 'IPv6',
    'DNS', 'DHCP', 'NAT', 'Routing', 'Switching', 'Firewall', 'Proxy', 'Load Balancer', 'Content Delivery Network', 'Network Address Translation',
    'Access Control List', 'Network Security Group', 'Virtual Private Network', 'Network Management System', 'Network Monitoring System',
    'Network Operations Center', 'Service Provider', 'Internet Service Provider', 'Telecommunications', 'Broadband', 'Voice over IP', 'Video Conferencing',
    'Unified Communications', 'Collaboration Tools', 'Remote Work', 'Telecommuting', 'Digital Workplace', 'Office 365', 'Google Workspace', 'Slack',
    'Microsoft Teams', 'Zoom', 'WebEx', 'GoToMeeting', 'Trello', 'Asana', 'Basecamp', 'Jira', 'Confluence', 'Miro', 'Notion', 'ClickUp', 'Monday.com',
    'Smartsheet', 'Wrike', 'Airtable', 'Zapier', 'IFTTT', 'Automation Tools', 'Task Management', 'Project Management', 'Product Management', 'Agile Management',
    'Kanban Board', 'Scrum Board', 'Gantt Chart', 'Timeline', 'Roadmap', 'Milestones', 'Deliverables', 'Dependencies', 'Risk Management', 'Issue Tracking',
    'Bug Tracking', 'Feature Tracking', 'Time Tracking', 'Resource Management', 'Capacity Planning', 'Workload Management', 'Team Collaboration',
    'Communication Tools', 'Chat Tools', 'Video Tools', 'Screen Sharing', 'File Sharing', 'Document Collaboration', 'Knowledge Management', 'Learning Management',
    'Performance Management', 'Employee Engagement', 'Employee Experience', 'Human Resources', 'Recruitment', 'Onboarding', 'Training and Development', 'Payroll',
    'Compensation', 'Benefits', 'Employee Relations', 'Labor Relations', 'Compliance', 'Workplace Safety', 'Diversity and Inclusion', 'Culture and Values',
    'Employee Wellbeing', 'Remote Work', 'Flexible Work', 'Hybrid Work', 'Work-Life Balance', 'Employee Recognition', 'Employee Feedback', 'Employee Surveys',
    'Exit Interviews', 'Employee Retention', 'Talent Management', 'Succession Planning', 'Leadership Development', 'Organizational Development', 'Change Management',
    'Performance Improvement', 'Process Improvement', 'Continuous Improvement', 'Lean', 'Six Sigma', 'Kaizen', 'Business Process Management', 'Workflow Automation',
    'Robotic Process Automation', 'Digital Transformation', 'Innovation Management', 'Idea Management', 'Knowledge Management', 'Information Management', 'Document Management',
    'Content Management', 'Records Management', 'Data Management', 'Master Data Management', 'Metadata Management', 'Data Governance', 'Data Quality', 'Data Integration',
    'Data Migration', 'Data Warehousing', 'Data Lake', 'Big Data', 'Data Analytics', 'Business Intelligence', 'Reporting', 'Dashboard', 'Data Visualization', 'Data Mining',
    'Machine Learning', 'Artificial Intelligence', 'Predictive Analytics', 'Prescriptive Analytics', 'Cognitive Computing', 'Natural Language Processing', 'Computer Vision',
    'Speech Recognition', 'Chatbot', 'Virtual Assistant', 'Robotic Process Automation', 'Automation', 'Digital Workforce', 'Smart Automation', 'Intelligent Automation',
    'Autonomous Systems', 'Smart Systems', 'Cyber-Physical Systems', 'Internet of Things', 'Industrial Internet of Things', 'Smart Cities', 'Smart Grid', 'Smart Home',
    'Smart Health', 'Smart Manufacturing', 'Smart Agriculture', 'Smart Transportation', 'Autonomous Vehicles', 'Connected Devices', 'Wearables', 'Augmented Reality',
    'Virtual Reality', 'Mixed Reality', 'Extended Reality', '3D Printing', 'Additive Manufacturing', 'Advanced Manufacturing', 'Industry 4.0', 'Digital Twin', 'Digital Thread',
    'Supply Chain', 'Logistics', 'Procurement', 'Manufacturing', 'Production', 'Quality Control', 'Maintenance', 'Asset Management', 'Facilities Management', 'Building Management',
    'Energy Management', 'Water Management', 'Waste Management', 'Environmental Management', 'Sustainability', 'Green Technology', 'Renewable Energy', 'Solar Power', 'Wind Power',
    'Hydropower', 'Geothermal Energy', 'Biomass', 'Biofuels', 'Hydrogen', 'Energy Storage', 'Battery Technology', 'Electric Vehicles', 'Charging Infrastructure', 'Smart Grid',
    'Distributed Energy Resources', 'Demand Response', 'Energy Efficiency', 'Carbon Footprint', 'Carbon Neutral', 'Net Zero', 'Circular Economy', 'Climate Change', 'Environmental Impact',
    'Life Cycle Assessment', 'Environmental Reporting', 'Corporate Social Responsibility', 'Sustainable Development Goals', 'United Nations', 'Global Reporting Initiative', 'ISO Standards',
    'Environmental Management System', 'Energy Management System', 'Occupational Health and Safety', 'Health and Safety Management System', 'Quality Management System', 'Risk','développeur','fullstack','sap','rgpd','dba','administrateur base de données','Audits', 'Achats', 'Helpdesk', 'Système', 'Sécurité', 'Telecom', 'Processus', 'PRA', 'Budgets',
    'opex', 'capex' ,'Architecture ', 'Cloud' ,'privé' ,'Vmware' ,'Google' ,'AS400','Citrix' ,'AWS',
    'Responsable des Services Généraux siège' ,'Immobilier', 'Amélioration continue',
    'animations sécurité', 'ISO', 'HSE', 'space planning', 'Budgets',
    'pilotage', 'fournisseurs','moa','moe','quality assurance','test','testeur','test unitaire','conteneurisation','intelligence artificielle','data science','wordpress','erp','crm','coach agile','scrum master','devops','c ++','c #', 'android studio'
    'junior','senior','datacenter','climatisation','allemand','espagnol','français','anglais','toeic','certifications','communication','telecom','télécommunication'
    ,'paris','lyon','marseille','arabe','carrefour','ingénieur système','ingénieur réseau','ingénieur système réseau','italien','infrastructure IT','infrastructure','pytest','data engineering'
    ,'pytest','data engineering','5 ans d\'expérience','6 ans d\'expérience','7 ans d\'expérience','8 ans d\'expérience','9 ans d\'expérience','10 ans d\'expérience','12 ans d\'expérience','3 ans d\'expérience','secteur bancaire'
    ,'(Gerrit/GitLab)','gitlab','gerrit', 'SVN', 'SonarQube', 'Nexus','italien','Windows Server','Openstack' , 'datacenters' , 'ingénieries' ,'monitoring','virtualisation','HA-Proxy','cybersécurité','Graphite','Icinga 2','autonome','force de proposition','challenge'
    ,'mise en confirmité','rigoureux','fortinet','scripting','bash','gitbash','paas','saas','master 2' , 'bac +5','data','sonar','gitconnaissance','nomes','signal','audio','tcp','ip','cross-plateform','agile','scrum'
    ,'intelligence embarquée','pssi'] 

### prétraitement du CV en format pdf parsé 

def preprocess_text_cv(text):
    # mots clé qu'on retrouve lors du traitement de text des cvs ce qui est très utile lors du processus du finetuning 
    non_modifiable_words=liste_mots_cle
    non_modifiable_mots=set(non_modifiable_words)
    text = text.lower()
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'\b\d{10,13}\b', '', text)
    text = re.sub(r'page \d+ of \d+', '', text)
    text = re.sub(r'page \d+ de \d+', '', text)
    text = re.sub(r'page \d+ sur \d+', '', text)
    text = re.sub(r'\b\d{4}\b', '', text)

    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    month_pattern = re.compile(r'\b(' + '|'.join(months) + r')\b', re.IGNORECASE)
    text = month_pattern.sub('', text)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d+', '', text)
    
    words = nltk.word_tokenize(text)
    
    # Retirer les mots non modifiables de la liste des transformations
    modifiable_words = [word for word in words if word not in non_modifiable_mots]

    #traiter les mots-clé modifiables 
    pos_tags = nltk.pos_tag(modifiable_words)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in pos_tags]
    lemmatized_text = ' '.join(lemmatized_words)
    
    sensitive_words = ['marié', 'mariée', 'enfant', 'enfants', 'âge', 'ans', 'nom', 'prénom', 'adresse', 'téléphone', 'tél', 'portable', 'mobile', 'email', 'page', 'coordonnées', 'autres', 'plus', 'autre', 'maintenant', 'aujourd\'hui', 'but', 'd\'usage', 'depuis', 'ainsi', 'aussi', 'donc', 'alors', 'comme', 'leur', 'moins', 'mes', 'ton', 'ta', 'tes', 'ma', 'mon', 'ses', 'son', 'sa', 'principal', 'or', 'and', 'principal', 'principaux', 'principal', 'principales', 'nouvelles', 'nouveaux', 'nouvelle', 'nouveau', 'chaque', 'il', 'y a']
    pattern = re.compile(r'\b(' + '|'.join(sensitive_words) + r')\b', re.IGNORECASE)
    lemmatized_text = pattern.sub('', lemmatized_text)

    words = nltk.word_tokenize(lemmatized_text)
    pos_tags = nltk.pos_tag(words)
    words = [word for word, pos in pos_tags if pos not in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'PRP', 'PRP$', 'WP', 'WP$', 'IN', 'MD', 'DT']]
    words = words[3:]
    french_stopwords = set(stopwords.words('french'))
    words = [word for word in words if word not in french_stopwords]

    original_words = nltk.word_tokenize(text)
    words.extend([word for word in original_words if word in non_modifiable_mots])
    
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            words.extend([ent.text])
    text = ' '.join(words)
    return text

def preprocess_text_mission(text):
    # mots clé qu'on retrouve lors du traitement de text des cvs ce qui est très utile lors du processus du finetuning 
    non_modifiable_words = liste_mots_cle
    non_modifiable_mots = set(word.lower() for word in non_modifiable_words)
    text = text.lower()

    # Remove emails, URLs, phone numbers, page numbers, and years
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'\b\d{10,13}\b', '', text)
    text = re.sub(r'page \d+ of \d+', '', text)
    text = re.sub(r'page \d+ de \d+', '', text)
    text = re.sub(r'page \d+ sur \d+', '', text)
    text = re.sub(r'\b\d{4}\b', '', text)

    # Remove months
    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    month_pattern = re.compile(r'\b(' + '|'.join(months) + r')\b', re.IGNORECASE)
    text = month_pattern.sub('', text)

    # Replace / with space
    text = text.replace('/', ' ')

    # Split words with two capital letters
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Remove non-alphanumeric characters and digits
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d+', '', text)
    
    words = nltk.word_tokenize(text)
    
    # Retirer les mots non modifiables de la liste des transformations
    modifiable_words = [word for word in words if word not in non_modifiable_mots]

    # Traiter les mots-clé modifiables 
    pos_tags = nltk.pos_tag(modifiable_words)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in pos_tags]
    lemmatized_text = ' '.join(lemmatized_words)
    
    sensitive_words = ['marié', 'mariée', 'enfant', 'enfants', 'âge', 'ans', 'nom', 'prénom', 'adresse', 'téléphone', 'tél', 'portable', 'mobile', 'email', 'page', 'coordonnées', 'autres', 'plus', 'autre', 'maintenant', 'aujourd\'hui', 'but', 'd\'usage', 'depuis', 'ainsi', 'aussi', 'donc', 'alors', 'comme', 'leur', 'moins', 'mes', 'ton', 'ta', 'tes', 'ma', 'mon', 'ses', 'son', 'sa', 'principal', 'or', 'and', 'principal', 'principaux', 'principal', 'principales', 'nouvelles', 'nouveaux', 'nouvelle', 'nouveau', 'chaque', 'il', 'y a','sur','en dessus']
    pattern = re.compile(r'\b(' + '|'.join(sensitive_words) + r')\b', re.IGNORECASE)
    lemmatized_text = pattern.sub('', lemmatized_text)

    words = nltk.word_tokenize(lemmatized_text)
    pos_tags = nltk.pos_tag(words)
    words = [word for word, pos in pos_tags if pos not in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'PRP', 'PRP$', 'WP', 'WP$', 'IN', 'MD', 'DT']]
    french_stopwords = set(stopwords.words('french'))
    words = [word for word in words if word not in french_stopwords]

    original_words = nltk.word_tokenize(text)
    words.extend([word for word in original_words if word in non_modifiable_mots])
    
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            words.extend([ent.text])
    
    text = ' '.join(words)
    return text

def create_index(index_name):
    es.indices.create(index=index_name, ignore=400)

def preprocess_text_langue(langue_text):
    langue_text = langue_text.lower()
    words = nltk.word_tokenize(langue_text)
    ponctuation=set(stopwords.words('french'))
    non_modif = set(liste_mots_cle)
    resultat = [word for word in words if word not in ponctuation or word in non_modif]
    texte = ' '.join(resultat)
    return texte

def preprocess_text_entreprises(entreprises_text):
    entreprises_text = entreprises_text.lower()
    words=nltk.word_tokenize(entreprises_text)
    ponctuation=set(stopwords.words('french'))
    non_modif=set(liste_mots_cle)
    resultat=[word for word in words if word not in ponctuation or word in non_modif]
    texte=' '.join(resultat)
    return texte

def preprocess_text_competences(competences_text):
    competences_text = competences_text.lower()
    words=nltk.word_tokenize(competences_text)
    ponctuation=set(stopwords.words('french') )
    non_modif=set(liste_mots_cle)
    resultat=[word for word in words if word not in ponctuation or word in non_modif]
    texte=' '.join(resultat)
    return texte

def search_matching_cvs(mission_text, langue_text, entreprises_text, competences_text,
                        poids_mission=3, poids_langue=2, poids_entreprises=2, poids_competences=1, top_n=10):
    preprocessed_mission_text = preprocess_text_mission(mission_text)
    preprocessed_langue_text = preprocess_text_langue(langue_text)
    preprocessed_entreprises_text = preprocess_text_entreprises(entreprises_text)
    preprocessed_competences_text = preprocess_text_competences(competences_text)

    
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "content": {
                                "query": preprocessed_mission_text,
                                "boost": poids_mission  # Poids pour le texte de mission
                            }
                        }
                    },
                    {
                        "match": {
                            "content": {
                                "query": preprocessed_langue_text,
                                "boost": poids_langue  # Poids pour les langues
                            }
                        }
                    },
                    {
                        "match": {
                            "content": {
                                "query": preprocessed_entreprises_text,
                                "boost": poids_entreprises  # Poids pour les entreprises précédentes
                            }
                        }
                    },
                    {
                        "match": {
                            "content": {
                                "query": preprocessed_competences_text,
                                "boost": poids_competences  # Poids pour les compétences
                            }
                        }
                    }
                ]
            }
        }
    }
    
    results = es.search(index="cvs", body=query, size=top_n)
    return results['hits']['hits']

def display_matching_cvs(results):
    for i, result in enumerate(results):
        score = result['_score']
        filename = result['_source']['filename']
        content = result['_source']['content']
        print(f"Result {i + 1}:\nScore: {score}\nFilename: {filename}\nContent:\n{content}\n{'-' * 50}")


def preprocess_text_lead(langue_text,liste_mots_cle):
    langue_text = langue_text.lower()
    words = nltk.word_tokenize(langue_text)
    ponctuation=set(stopwords.words('french'))
    non_modif = set(liste_mots_cle)
    resultat = list(set([word for word in words if word in non_modif]))
    texte = ' '.join(resultat)
    return resultat
############################"

from sklearn.feature_extraction.text import CountVectorizer

nlp = spacy.load('fr_core_news_sm')
def nettoyage_texte(text):
    text = text.replace('\\', ' ')
    text = text.replace('/', '')
    text = text.replace('(', '')
    text = text.replace(')', '')
    # Séparer les mots composés de minuscules suivies de majuscules (ex : cybersécuritéEngineering -> cybersécurité Engineering)
    text = re.sub(r'([a-zéèêàùîï])([A-ZÉÈÊÀÙÎÏ])', r'\1 \2', text)
    return text

    return text
def get_bigrams(text):
    words = text.split()
    bigrams = [' '.join(bigram) for bigram in zip(words, words[1:])]
    return bigrams

def remove_duplicates(all_keywords_and_phrases):
    unique_elements = set()
    result = []
    
    for element in all_keywords_and_phrases:
        words = set(element.split())
        if not any(word in unique_elements for word in words):
            unique_elements.update(words)
            result.append(element)
    
    return result

def extract_keywords(competences_text):
    competences_text = nettoyage_texte(competences_text)
    # Tokenisation en phrases
    doc = nlp(competences_text)
    sentences = list(doc.sents)
    
    # Convertir la liste des mots-clés non modifiables en minuscules
    non_modif = set(word.lower() for word in liste_mots_cle)
    
    all_keywords_and_phrases = []

    # Extraction des bigrammes et identification des phrases-clés
    for sentence in sentences:
        sentence_text = sentence.text
        bigrams_in_sentence = get_bigrams(sentence_text)
        
        for bigram in bigrams_in_sentence:
            words = bigram.split()
            # Si le bigramme est dans la liste des mots-clés non modifiables, l'ajouter
            if bigram.lower() in non_modif:
                all_keywords_and_phrases.append(bigram)
            else:
                # Sinon, vérifier chaque mot du bigramme
                for word in words:
                    # Séparer les mots composés de minuscules suivies de majuscules
                    separated_words = re.sub(r'([a-zéèêàùîï])([A-ZÉÈÊÀÙÎÏ])', r'\1 \2', word).split()
                    for sep_word in separated_words:
                        if sep_word.lower() in non_modif:
                            all_keywords_and_phrases.append(sep_word)
                            break
    
    liste_finale = list(set(all_keywords_and_phrases))
    
    
    # Convertir la liste des mots-clés et phrases-clés en une chaîne de caractères séparée par des espaces
    result_text = ' , '.join(liste_finale)
    
    print(f'Extracted keywords and key phrases: {all_keywords_and_phrases}')
    print(f'Result Text: {result_text}')
    
    return result_text
### séparer chaque élément de la liste par un espace afin de le convertir en une chaine de caracteres 


def search_matching_cvs_v2(mission_text, keywords_text, poids_lead=3, poids_keywords=2, top_n=10):
    preprocessed_mission_text = preprocess_text_mission(mission_text)
    preprocessed_keywords_text = keywords_text.split()

    should_clauses = [
        {
            "match": {
                "content": {
                    "query": preprocessed_mission_text,
                    "boost": poids_lead  # Poids pour le texte de mission
                }
            }
        }
    ]

    for keyword in preprocessed_keywords_text:
        should_clauses.append({
            "match_phrase": {
                "content": {
                    "query": keyword,
                    "boost": poids_keywords  # Poids pour les mots clés exacts
                }
            }
        })

    query = {
        "query": {
            "bool": {
                "should": should_clauses
            }
        }
    }

    results = es.search(index="cvs", body=query, size=top_n)
    return results['hits']['hits']
##################################################################"


''' 
problèmatique : les mots clés capturés ne sont pas toujours pertinents et peuvent parfois 
induire en erreur le modèle à choisir le meilleur CV 
par exemple C désignant le langage C et dans les occurences des 'C' capturés dans les cv , 
le contexte est dans ce cas différent et fausse par conséquent les résultats 
Solution :
mise en place d'une fonction afin de permettre une analyse approfondie des mots clés récupérés , 
qui réajuste l'algorithme de matching de CV 
l'algorithme de matching CV-lead_description
étape 1 : récupérer les mots clés récupérés lors du matching 
étape 2 : récupérer le contexte des mots clés dans le job description du lead :
par exemple : arm => embarqué et ça se fait via la classification via un fichier csv
Si le mot mentionné dans le job description lead n'est pas pertinent : le mot clé sera ignoré 
par exemple si arm veut dire bras dans le contexte du lead , le mot clé sera supprimé
(piste : utilisation d'algorithmes de clustering pour voir si le mot est pertinent ou non )
étape 3 : récupérer le contexte des mots clés capturés dans chaque CV , et avec le word-vectors embedding , 
chaque occurence du mot trouvée dans chaque CV sera étudiée , et si la classification n'a rien à voir avec 
le contexte du mot dans le lead , l'occurence sera ignorée et ce ne sera pas comptabilisé et ça va 
influer sur le score final : sur 36 occurences du mot ARM , seules 10 représentent : intelligence embarquée 
et donc cette occurence sera ignorée dans l'analyse approfondie 
étape 4 : modifier l'algorithme de matching CV , en jouant sur l'occurence du mot récupéré après , 
et si cette occurence n'a pas de contexte qui match avec le lead récupéré , dans ce cas ce sera ignoré 

et on fait ça avec les mots ayant une longueur < 4 , car j'estime que au delà , le mot est considéré 
comme pertinent 
étape 5 : développer un bouton  de fonctionnalité avancée qui retourne de nouveaux mots clés , un sous 
ensemble E' qui appartient à l'ensemble de base E , telle que E' est inclus ou égal à E (
égal si et seulement si tous les mots clés des leads capturés sont considérés comme pertinents
) , mettre ensuite en place un écran de chargement puis affichage des résultats avec les nouveaux mots clés et un nouveau résultat de matching 
'''


''' récupération des numéros de téléphones et mails'''

