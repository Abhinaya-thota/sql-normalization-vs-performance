import pandas as pd
import sqlite3
import time
import matplotlib.pyplot as plt

def create_schema(conn):
    """Create normalized schema"""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS persons (
        PersonID INTEGER PRIMARY KEY,
        PersonName TEXT,
        BirthDate TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        SchoolID INTEGER PRIMARY KEY,
        SchoolName TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campus (
        SchoolID INTEGER,
        SchoolCampus TEXT,
        PRIMARY KEY (SchoolID, SchoolCampus),
        FOREIGN KEY (SchoolID) REFERENCES schools(SchoolID)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS department (
        DepartmentID INTEGER PRIMARY KEY,
        DepartmentName TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dept_campus (
        DepartmentID INTEGER,
        SchoolID INTEGER,
        SchoolCampus TEXT,
        FOREIGN KEY (DepartmentID) REFERENCES department(DepartmentID),
        FOREIGN KEY (SchoolID, SchoolCampus) REFERENCES campus(SchoolID, SchoolCampus)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employment_records (
        StillWorking INTEGER,
        PersonID INTEGER,
        JobID INTEGER,
        JobTitle TEXT,
        Earnings REAL,
        EarningsYear INTEGER,
        SchoolID INTEGER,
        SchoolCampus TEXT,
        DepartmentID INTEGER,
        FOREIGN KEY (PersonID) REFERENCES persons(PersonID),
        FOREIGN KEY (SchoolID, SchoolCampus) REFERENCES campus(SchoolID, SchoolCampus),
        FOREIGN KEY (DepartmentID) REFERENCES department(DepartmentID)
    )''')
    conn.commit()

def load_and_normalize_data(csv_file, db_name):
    """Load CSV data into staging table and normalize into schema"""
    conn = sqlite3.connect(db_name)
    create_schema(conn)
    
    # Load CSV into DataFrame
    df = pd.read_csv(csv_file)
    
    # Insert data into normalized tables
    df[['PersonID', 'PersonName', 'BirthDate']].drop_duplicates().to_sql('persons', conn, if_exists='replace', index=False)
    df[['SchoolID', 'SchoolName']].drop_duplicates().to_sql('schools', conn, if_exists='replace', index=False)
    df[['SchoolID', 'SchoolCampus']].drop_duplicates().to_sql('campus', conn, if_exists='replace', index=False)
    df[['DepartmentID', 'DepartmentName']].drop_duplicates().to_sql('department', conn, if_exists='replace', index=False)
    df[['DepartmentID', 'SchoolID', 'SchoolCampus']].drop_duplicates().to_sql('dept_campus', conn, if_exists='replace', index=False)
    
    # Create employment_records table
    employment_records = df[['StillWorking', 'PersonID', 'JobID', 'JobTitle', 'Earnings', 'EarningsYear', 'SchoolID', 'SchoolCampus', 'DepartmentID']]
    employment_records.to_sql('employment_records', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Data from {csv_file} has been normalized and stored in {db_name}.")

def execute_queries_from_file(db_name, query_file, output_file):
    """Execute SQL queries from a file on the SQLite database and save the output."""
    conn = sqlite3.connect(db_name)
    
    with open(query_file, 'r') as file:
        queries = file.read().split(';')

    execution_times = []

    with open(output_file, 'a') as output:
        output.write(f"\nResults for {db_name}:\n")
        
        for i, query in enumerate(queries, 1):
            query = query.strip()
            if query:
                output.write(f"\nQuery {i}:\n{query}\n")
                try:
                    start_time = time.perf_counter()  # Use perf_counter for more precise timing
                    result = pd.read_sql_query(query, conn)
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    execution_times.append(execution_time)
                    
                    if result.empty:
                        output.write("No results returned.\n")
                    else:
                        output.write(result.to_string(index=False) + "\n")
                    output.write(f"Execution time: {execution_time:.6f} seconds\n\n")  # Print time after results
                except Exception as e:
                    output.write(f"Error executing query: {str(e)}\n")
                    execution_times.append(None)

    conn.close()
    return execution_times

def graph_execution_times(execution_times_dict):
    """Graph the execution times for each query across different file sizes using a line graph."""
    file_sizes = list(execution_times_dict.keys())
    num_queries = len(execution_times_dict[file_sizes[0]])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for query_num in range(num_queries):
        query_times = [execution_times_dict[size][query_num] for size in file_sizes]
        ax.plot(file_sizes, query_times, marker='o', label=f'Query {query_num + 1}')
    
    ax.set_xlabel('Dataset Size')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Query Execution Times Across Different Dataset Sizes')
    ax.legend(title='Queries', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('results/query_execution_times_normalized.png')
    plt.close()

# File paths and database names
files = [
    ("data/salary_tracker_1MB.csv", "salaries_1MB.db"),
    ("data/salary_tracker_10MB.csv", "salaries_10MB.db"),
    ("data/salary_tracker_100MB.csv", "salaries_100MB.db"),
]

# Load and normalize each file
for csv_file, db_name in files:
    load_and_normalize_data(csv_file, db_name)

# Execute queries and collect execution times
query_file = "queries_normalized.txt"
output_file = "results/query_results_normalized.txt"
execution_times_dict = {}

with open(output_file, 'w') as file:
    file.write("Query Execution Results\n\n")

for csv_file, db_name in files:
    execution_times = execute_queries_from_file(db_name, query_file, output_file)
    file_size = csv_file.split('_')[2].split('.')[0]  # Extract file size (1MB, 10MB, 100MB)
    execution_times_dict[file_size] = execution_times

# Graph the execution times
graph_execution_times(execution_times_dict)

print("Process completed. Check results/query_results_normalized.txt for output and results/query_execution_times_normalized.png for the graph.")