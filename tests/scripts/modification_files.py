import os
import MySQLdb

# Configuration de la connexion à la base de données MySQL
def get_cv_by_checksum(checksum):
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="",
        db="odoo",
        port=3306
    )

    # Créer un curseur pour exécuter les requêtes SQL
    cursor = db.cursor()

    # Exécuter la requête SQL pour récupérer les données de la table cv en fonction du checksum
    cursor.execute("SELECT id, name, checksum, mimetype FROM facture_nettoye WHERE checksum = %s", (checksum,))

    # Récupérer le résultat de la requête
    cv = cursor.fetchone()

    # Fermer la connexion à la base de données
    db.close()

    # Retourner le résultat
    return cv

# Dictionnaire pour mapper les types MIME aux extensions
mime_to_extension = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'image/png': '.png',
    'image/jpeg': '.jpeg',
    'text/vnd.graphviz': '.gv',
    'application/vnd.oasis.opendocument.text': '.odt',
    'application/zip': '.zip',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx'
}

# Fonction pour ajouter les extensions aux fichiers
def add_extension_to_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Rechercher le CV dans la base de données en fonction du checksum (nom du fichier)
            cv = get_cv_by_checksum(file)
            if cv:
                mime_type = cv[3]

                # Si le type MIME est dans le dictionnaire, ajouter l'extension appropriée
                if mime_type in mime_to_extension:
                    new_file_path = file_path + mime_to_extension[mime_type]

                    # Renommer le fichier
                    os.rename(file_path, new_file_path)
                    print(f"Renamed: {file_path} to {new_file_path}")
                else:
                    print(f"Skipping: {file_path} (MIME type not recognized)")
            else:
                print(f"Skipping: {file_path} (No matching CV found in database)")

# Chemin du répertoire
directory_path = r"C:\Users\Ryan MOKHTARI.DESKTOP-GP4R4DN\Documents\GitHub\new_rs_telecom\test\static\test\CV\filestore"

# Ajouter les extensions appropriées aux fichiers
add_extension_to_files(directory_path)
