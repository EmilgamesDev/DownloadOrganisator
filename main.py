import os
import shutil

# Pfad zum Download-Ordner
download_path = os.path.expanduser("~/Downloads")

# Alle Dateien im Download-Ordner auflisten
files = os.listdir(download_path)

# Jede Datei durchgehen
for file in files:
    # Dateinamen und Erweiterungen trennen
    name, ext = os.path.splitext(file)
    # Wenn es eine Erweiterung gibt
    if ext:
        # Zielordner basierend auf der Erweiterung festlegen
        folder_path = os.path.join(download_path, ext.lstrip('.').upper())
        # Wenn der Zielordner nicht existiert, erstelle ihn
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # Verschiebe die Datei in den Zielordner
        shutil.move(os.path.join(download_path, file), os.path.join(folder_path, file))

print("Dateien erfolgreich organisiert.")
