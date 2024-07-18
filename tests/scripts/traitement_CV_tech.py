import pandas as pd
from sqlalchemy import create_engine, text,MetaData, Table, Column, Integer, String

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
DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fbkfdayw_8rdfcrs-telecom',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
db_config1= DATABASE['default']
engine1 = create_engine(f"mysql+mysqldb://{db_config1['USER']}:{db_config1['PASSWORD']}@{db_config1['HOST']}:{db_config1['PORT']}/{db_config1['NAME']}")
# Création du moteur de connexion à la base de données
db_config = DATABASES['default']
engine = create_engine(f"mysql+mysqldb://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}")

df = pd.read_sql_table('users', engine)

new_df = df[['id' ,'login']]

df1 = pd.read_sql_table('users', engine1)

print(df1.shape)
