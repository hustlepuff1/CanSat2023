import csv
import mysql.connector

def export_table_to_csv(hostname, username, password, port, database, table, csv_file):
    try:
        # Connect to the MySQL database
        cnx = mysql.connector.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database=database
        )
        
        # Create a cursor
        cursor = cnx.cursor()
        
        # Execute a SELECT query to fetch all rows from the table
        query = f"SELECT * FROM {table}"
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [column[0] for column in cursor.description]
        
        # Write the data to the CSV file
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the column names as the header row
            writer.writerow(column_names)
            
            # Write the data rows
            writer.writerows(rows)
        
        print(f"Table '{table}' exported to '{csv_file}' successfully.")
        
    except mysql.connector.Error as e:
        print(f"Error occurred while exporting table to CSV: {e}")
        
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Example usage
hostname = "bifrost0602.duckdns.org"
port = 2024
username = "TEST"
password = "1234"
database = "CANSATDB"
table = "SENSOR"
csv_file = "output.csv"

if __name__ =="__main__":
    export_table_to_csv(hostname, username, password, port, database, table, csv_file)