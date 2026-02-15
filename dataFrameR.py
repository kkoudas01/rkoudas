def generate_r_dataframe_code(column_headers_str, data_rows_str, df_name="data_frame_sot_eklogeis"):
    """
    Δημιουργεί κώδικα R για τη δημιουργία ενός data.frame από τις παρεχόμενες επικεφαλίδες
    στηλών και δεδομένα.

    Args:
        column_headers_str (str): Μια συμβολοσειρά με τις επικεφαλίδες των στηλών,
                                  χωρισμένες με κενά.
        data_rows_str (str): Μια συμβολοσειρά με τις γραμμές δεδομένων, όπου κάθε γραμμή
                             είναι χωρισμένη με νέα γραμμή και τα στοιχεία με κενά.
                             Οι ποσοστιαίες τιμές (π.χ., "78%") θα μετατραπούν σε ακέραιους.
        df_name (str): Το όνομα που θα δοθεί στο data.frame στην R.

    Returns:
        str: Ο κώδικας R έτοιμος για copy-paste.
    """

    # Καθαρισμός και διαχωρισμός των επικεφαλίδων των στηλών
    # Αντικαθιστούμε τους μη λατινικούς/ελληνικούς χαρακτήρες (εκτός του underscore)
    # για να είναι συμβατά ονόματα μεταβλητών στην R
    cleaned_headers = [
        header.replace("ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ", "ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ")
        .replace(" ", "_")
        .strip()
        for header in column_headers_str.split()
    ]
    # Ειδικός χειρισμός για την ΟΙΚΙΑΚΑ που έχει κενό στο τέλος στην είσοδο
    if "ΟΙΚΙΑΚΑ" in cleaned_headers:
        cleaned_headers = [h.replace("ΟΙΚΙΑΚΑ", "ΟΙΚΙΑΚΑ") for h in cleaned_headers]


    # Διαχωρισμός των γραμμών δεδομένων
    data_rows = [row.strip().split() for row in data_rows_str.strip().split('\n')]

    # Δημιουργία ενός λεξικού για να αποθηκεύσουμε τις στήλες
    # Κάθε κλειδί είναι το όνομα της στήλης και η τιμή είναι μια λίστα με τα δεδομένα της στήλης
    columns_data = {header: [] for header in cleaned_headers}

    for row in data_rows:
        response_category = row[0] # Π.χ. "Συμφωνώ"
        columns_data["απάντηση"].append(f'"{response_category}"') # Προσθήκη με εισαγωγικά

        # Ξεκινάμε από τον δεύτερο δείκτη για τα αριθμητικά δεδομένα
        for i, value_str in enumerate(row[1:]):
            # Καθαρισμός του '%' και μετατροπή σε ακέραιο
            numeric_value = int(value_str.replace('%', ''))
            columns_data[cleaned_headers[i + 1]].append(str(numeric_value))

    # Δημιουργία του κώδικα R
    r_code_lines = []
    r_code_lines.append(f'{df_name} <- data.frame(')

    for i, header in enumerate(cleaned_headers):
        values = ", ".join(columns_data[header])
        if header == "απάντηση":
            r_code_lines.append(f'  {header} = c({values}){"" if i == len(cleaned_headers) - 1 else ","}')
        else:
            r_code_lines.append(f'  {header} = c({values}){"" if i == len(cleaned_headers) - 1 else ","}')

    r_code_lines.append(')')

    return "\n".join(r_code_lines)

# --- Παράδειγμα Χρήσης ---

# 1) Εισαγωγή των επικεφαλίδων των στηλών
column_headers_input = "απάντηση σύνολο ΝΔ ΣΥΡΙΖΑ ΠΑΣΟΚ ΚΚΕ Σπαρτιάτες Ελληνική_Λύση Νίκη Πλεύση_Ελευθερίας Νέα_Αριστερά ΜΕΡΑ25 Αριστερά_Κεντροαριστερά"

# 2) Εισαγωγή των δεδομένων του πίνακα
data_rows_input = """
ΚοινωνικέςΤάξειςΝΑΙ 78% 58% 93% 80% 93% 85% 84% 76% 87% 96% 95% 91%
ΚοινωνικέςΤάξειςΟΧΙ 20% 39% 7% 15% 6% 15% 14% 22% 13% 2% 2% 7%
ΚοινωνικέςΤάξειςΔΞ 2% 3% 1% 4% 1% 0% 2% 2% 0% 2% 2% 1%
"""

# Κλήση της συνάρτησης για παραγωγή του κώδικα R
r_code_output = generate_r_dataframe_code(column_headers_input, data_rows_input)

# Εκτύπωση του παραγόμενου κώδικα R
print(r_code_output)