import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Database connection
def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Aman@2003",  # Replace with your MySQL password
        database="healthcare"  # Replace with your database name
    )
    return conn

# Fetch diseases and symptoms from the database
def fetch_diseases():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT disease_name, symptoms FROM diseases"
    cursor.execute(query)
    diseases = cursor.fetchall()
    cursor.close()
    conn.close()
    return diseases

# Fetch data from the patients table for analysis
def fetch_data():
    conn = connect_db()
    query = "SELECT age, city, disease FROM patients"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch disease cost and recovery time data
def fetch_disease_costs():
    conn = connect_db()
    query = "SELECT disease_name, cost, expected_recovery_time FROM disease_cost"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Match user symptoms with diseases
def match_disease(user_symptoms, disease_symptoms):
    user_symptom_set = set(user_symptoms)
    disease_symptom_set = set(disease_symptoms.split(','))

    # Calculate similarity percentage
    common_symptoms = user_symptom_set.intersection(disease_symptom_set)
    similarity = len(common_symptoms) / len(disease_symptom_set)
    
    return similarity

# Categorize age into groups of 10 (0-9, 10-19, 20-29, etc.)
def categorize_age(age):
    return f'{age // 10 * 10}-{(age // 10 * 10) + 9}'

# Plot the distribution of diseases by city
def plot_diseases_by_city(df):
    disease_city_group = df.groupby(['city', 'disease']).size().reset_index(name='count')
    pivot_df = disease_city_group.pivot(index='city', columns='disease', values='count').fillna(0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title("Distribution of Diseases by City")
    plt.xlabel("City")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Disease')
    plt.tight_layout()
    plt.show()

# Plot the distribution of diseases by age group (grouped in 10-year ranges)
def plot_diseases_by_age_group(df):
    df['age_group'] = df['age'].apply(categorize_age)
    disease_age_group = df.groupby(['age_group', 'disease']).size().reset_index(name='count')
    pivot_df_age = disease_age_group.pivot(index='age_group', columns='disease', values='count').fillna(0)
    pivot_df_age.plot(kind='bar', stacked=True, figsize=(12, 8), colormap="tab20")
    plt.title("Distribution of Diseases by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Disease')
    plt.tight_layout()
    plt.show()

# Plot disease costs
def plot_disease_costs(df):
    plt.figure(figsize=(12, 6))
    plt.bar(df['disease_name'], df['cost'], color='blue', alpha=0.7)
    plt.title('Disease Costs')
    plt.xlabel('Disease Name')
    plt.ylabel('Cost (in currency)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Display expected recovery times
def display_expected_recovery_times(df):
    plt.figure(figsize=(12, 6))
    recovery_times = []
    
    for recovery_time in df['expected_recovery_time']:
        # Check if recovery_time is a range or numeric
        try:
            if '-' in recovery_time:
                # Extract the lower limit of the range
                recovery_days = int(recovery_time.split('-')[0])
            else:
                recovery_days = int(recovery_time)
        except ValueError:
            # Handle non-integer values by assigning a default value (e.g., 0 or skipping)
            recovery_days = 0  # You could also choose to use np.nan if you prefer

        recovery_times.append(recovery_days)

    # Plotting the results
    plt.bar(df['disease_name'], recovery_times, color='green', alpha=0.7)
    plt.title('Expected Recovery Times')
    plt.xlabel('Disease Name')
    plt.ylabel('Expected Recovery Time (days)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Chatbot logic for symptom matching
def chatbot():
    print("Hello! I'm your healthcare assistant. How can I help you?")
    print("1. Check for diseases based on symptoms.")
    print("2. View disease analysis by city.")
    print("3. View disease analysis by age group.")
    print("4. View disease costs.")
    print("5. View expected recovery times.")
    
    choice = input("Please select an option (1, 2, 3, 4, or 5): ")
    
    if choice == '1':
        # Symptom-based disease matching
        user_input = input("Enter your symptoms (comma-separated): ")
        user_symptoms = [symptom.strip().lower() for symptom in user_input.split(',')]
        diseases = fetch_diseases()
        
        possible_diseases = []
        for disease in diseases:
            similarity = match_disease(user_symptoms, disease['symptoms'])
            if similarity > 0.3:  # Threshold for matching
                possible_diseases.append((disease['disease_name'], similarity))
        
        possible_diseases.sort(key=lambda x: x[1], reverse=True)
        if possible_diseases:
            print("\nBased on your symptoms, you might have the following diseases:")
            for disease, similarity in possible_diseases:
                print(f"- {disease} ({similarity*100:.2f}% match)")
        else:
            print("\nSorry, I couldn't match your symptoms to any known diseases.")
    
    elif choice == '2':
        # Disease distribution by city
        df = fetch_data()
        plot_diseases_by_city(df)
    
    elif choice == '3':
        # Disease distribution by age group
        df = fetch_data()
        plot_diseases_by_age_group(df)

    elif choice == '4':
        # Display disease costs
        df = fetch_disease_costs()
        plot_disease_costs(df)
    
    elif choice == '5':
        # Display expected recovery times
        df = fetch_disease_costs()
        display_expected_recovery_times(df)
    
    else:
        print("Invalid choice. Please select a valid option.")

# Main function
if __name__ == "__main__":
    chatbot()
