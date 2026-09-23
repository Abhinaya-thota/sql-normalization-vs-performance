import sqlite3
import csv
import time
import matplotlib.pyplot as plt

#path to the csv file
csv_files = [
    'data/salary_tracker_1MB.csv',
    'data/salary_tracker_10MB.csv',
    'data/salary_tracker_100MB.csv',
]

# Define the queries to execute
queries_list = [
    f"""SELECT PersonName 
       FROM salary_tracker_table
       WHERE BirthDate < '1975-01-01' 
       AND Earnings > 130000 
       AND EarningsYear = (SELECT MAX(EarningsYear) FROM salary_tracker_table);
       """,
    f"""SELECT PersonName, SchoolName 
       FROM salary_tracker_table 
       WHERE Earnings > 400000
       AND StillWorking = 'no';
       """,
    f"""SELECT DISTINCT PersonName
       FROM salary_tracker_table
       WHERE SchoolName = 'University of Texas'
       AND Jobtitle = 'Lecturer' 
       AND StillWorking = 'no';
       """,
    f"""SELECT SchoolName, SchoolCampus, COUNT(*) AS ActiveFacultyCount
       FROM salary_tracker_table
       WHERE StillWorking = 'yes'
       GROUP BY SchoolName, SchoolCampus
       ORDER BY ActiveFacultyCount DESC
       LIMIT 1;
       """,
    f"""SELECT PersonName, JobTitle, DepartmentName, SchoolName, Earnings
       FROM salary_tracker_table AS outer_table
       WHERE PersonName = 'Abhinaya Thota' 
       AND EarningsYear = (
                   SELECT MAX(EarningsYear)
                   FROM salary_tracker_table AS inner_table
                   WHERE inner_table.PersonID = outer_table.PersonID);
        """,
    f"""SELECT DepartmentName, AVG(Earnings) AS AverageEarnings
       FROM salary_tracker_table
       GROUP BY DepartmentName
       ORDER BY AverageEarnings DESC
       LIMIT 1;
       """,
]

# Store execution times for each file
execution_times = {file_size: [] for file_size in ['1MB', '10MB', '100MB']}

#open a log file to display outputs
with open('results/output_unnormalized.txt', 'w') as log_file:

   # create the table and load data into table
    def create_table(csv_file, table_name):
        conn = sqlite3.connect('salary_tracker.db')
        c = conn.cursor()
    
        with open(csv_file, newline='') as csv_file:
           reader = csv.reader(csv_file)
           headers = next(reader)  # get the column names of first row from the csv file
        
           c.execute(f"DROP TABLE IF EXISTS {table_name}")  #  drop the table if it already exists
           columns = ', '.join(f"{header} TEXT" for header in headers)  # convert the column names to string
           c.execute(f"CREATE TABLE \"{table_name}\" ({columns})")  # create the table with  the column names 

           # Insert data into the table
           for row in reader:
                placeholders = ', '.join('?' for _ in row)   # create a string of placeholders for the values
                c.execute(f"INSERT INTO \"{table_name}\" VALUES ({placeholders})", row)  # insert the  data into the table
        
        
           conn.commit()
        conn.close()

    # Function to execute queries and record execution times
    def queries(table_name):
        conn = sqlite3.connect('salary_tracker.db')  #connect to the database
        c = conn.cursor()
    
        for query in queries_list:
            start_time = time.time()  # record the start time of the query execution
            c.execute(query)
            result = c.fetchall()  #fetch all the results from the query
            end_time = time.time()  # record the end time of the query execution
        
            elapsed_time = end_time - start_time  # calculate the elapsed time of the query execution
            execution_times[current_file_size].append(elapsed_time)  # Record execution time of the query execution
            log_file.write(f"Query REsult: {result}\n Execution Time: {elapsed_time:.4f} seconds\n\n")
    
        conn.close()

    # Main loop to process each file size
    for file in csv_files:
        current_file_size = file.split('_')[-1].split('.')[0]  # Extract file size (1MB, 10MB, 100MB)
        log_file.write(f"\n--- Processing file size: {current_file_size} ---\n")
        create_table(file, 'salary_tracker_table')
        queries('salary_tracker_table')

# Modified plotting code
plt.figure(figsize=(12, 8))

# Prepare data for plotting
datasets = ['1MB', '10MB', '100MB']
query_times = {f'Query {i+1}': [] for i in range(len(queries_list))}

for dataset in datasets:
    for i, time in enumerate(execution_times[dataset]):
        query_times[f'Query {i+1}'].append(time)

# Plot lines for each query
for query, times in query_times.items():
    plt.plot(datasets, times, marker='o', label=query)

plt.title("Query Execution Times for Different CSV Sizes")
plt.xlabel("Dataset Size")
plt.ylabel("Execution Time (seconds)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("results/query_execution_times_unnormalized.png")
plt.show()
#Report
# Note: appends to the same log file instead of overwriting the detailed
# per-query results written above (the original version used 'w' here,
# which erased the detailed log — fixed to 'a' so both are preserved)
with open('results/output_unnormalized.txt', 'a') as log_file:
    log_file.write("\n--- Performance Analysis Report ---")
    log_file.write("Schema Design: salary_tracker_table with columns based on CSV file headers.")
    log_file.write("Performance Analysis:")
    for file_size, times in execution_times.items():
        log_file.write(f"{file_size} CSV:\n")
        for i, time in enumerate(times):
            log_file.write(f"  Query {i+1}: {time:.4f} seconds")
            log_file.write("Observations: Analyze the graphs and the times to identify trends and performance bottlenecks.")
