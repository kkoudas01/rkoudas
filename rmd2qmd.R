# Φόρτωση απαραίτητων βιβλιοθηκών
if (!require(knitr)) install.packages("knitr")
library(knitr)

# Συνάρτηση επεξεργασίας του YAML header για Quarto
fix_yaml_for_quarto <- function(file_path) {
  lines <- readLines(file_path, encoding = "UTF-8")
  
  # Εντοπισμός των ορίων του YAML (τα --- στην αρχή)
  yaml_delimiters <- which(lines == "---")
  
  if (length(yaml_delimiters) >= 2) {
    yaml_start <- yaml_delimiters[1]
    yaml_end <- yaml_delimiters[2]
    
    # Απομόνωση των γραμμών του YAML
    yaml_lines <- lines[(yaml_start + 1):(yaml_end - 1)]
    
    # 1. Αλλαγή του output: html_document σε format: html
    yaml_lines <- gsub("^output:", "format:", yaml_lines)
    yaml_lines <- gsub("html_document:", "html:", yaml_lines)
    
    # 2. Μετατροπή των snake_case σε kebab-case (π.χ. number_sections -> number-sections)
    yaml_lines <- gsub("number_sections:", "number-sections:", yaml_lines)
    yaml_lines <- gsub("fig_caption:", "fig-cap:", yaml_lines)
    # Το fig_width/height στο Quarto είναι fig-width/height
    yaml_lines <- gsub("fig_width:", "fig-width:", yaml_lines)
    yaml_lines <- gsub("fig_height:", "fig-height:", yaml_lines)
    
    # 3. Αφαίρεση του toc_float (Το Quarto το χειρίζεται διαφορετικά, συνήθως είναι default floating)
    # Αν θέλουμε να το κρατήσουμε καθαρό, αφαιρούμε τη γραμμή.
    yaml_lines <- yaml_lines[!grepl("toc_float:", yaml_lines)]
    
    # Επανασύνθεση του αρχείου
    new_content <- c(
      "---",
      yaml_lines,
      lines[yaml_end:length(lines)]
    )
    
    writeLines(new_content, file_path, useBytes = TRUE)
  }
}

# Κύρια διαδικασία
convert_all_rmd <- function() {
  # Εύρεση όλων των .Rmd αρχείων στον τρέχοντα φάκελο
  rmd_files <- list.files(pattern = "\\.Rmd$", full.names = TRUE, recursive = FALSE)
  
  if (length(rmd_files) == 0) {
    message("Δεν βρέθηκαν αρχεία .Rmd στον τρέχοντα φάκελο.")
    return()
  }
  
  message(paste("Βρέθηκαν", length(rmd_files), "αρχεία για μετατροπή."))
  
  for (rmd_file in rmd_files) {
    qmd_file <- sub("\\.Rmd$", ".qmd", rmd_file)
    
    message(paste("Μετατροπή:", basename(rmd_file), "->", basename(qmd_file)))
    
    # Βήμα 1: Χρήση του knitr για μετατροπή των chunks ({r echo=F} -> #| echo: false)
    # Η convert_chunk_header διαβάζει το Rmd και γράφει το Qmd με τα νέα chunks
    tryCatch({
      knitr::convert_chunk_header(input = rmd_file, output = qmd_file)
      
      # Βήμα 2: Επεξεργασία του YAML στο νέο .qmd αρχείο
      fix_yaml_for_quarto(qmd_file)
      
      # Βήμα 3: Διαγραφή του παλιού .Rmd αρχείου (αφού υπάρχει backup)
      file.remove(rmd_file)
      
    }, error = function(e) {
      message(paste("Σφάλμα στο αρχείο:", rmd_file, "\n", e))
    })
  }
  
  message("Η διαδικασία ολοκληρώθηκε!")
}

# Εκτέλεση της συνάρτησης
convert_all_rmd()