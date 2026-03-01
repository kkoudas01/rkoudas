# Μετατροπή excel και csv σε rds

# 1. Έλεγχος και φόρτωση απαραίτητων εργαλείων
if (!requireNamespace("rstudioapi", quietly = TRUE)) {
  install.packages("rstudioapi")
}
if (!requireNamespace("readxl", quietly = TRUE)) {
  install.packages("readxl")
}

library(tools)
library(readxl)

# 2. Ασφαλής επιλογή φακέλου μέσω RStudio UI
folder_path <- rstudioapi::selectDirectory(
  caption = "Επίλεξε τον φάκελο με τα CSV/Excel σου",
  label = "Επιλογή Φακέλου"
)

# Έλεγχος αν ο χρήστης πάτησε Cancel
if (is.null(folder_path)) {
  stop("Η διαδικασία ακυρώθηκε από τον χρήστη.")
}

message("Επιλέχθηκε ο φάκελος: ", folder_path)

# 3. Εύρεση αρχείων
files_to_convert <- list.files(path = folder_path, 
                               pattern = "\\.(csv|xlsx|xls)$", 
                               full.names = TRUE, 
                               ignore.case = TRUE)

if (length(files_to_convert) == 0) {
  stop("Δεν βρέθηκαν αρχεία Excel ή CSV στον φάκελο.")
}

# 4. Μετατροπή
for (file in files_to_convert) {
  
  ext <- tolower(file_ext(file))
  base_name <- file_path_sans_ext(basename(file))
  out_file <- file.path(folder_path, paste0(base_name, ".rds"))
  
  # Αν υπάρχει ήδη το .rds, το προσπερνάμε για οικονομία χρόνου
  if (file.exists(out_file)) {
    message("-> Το '", base_name, ".rds' υπάρχει ήδη. Παράλειψη.")
    next
  }
  
  message("Μετατροπή: ", basename(file), "...")
  
  tryCatch({
    # Διάβασμα (χρησιμοποιούμε read.csv της base R για να μη θέλουμε extra πακέτα)
    if (ext == "csv") {
      temp_data <- read.csv(file, stringsAsFactors = FALSE)
    } else {
      temp_data <- read_excel(file)
    }
    
    # Αποθήκευση σε .rds (default compression = "gzip")
    saveRDS(temp_data, file = out_file)
    
  }, error = function(e) {
    message("!!! Σφάλμα στο αρχείο ", basename(file), ": ", e$message)
  })
}

message("\n--- Η ΜΕΤΑΤΡΟΠΗ ΟΛΟΚΛΗΡΩΘΗΚΕ ---")