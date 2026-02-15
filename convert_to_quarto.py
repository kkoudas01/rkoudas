import os
import shutil
import re

# Βάλε εδώ την πλήρη διαδρομή αν δεν τρέχεις το script μέσα από τον φάκελο
SOURCE_DIR = r"C:\Users\kkoud\Documents\GitHub\r4social" 
BACKUP_DIR = os.path.join(SOURCE_DIR, "backup_rmd")

# Λεξικό αντικαταστάσεων για το YAML header
REPLACEMENTS = {
    r"output:": "format:",
    r"html_document:": "html:",
    r"pdf_document:": "pdf:",
    r"highlight:": "highlight-style:",
    r"code_folding:": "code-fold:",
    r"self_contained: true": "embed-resources: true",
}

def convert():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    files_processed = 0
    
    for file in os.listdir(SOURCE_DIR):
        if file.endswith(".Rmd"):
            rmd_path = os.path.join(SOURCE_DIR, file)
            qmd_path = os.path.join(SOURCE_DIR, file.replace(".Rmd", ".qmd"))
            
            # 1. Backup το πρωτότυπο Rmd
            shutil.copy2(rmd_path, os.path.join(BACKUP_DIR, file))
            
            # 2. Διάβασμα και μετατροπή
            with open(rmd_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Διόρθωση YAML
            new_content = content
            for pattern, rep in REPLACEMENTS.items():
                new_content = re.sub(pattern, rep, new_content)

            # 3. Αποθήκευση ως QMD
            with open(qmd_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Μετατράπηκε: {file} -> {os.path.basename(qmd_path)}")
            files_processed += 1

    print(f"\nΟλοκληρώθηκε! Μετατράπηκαν {files_processed} αρχεία.")

if __name__ == "__main__":
    convert()