import re
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

def extract_person_name(filename):
    # Retirer tout ce qui suit le premier point dans le fichier
    filename_no_ext = filename.split('.')[0]
    
    # Retirer les parties 'CV' et le code ID avant le nom, ainsi que toutes les occurrences de 'CV'
    filename_no_cv = re.sub(r'^CV\d*_', '', filename_no_ext)
    filename_no_cv = re.sub(r'CV', '', filename_no_cv)
    
    # Remplacer les tirets, underscores, et caractères spéciaux par des espaces
    person_name = re.sub(r'[-_()\[\]{}"\'<>.,]', ' ', filename_no_cv)
    
    # Supprimer les chiffres
    person_name = re.sub(r'\d+', '', person_name)
    
    # Traiter les mots séparés par des majuscules
    person_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', person_name)
    
    # Supprimer les mots courants non pertinents
    non_pertinent_words = ['Resume', 'Profile', 'Summary', 'Turnover', 'Report', 'it', 'GoogleA', 'Docs']
    pattern = re.compile(r'\b(?:' + '|'.join(non_pertinent_words) + r')\b', re.IGNORECASE)
    person_name = pattern.sub('', person_name)
    
    # Supprimer les doubles espaces s'il y en a
    person_name = re.sub(r'\s+', ' ', person_name).strip()
    
    return person_name

def traitement_text(index_content):
    return index_content.lower() if index_content is not None else None 

def get_cv_data(engine):
    # Requête SQL pour récupérer les données
    query = """
    SELECT name, index_content
    FROM cv;
    """
    
    # Exécution de la requête et récupération des résultats dans un DataFrame
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)
    
    return df

def create_nom_propre_table(engine):
    metadata = MetaData()
    nom_propre_table = Table('nom_propre', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('filename', String(255), nullable=False),
        Column('nom_propre', String(255), nullable=False)
    )
    metadata.create_all(engine)

def main():
    # Configuration de la base de données
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'odoo',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    
    db_config = DATABASES['default']
    engine = create_engine(f"mysql+mysqldb://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}")
    
    # Créer la table nom_propre si elle n'existe pas
    create_nom_propre_table(engine)
    
    # Récupérer les données de la base de données
    df = get_cv_data(engine)
    
    # Traiter les données récupérées
    nom_propre_data = []
    for index, row in df.iterrows():
        filename = row['name']
        index_content = row['index_content']
        
        # Extraire le nom de la personne
        person_name = extract_person_name(filename)
        
        # Traiter le texte du CV
        processed_text = traitement_text(index_content)
        
    
        nom_cv = person_name.split()
        if processed_text is None or (len(nom_cv) == 2)  :
            nom_propre_data.append({
                'filename': filename,
                'nom_propre': person_name
            })
            continue
        else:
            processed_text_list = processed_text.split()
            nom_prenom = []
            
            for element in nom_cv:
                if element.lower() in processed_text_list and len(nom_prenom)<=2:
                    nom_prenom.append(element)
            
            # Garder soit les éléments trouvés en correspondance, soit le nom de base
            if nom_prenom:
                final_name = ' '.join(nom_prenom)
            else:
                final_name = person_name
            
            # Ajouter le nom propre à la liste
            nom_propre_data.append({
                'filename': filename,
                'nom_propre': final_name
            })
    
    # Convertir la liste en DataFrame
    nom_propre_df = pd.DataFrame(nom_propre_data)
    
    # Insérer les noms propres dans la table nom_propre
    with engine.connect() as connection:
        nom_propre_df.to_sql('nom_propre', connection, if_exists='append', index=False)

if __name__ == "__main__":
    main()
