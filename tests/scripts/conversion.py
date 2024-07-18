# import re

# # Fonction pour échapper les apostrophes simples dans les valeurs
# def escape_apostrophes(value):
#     if value:
#         return value.replace("'", "''")
#     return value

# # Fonction pour lire et corriger les requêtes SQL
# def read_and_correct_sql(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         sql_commands = file.read()

#     # Corriger les backticks pour les mots réservés comme 'key'
#     corrected_sql = re.sub(r"(\s)key(\s|,)", r" `key` ", sql_commands)

#     # Diviser les requêtes SQL en liste en tenant compte des points-virgules suivis de retours à la ligne
#     sql_list = re.split(r';\s*\n', corrected_sql)
    
#     # Nettoyer les requêtes vides
#     sql_list = [sql.strip() + ';' for sql in sql_list if sql.strip()]

#     # Échapper les apostrophes simples dans chaque commande
#     escaped_sql_list = [escape_apostrophes(sql) for sql in sql_list]

#     return escaped_sql_list

# # Fonction pour écrire les requêtes SQL corrigées dans un nouveau fichier
# def write_corrected_sql(sql_commands, output_file_path):
#     with open(output_file_path, 'w', encoding='utf-8') as file:
#         for command in sql_commands:
#             file.write(command + '\n')

# if __name__ == "__main__":
#     # Spécifiez le chemin vers votre fichier SQL original
#     input_file_path = 'transformed_script.sql'
    
#     # Spécifiez le chemin vers votre fichier SQL corrigé
#     output_file_path = 'corrected_sql_file.sql'

#     # Lire et corriger les requêtes SQL
#     corrected_sql_commands = read_and_correct_sql(input_file_path)

#     # Écrire les requêtes SQL corrigées dans un nouveau fichier
#     write_corrected_sql(corrected_sql_commands, output_file_path)

#     print(f"Les requêtes corrigées ont été écrites dans le fichier {output_file_path}")

import re

def convert_line_to_mysql(line):
    # Split the line by tab
    columns = line.strip().split('\t')
    
    # Escape single quotes and replace '\N' with 'NULL'
    escaped_columns = []
    for column in columns:
        if column == '\\N':
            escaped_columns.append('NULL')
        else:
            # Replace single quotes with \'
            column = column.replace("'", "\\'")
            escaped_columns.append(f"'{column}'")
    
    # Join the columns into a MySQL VALUES string
    values = ", ".join(escaped_columns)
    return values

def convert_postgresql_to_mysql(file_path):
    # Read the file and process each line
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    insert_statements = []
    
    for line in lines:
        if line.strip().startswith('COPY'):
            continue  # Skip the COPY command line
        if line.strip().startswith('\\.'):
            continue  # Skip the end of COPY marker
        if not line.strip():  # Skip empty lines
            continue
        
        # Process each non-empty line
        values = convert_line_to_mysql(line)
        insert_statement = f"INSERT INTO employes (id, name, user_id, active, company_id, address_home_id, country_id, gender, marital, spouse_complete_name, spouse_birthdate, children, place_of_birth, country_of_birth, birthday, ssnid, sinid, identification_id, passport_id, bank_account_id, permit_no, visa_no, visa_expire, additional_note, certificate, study_field, study_school, emergency_contact, emergency_phone, km_home_work, notes, color, barcode, pin, departure_description, departure_date, message_main_attachment_id, department_id, job_id, job_title, address_id, work_phone, mobile_phone, work_email, resource_id, resource_calendar_id, parent_id, coach_id, create_uid, create_date, write_uid, write_date, employee_type, work_location_id, departure_reason_id, work_permit_scheduled_activity, work_permit_expiration_date, vehicle, contract_id, contract_warning, first_contract_date, leave_manager_id, hourly_cost, timesheet_manager_id, work_contact_id, documents_share_id, last_validated_timesheet_date);"
        insert_statements.append(insert_statement)
    
    return insert_statements

def main():
    # Path to your PostgreSQL file
    postgresql_file_path = 'script.sql'
    
    # Convert to MySQL insert statements
    insert_statements = convert_postgresql_to_mysql(postgresql_file_path)
    
    # Output to a MySQL file
    mysql_file_path = 'transformed_script.sql'
    with open(mysql_file_path, 'w', encoding='utf-8') as file:
        for statement in insert_statements:
            file.write(statement + '\n')
    
    print(f"Conversion completed. MySQL statements saved to {mysql_file_path}")

if __name__ == "__main__":
    main()