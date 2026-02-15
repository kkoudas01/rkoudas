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
    Δημιουργεί κώδικα R για τη δημιουργία δύο data.frame, τα συγχωνεύει,
    προσθέτει επιπλέον εντολές μετασχηματισμού και ανάλυσης CA,
    και μορφοποιεί την έξοδο ως R Markdown snippet.

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
        str: Ο πλήρης κώδικας R Markdown έτοιμος για copy-paste.
    """

    response_names = [f'"{name.strip()}"' for name in response_names_str.split()]

    def clean_header(header):
        cleaned = header.replace(" ", "_").strip()
        cleaned = cleaned.replace("ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ", "ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ")
        return cleaned

    def parse_data_to_r_code_chunk(column_headers_str, data_rows_str, df_specific_name, response_names_list):
        cleaned_headers = [clean_header(header) for header in column_headers_str.split()]
        processed_data_rows_str = data_rows_str.replace("ΔΞ / ΔΑ", "ΔΞ/ΔΑ")
        data_rows = [re.split(r'\s+', row.strip()) for row in processed_data_rows_str.strip().split('\n') if row.strip()]

        columns_data = {header: [] for header in cleaned_headers}

        for i, row in enumerate(data_rows):
            if i < len(response_names_list):
                columns_data["απάντηση"].append(response_names_list[i])
            else:
                columns_data["απάντηση"].append(f'"{row[0]}"') 

            for j, value_str in enumerate(row[1:]):
                numeric_value = int(value_str.replace('%', ''))
                if (j + 1) < len(cleaned_headers):
                    columns_data[cleaned_headers[j + 1]].append(str(numeric_value))
                else:
                    pass

        r_code_lines = []
        r_code_lines.append(f'{df_specific_name} <- data.frame(')

        for i, header in enumerate(cleaned_headers):
            values = ", ".join(columns_data[header])
            r_code_lines.append(f'  {header} = c({values}){"" if i == len(cleaned_headers) - 1 else ","}')

        r_code_lines.append(')')
        return "\n".join(r_code_lines)

    # --- Ονόματα Dataframe ---
    df1_name_full = f"{df_base_name}{df1_suffix}"
    df2_name_full = f"{df_base_name}{df2_suffix}"

    # --- Κώδικας R για το πρώτο dataframe ---
    r_code_df1 = parse_data_to_r_code_chunk(
        df1_column_headers_str, df1_data_rows_str, df1_name_full, response_names
    )

    # --- Κώδικας R για το δεύτερο dataframe ---
    r_code_df2 = parse_data_to_r_code_chunk(
        df2_column_headers_str, df2_data_rows_str, df2_name_full, response_names
    )

    # --- Κώδικας R για συγχώνευση και μετασχηματισμούς ---
    merge_and_transform_code = f"""
{df_base_name} <- merge(x={df1_name_full},y={df2_name_full},by=c("απάντηση","σύνολο"))
{df_base_name}Temp <- {df_base_name}[,-1]
row.names({df_base_name}Temp) <- {df_base_name}[,1]
{df_base_name}Temp2 <- data.frame(t({df_base_name}Temp))
{df_base_name}Temp2$omada <- colnames({df_base_name}Temp)
{df_base_name}Temp2 <- {df_base_name}Temp2[, c("omada", setdiff(names({df_base_name}Temp2), "omada"))]
"""

    # --- Κώδικας R για το CA Analysis ---
    ca_analysis_code = f"""
{df_base_name}PartyTemp <- {df2_name_full}[,-c(1,2)]
row.names({df_base_name}PartyTemp) <- {df2_name_full}[,1]
{df_base_name}PartyAll <- {df_base_name}PartyTemp
{df_base_name}PartyAll$ΝΔ <- {df_base_name}PartyAll$ΝΔ*feb29[1]
{df_base_name}PartyAll$ΣΥΡΙΖΑ <- {df_base_name}PartyAll$ΣΥΡΙΖΑ*feb29[2]
{df_base_name}PartyAll$ΠΑΣΟΚ <- {df_base_name}PartyAll$ΠΑΣΟΚ*feb29[3]
{df_base_name}PartyAll$ΚΚΕ <- {df_base_name}PartyAll$ΚΚΕ*feb29[4]
{df_base_name}PartyAll$Σπαρτιάτες <- {df_base_name}PartyAll$Σπαρτιάτες*feb29[5]
{df_base_name}PartyAll$Ελληνική_Λύση <- {df_base_name}PartyAll$Ελληνική_Λύση*feb29[6]
{df_base_name}PartyAll$Νίκη <- {df_base_name}PartyAll$Νίκη*feb29[7]
{df_base_name}PartyAll$Πλεύση_Ελευθερίας <- {df_base_name}PartyAll$Πλεύση_Ελευθερίας*feb29[8]
{df_base_name}PartyAll$Νέα_Αριστερά <- {df_base_name}PartyAll$Νέα_Αριστερά*feb29[9]
{df_base_name}PartyAll$ΜΕΡΑ25 <- {df_base_name}PartyAll$ΜΕΡΑ25*feb29[10]
{df_base_name}PartyAll <- {df_base_name}PartyAll[,]
{df_base_name}PartyCORA <- CA({df_base_name}PartyAll, graph=FALSE)
fviz_ca_biplot({df_base_name}PartyCORA,
               repel = TRUE, # Αποτρέπει την επικάλυψη ετικετών
               col.row = "purple", # Χρώμα για τις γραμμές (πολιτικές ταυτότητες)
               col.col = "orange",  # Χρώμα για τις στήλες (κόμματα)
               title = "Γράφημα Διπλής Προβολής πολιτικών κομμάτων και απαντήσεων"
               )
"""

    # --- Συναρμολόγηση του τελικού R Markdown κώδικα ---
    # Διορθώθηκαν τα διπλά άγκιστρα σε μονά για τη σωστή μορφοποίηση του R Markdown.
    full_r_code_markdown = (
        "```{r, echo=FALSE}\n"
        f"{r_code_df1}\n\n"
        f"{r_code_df2}\n\n"
        f"{merge_and_transform_code}\n"
        "```\n\n"
        "\n### {.tabset .tabset-fade .tabset-pills .unnumbered .toc-ignore}\n\n"
        "#### Πόσο κοντά είναι τα κόμματα στα ΝΑΙ/ΟΧΙ; {.unnumbered }\n\n"
        "```{r, echo=FALSE}\n"
        f"{ca_analysis_code}\n"
        "```\n\n"
        "#### Πόσο κοντά είναι τα κόμματα στην εκάστοτε κοινωνική ομάδα; {.unnumbered }\n\n"
        "```{r, echo=FALSE, message=FALSE, warning=FALSE}\n"
        f"PoPrKlim_interactive2D({df_base_name}Temp2)\n"
        "```\n\n"
        "```{r, echo=FALSE}\n"
        f"kommataKoinvnia <- merge(x=kommataKoinvnia,y={df_base_name}Temp2,by='omada')\n"
        "```\n"
    )

    return full_r_code_markdown

# --- Δεδομένα Εισόδου από τον Χρήστη ---

# 1) Ονόματα στηλών για το 1ο dataframe (π.χ., "Social")
df1_headers = "απάντηση σύνολο ηλικία17_34 ηλικία35_54 ηλικία55άνω Έως7000 από7001έως16000 από16001έως30000 Πάνω30000 ΜΙΣΘΩΤΟΣ_ΔΗΜΟΣΙΟΥ ΜΙΣΘΩΤΟΣ_ΙΔΙΩΤΙΚΟΥ ΣΥΝΤΑΞΙΟΥΧΟΣ ΕΛΕΥΘ.ΕΠΑΓΓΕΛΜΑΤΙΑΣ_ΑΥΤΟΑΠΑΣΧΟΛΟΥΜΕΝΟΣ ΑΝΕΡΓΟΣ ΟΙΚΙΑΚΑ"

# 2) Δεδομένα για το 1ο dataframe
df1_data = """
Συμφωνώ 72% 66% 71% 76% 66% 70% 76% 74% 69% 67% 79% 77% 67% 81%
Διαφωνώ 22% 28% 23% 19% 28% 25% 19% 20% 23% 26% 17% 18% 29% 17%
ΔΞ / ΔΑ 6% 6% 6% 5% 6% 5% 5% 6% 8% 7% 4% 5% 4% 2%
"""

# 3) Ονόματα στηλών για το 2ο dataframe (π.χ., "Party")
df2_headers = "απάντηση σύνολο ΝΔ ΣΥΡΙΖΑ ΠΑΣΟΚ ΚΚΕ Σπαρτιάτες Ελληνική_Λύση Νίκη Πλεύση_Ελευθερίας Νέα_Αριστερά ΜΕΡΑ25 Αριστερά_Κεντροαριστερά"

# 4) Δεδομένα για το 2ο dataframe
df2_data = """
Συμφωνώ 72% 70% 94% 83% 91% 46% 43% 22% 74% 100% 93% 93%
Διαφωνώ 22% 24% 4% 11% 8% 50% 49% 64% 26% 0% 0% 5%
ΔΞ / ΔΑ 6% 6% 2% 6% 1% 4% 7% 14% 0% 0% 7% 1%
"""

# 5) Βάση ονόματος για τα dataframes
base_name = "ekklisiaKratos"

# 6) Suffixes για τα dataframes
suffix1 = "Social"
suffix2 = "Party"

# 7) Νέα ονόματα για τις κατηγορίες "απάντηση"
new_response_names = "ΧωρισμόςΕκκλησίαςΚράτουςΝΑΙ ΧωρισμόςΕκκλησίαςΚράτουςΟΧΙ ΧωρισμόςΕκκλησίαςΚράτουςΔΞ"

# Κλήση της συνάρτησης για παραγωγή του πλήρους κώδικα R
final_r_code_markdown = generate_r_dataframe_and_merge_code(
    df1_headers, df1_data,
    df2_headers, df2_data,
    base_name, suffix1, suffix2,
    new_response_names
)

# Εκτύπωση του παραγόμενου κώδικα R Markdown
print(final_r_code_markdown)