# ============================================================
#  QMD Data Scanner
#  Σαρώνει QMD αρχεία και εντοπίζει τα data files που χρησιμοποιούν
# ============================================================

# Εγκατάσταση απαιτούμενων πακέτων αν δεν υπάρχουν
required_packages <- c("rstudioapi")
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

library(rstudioapi)

# ============================================================
# 1. Επιλογή φακέλου μέσω UI
# ============================================================
message(">> Παρακαλώ επιλέξτε τον φάκελο που περιέχει τα .qmd αρχεία...")
folder_path <- rstudioapi::selectDirectory(
  caption = "Επιλογή φακέλου με QMD αρχεία",
  label   = "Επιλογή"
)

if (is.null(folder_path) || folder_path == "") {
  stop("Δεν επιλέχθηκε φάκελος. Το script τερματίστηκε.")
}

# ============================================================
# 2. Επιλογή αρχείου εξόδου μέσω UI
# ============================================================
message(">> Παρακαλώ επιλέξτε πού θα αποθηκευτεί το αρχείο εξόδου (.txt)...")
output_file <- rstudioapi::selectFile(
  caption    = "Αποθήκευση αρχείου αποτελεσμάτων",
  label      = "Αποθήκευση",
  path       = folder_path,
  filter     = "Text Files (*.txt)",
  existing   = FALSE
)

if (is.null(output_file) || output_file == "") {
  stop("Δεν επιλέχθηκε αρχείο εξόδου. Το script τερματίστηκε.")
}

# Βεβαιωνόμαστε ότι έχει κατάληξη .txt
if (!grepl("\\.txt$", output_file, ignore.case = TRUE)) {
  output_file <- paste0(output_file, ".txt")
}

# ============================================================
# 3. Συλλογή QMD αρχείων
# ============================================================
qmd_files <- list.files(
  path       = folder_path,
  pattern    = "\\.qmd$",
  full.names = TRUE,
  recursive  = FALSE   # Αλλάξτε σε TRUE για αναζήτηση σε υποφακέλους
)

if (length(qmd_files) == 0) {
  stop(paste("Δεν βρέθηκαν .qmd αρχεία στον φάκελο:", folder_path))
}

message(sprintf(">> Βρέθηκαν %d QMD αρχεία. Σάρωση...", length(qmd_files)))

# ============================================================
# 4. Regex pattern για εντοπισμό data files
# ============================================================
# Επεκτείνετε τις καταλήξεις εδώ αν χρειαστεί
data_extensions <- c(
  "xlsx", "xls", "xlsm",          # Excel
  "csv", "tsv",                    # Delimited text
  "txt",                           # Plain text data
  "sav", "por",                    # SPSS
  "dta",                           # Stata
  "rds", "rdata", "rda",          # R data
  "json", "geojson",              # JSON
  "xml",                           # XML
  "parquet", "feather",           # Columnar formats
  "db", "sqlite", "sqlite3",      # Databases
  "shp", "gpkg"                    # Spatial
)

ext_pattern <- paste0(
  "[\"'`]([^\"'`\\s]+\\.(",
  paste(data_extensions, collapse = "|"),
  "))[\"'`]"
)

# ============================================================
# 5. Σάρωση κάθε QMD αρχείου
# ============================================================
extract_data_files <- function(qmd_path) {
  lines   <- readLines(qmd_path, warn = FALSE, encoding = "UTF-8")
  content <- paste(lines, collapse = "\n")
  
  matches <- regmatches(content, gregexpr(ext_pattern, content, ignore.case = TRUE, perl = TRUE))[[1]]
  
  if (length(matches) == 0) return(character(0))
  
  # Κρατάμε μόνο το εσωτερικό (όνομα αρχείου) από κάθε match
  files_found <- regmatches(
    matches,
    regexpr(
      paste0("[^\"'`\\s]+\\.(",
             paste(data_extensions, collapse = "|"), ")",
             collapse = ""),
      matches, ignore.case = TRUE, perl = TRUE
    )
  )
  
  unique(trimws(files_found))
}

results <- lapply(qmd_files, function(f) {
  list(
    qmd_name   = basename(f),
    data_files = extract_data_files(f)
  )
})

# ============================================================
# 6. Δημιουργία πίνακα εξόδου σε txt
# ============================================================
folder_name <- basename(folder_path)

# Υπολογισμός πλάτους στηλών
col1_width <- max(nchar("QMD Αρχείο"),  max(sapply(results, function(r) nchar(r$qmd_name))))
col2_width <- max(nchar("Data Αρχεία"), max(sapply(results, function(r) {
  if (length(r$data_files) == 0) nchar("(κανένα)") else max(nchar(r$data_files))
})))

col1_width <- col1_width + 2
col2_width <- col2_width + 2

make_row <- function(c1, c2) {
  sprintf("| %-*s | %-*s |", col1_width, c1, col2_width, c2)
}

separator <- paste0(
  "+", paste(rep("-", col1_width + 2), collapse = ""),
  "+", paste(rep("-", col2_width + 2), collapse = ""),
  "+"
)

# Συγκέντρωση γραμμών
output_lines <- character(0)

# Τίτλος
title_line <- paste0("Φάκελος: ", folder_name)
output_lines <- c(
  output_lines,
  strrep("=", nchar(separator)),
  title_line,
  strrep("=", nchar(separator)),
  ""
)

# Header πίνακα
output_lines <- c(
  output_lines,
  separator,
  make_row("QMD Αρχείο", "Data Αρχεία"),
  separator
)

# Γραμμές δεδομένων
for (r in results) {
  if (length(r$data_files) == 0) {
    output_lines <- c(output_lines, make_row(r$qmd_name, "(κανένα)"))
  } else {
    # Πρώτη γραμμή με το όνομα qmd
    output_lines <- c(output_lines, make_row(r$qmd_name, r$data_files[1]))
    # Επιπλέον data files στις επόμενες γραμμές
    if (length(r$data_files) > 1) {
      for (df in r$data_files[-1]) {
        output_lines <- c(output_lines, make_row("", df))
      }
    }
  }
  output_lines <- c(output_lines, separator)
}

# Footer
output_lines <- c(
  output_lines,
  "",
  paste0("Σύνολο QMD αρχείων: ", length(qmd_files)),
  paste0("Ημερομηνία σάρωσης: ", format(Sys.time(), "%d/%m/%Y %H:%M:%S"))
)

# ============================================================
# 7. Εγγραφή αρχείου
# ============================================================
writeLines(output_lines, con = output_file, useBytes = FALSE)

message(sprintf(">> Ολοκληρώθηκε! Τα αποτελέσματα αποθηκεύτηκαν στο:\n   %s", output_file))

# Προαιρετικά: άνοιγμα του αρχείου στο RStudio
if (rstudioapi::isAvailable()) {
  rstudioapi::navigateToFile(output_file)
}