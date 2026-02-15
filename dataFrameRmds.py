import re

def generate_r_dataframe_and_merge_code(
    df1_column_headers_str,
    df1_data_rows_str,
    df2_column_headers_str,
    df2_data_rows_str,
    df_base_name,
    df1_suffix,
    df2_suffix,
    response_names_str
):
    """
    Δημιουργεί κώδικα R για τη δημιουργία δύο data.frame, τα συγχωνεύει
    και προσθέτει επιπλέον εντολές μετασχηματισμού και ανάλυσης.

    Args:
        df1_column_headers_str (str): Επικεφαλίδες στηλών για το πρώτο dataframe.
        df1_data_rows_str (str): Δεδομένα γραμμών για το πρώτο dataframe.
        df2_column_headers_str (str): Επικεφαλίδες στηλών για το δεύτερο dataframe.
        df2_data_rows_str (str): Δεδομένα γραμμών για το δεύτερο dataframe.
        df_base_name (str): Η βάση του ονόματος για τα dataframes (π.χ., "koinonikesTaxeis").
        df1_suffix (str): Το suffix για το πρώτο dataframe (π.χ., "Social").
        df2_suffix (str): Το suffix για το δεύτερο dataframe (π.χ., "Party").
        response_names_str (str): Μια συμβολοσειρά με τα νέα ονόματα για "Συμφωνώ", "Διαφωνώ", "ΔΞ/ΔΑ",
                                  χωρισμένα με κενά (π.χ., "ΚοινωνικέςΤάξειςΝΑΙ ΚοινωνικέςΤάξειςΟΧΙ ΚοινωνικέςΤάξειςΔΞ").

    Returns:
        str: Ο πλήθος κώδικας R έτοιμος για copy-paste.
    """

    response_names = [f'"{name.strip()}"' for name in response_names_str.split()]

    def clean_header(header):
        # Αντικαθιστούμε τα κενά με "_" και αφαιρούμε τυχόν περίσσεια κενά
        cleaned = header.replace(" ", "_").strip()
        # Ειδικός χειρισμός για ορισμένα ονόματα με τελείες ή περίεργους χαρακτήρες
        # Βεβαιωνόμαστε ότι το "ΔΞ/ΔΑ" ή "ΔΞ_ΔΑ" αντιμετωπίζεται σωστά
        cleaned = cleaned.replace("ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ", "ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ")
        return cleaned

    def parse_data_to_r_code(column_headers_str, data_rows_str, df_specific_name, response_names_list):
        cleaned_headers = [clean_header(header) for header in column_headers_str.split()]
        
        # Εδώ κάνουμε τη βελτίωση: Χρησιμοποιούμε re.split για να διαχωρίσουμε τη γραμμή
        # λαμβάνοντας υπόψη ένα ή περισσότερα κενά ως διαχωριστή,
        # και αντιμετωπίζουμε το "ΔΞ / ΔΑ" ως ένα ενιαίο στοιχείο στην πρώτη στήλη.
        # Πρώτα καθαρίζουμε τη συμβολοσειρά εισόδου για να διαχειριστούμε το "ΔΞ / ΔΑ"
        # ώστε να γίνει "ΔΞ_ΔΑ" για καλύτερο διαχωρισμό, αν και το re.split θα βοηθήσει ούτως ή άλλως.
        
        # Προ-επεξεργασία των γραμμών δεδομένων για να αντικαταστήσουμε "ΔΞ / ΔΑ" με "ΔΞ/ΔΑ" ή "ΔΞ_ΔΑ"
        # για ευκολότερο διαχωρισμό. Επειδή το "ΔΞ / ΔΑ" είναι η πρώτη στήλη,
        # μπορούμε να το αντικαταστήσουμε πριν το split.
        processed_data_rows_str = data_rows_str.replace("ΔΞ / ΔΑ", "ΔΞ/ΔΑ")
        
        # Τώρα χρησιμοποιούμε re.split για να διαχωρίσουμε με βάση ένα ή περισσότερα κενά
        data_rows = [re.split(r'\s+', row.strip()) for row in processed_data_rows_str.strip().split('\n') if row.strip()]

        columns_data = {header: [] for header in cleaned_headers}

        for i, row in enumerate(data_rows):
            # Χρησιμοποιούμε τα νέα ονόματα για την στήλη "απάντηση"
            # Βεβαιωνόμαστε ότι η λίστα response_names_list έχει αρκετά στοιχεία
            if i < len(response_names_list):
                columns_data["απάντηση"].append(response_names_list[i])
            else:
                columns_data["απάντηση"].append(f'"{row[0]}"') # Fallback αν δεν υπάρχει αντιστοίχιση

            # Ξεκινάμε από τον δεύτερο δείκτη για τα αριθμητικά δεδομένα
            for j, value_str in enumerate(row[1:]):
                # Καθαρισμός του '%' και μετατροπή σε ακέραιο
                # Επειδή έχουμε ήδη χειριστεί το "ΔΞ / ΔΑ" στην προ-επεξεργασία,
                # οι αριθμοί θα πρέπει να είναι καθαροί.
                numeric_value = int(value_str.replace('%', ''))
                
                # Ελέγχουμε αν το j + 1 είναι εντός των ορίων της cleaned_headers
                if (j + 1) < len(cleaned_headers):
                    columns_data[cleaned_headers[j + 1]].append(str(numeric_value))
                else:
                    print(f"Προσοχή: Η τιμή '{value_str}' στη σειρά {i+1} ξεπερνά τις δηλωμένες επικεφαλίδες για το DF '{df_specific_name}'.")


        r_code_lines = []
        r_code_lines.append(f'{df_specific_name} <- data.frame(')

        for i, header in enumerate(cleaned_headers):
            values = ", ".join(columns_data[header])
            r_code_lines.append(f'  {header} = c({values}){"" if i == len(cleaned_headers) - 1 else ","}')

        r_code_lines.append(')')
        return "\n".join(r_code_lines)

    # --- Παραγωγή κώδικα για το πρώτο dataframe ---
    df1_name_full = f"{df_base_name}{df1_suffix}"
    r_code_df1 = parse_data_to_r_code(
        df1_column_headers_str, df1_data_rows_str, df1_name_full, response_names
    )

    # --- Παραγωγή κώδικα για το δεύτερο dataframe ---
    df2_name_full = f"{df_base_name}{df2_suffix}"
    r_code_df2 = parse_data_to_r_code(
        df2_column_headers_str, df2_data_rows_str, df2_name_full, response_names
    )

    # --- Συγχώνευση και επιπλέον εντολές ---
    merge_code = f"""
{df_base_name} <- merge(x={df1_name_full},y={df2_name_full},by=c("απάντηση","σύνολο"))
{df_base_name}
{df_base_name}Temp <- {df_base_name}[,-1]
row.names({df_base_name}Temp) <- {df_base_name}[,1]
{df_base_name}Temp2 <- data.frame(t({df_base_name}Temp))
{df_base_name}Temp2$omada <- colnames({df_base_name}Temp)
{df_base_name}Temp2 <- {df_base_name}Temp2[, c("omada", setdiff(names({df_base_name}Temp2), "omada"))]
PoPrKlim({df_base_name}Temp2)
"""

    full_r_code = f"{r_code_df1}\n\n{r_code_df2}\n{merge_code}"
    return full_r_code

# --- Δεδομένα Εισόδου από τον Χρήστη ---

# 1) Ονόματα στηλών για το 1ο dataframe (π.χ., "Social")
df1_headers = "απάντηση σύνολο ηλικία17_34 ηλικία35_54 ηλικία55άνω Έως7000 από7001έως16000 από16001έως30000 Πάνω30000 ΜΙΣΘΩΤΟΣ_ΔΗΜΟΣΙΟΥ ΜΙΣΘΩΤΟΣ_ΙΔΙΩΤΙΚΟΥ ΣΥΝΤΑΞΙΟΥΧΟΣ ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ ΑΝΕΡΓΟΣ ΟΙΚΙΑΚΑ"

# 2) Δεδομένα για το 1ο dataframe
df1_data = """
Συμφωνώ 78% 76% 80% 76% 78% 83% 77% 73% 81% 76% 78% 71% 88% 81%
Διαφωνώ 20% 23% 18% 21% 19% 15% 21% 24% 16% 20% 21% 27% 10% 17%
ΔΞ/ΔΑ 2% 1% 2% 3% 2% 2% 2% 3% 3% 3% 2% 2% 2% 2%
"""

# 3) Ονόματα στηλών για το 2ο dataframe (π.χ., "Party")
df2_headers = "απάντηση σύνολο ΝΔ ΣΥΡΙΖΑ ΠΑΣΟΚ ΚΚΕ Σπαρτιάτες Ελληνική_Λύση Νίκη Πλεύση_Ελευθερίας Νέα_Αριστερά ΜΕΡΑ25 Αριστερά_Κεντροαριστερά"

# 4) Δεδομένα για το 2ο dataframe
df2_data = """
Συμφωνώ 78% 58% 93% 80% 93% 85% 84% 76% 87% 96% 95% 91%
Διαφωνώ 20% 39% 7% 15% 6% 15% 14% 22% 13% 2% 2% 7%
ΔΞ / ΔΑ 2% 3% 1% 0% 1% 0% 2% 2% 0% 2% 2% 1%
"""

# 5) Βάση ονόματος για τα dataframes
base_name = "koinonikesTaxeis"

# 6) Suffixes για τα dataframes
suffix1 = "Social"
suffix2 = "Party"

# 7) Νέα ονόματα για τις κατηγορίες "απάντηση"
new_response_names = "ΚοινωνικέςΤάξειςΝΑΙ ΚοινωνικέςΤάξειςΟΧΙ ΚοινωνικέςΤάξειςΔΞ"

# Κλήση της συνάρτησης για παραγωγή του πλήρους κώδικα R
final_r_code = generate_r_dataframe_and_merge_code(
    df1_headers, df1_data,
    df2_headers, df2_data,
    base_name, suffix1, suffix2,
    new_response_names
)

# Εκτύπωση του παραγόμενου κώδικα R
print(final_r_code)