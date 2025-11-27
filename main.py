#!/usr/bin/env python3
"""
Download Organizer - Organisiert Dateien im Download-Ordner nach Dateierweiterungen
"""
import os
import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, Set

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kategorie-Mapping für bessere Organisation
FILE_CATEGORIES: Dict[str, Set[str]] = {
    'Bilder': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'},
    'Dokumente': {'pdf', 'doc', 'docx', 'txt', 'odt', 'rtf', 'tex', 'md'},
    'Tabellen': {'xls', 'xlsx', 'csv', 'ods'},
    'Präsentationen': {'ppt', 'pptx', 'odp'},
    'Videos': {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'},
    'Audio': {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'},
    'Archive': {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'},
    'Programme': {'exe', 'msi', 'dmg', 'pkg', 'deb', 'rpm', 'AppImage'},
    'Code': {'py', 'js', 'java', 'c', 'cpp', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'html', 'css'},
}


def get_category_for_extension(ext: str) -> str:
    """
    Bestimmt die Kategorie für eine Dateierweiterung

    Args:
        ext: Dateierweiterung (ohne Punkt)

    Returns:
        Kategoriename oder die Erweiterung in Großbuchstaben
    """
    ext_lower = ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext_lower in extensions:
            return category
    return ext.upper()


def get_unique_filename(target_path: Path) -> Path:
    """
    Generiert einen eindeutigen Dateinamen falls die Datei bereits existiert

    Args:
        target_path: Ziel-Dateipfad

    Returns:
        Eindeutiger Dateipfad
    """
    if not target_path.exists():
        return target_path

    base = target_path.stem
    ext = target_path.suffix
    parent = target_path.parent
    counter = 1

    while True:
        new_path = parent / f"{base}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def organize_downloads(download_path: str, use_categories: bool = True, dry_run: bool = False) -> None:
    """
    Organisiert Dateien im Download-Ordner

    Args:
        download_path: Pfad zum Download-Ordner
        use_categories: Ob kategoriebasierte Organisation verwendet werden soll
        dry_run: Wenn True, werden keine Dateien verschoben, nur angezeigt
    """
    download_dir = Path(download_path).expanduser()

    if not download_dir.exists():
        logger.error(f"Download-Ordner existiert nicht: {download_dir}")
        return

    if not download_dir.is_dir():
        logger.error(f"Pfad ist kein Ordner: {download_dir}")
        return

    files_moved = 0
    files_skipped = 0

    logger.info(f"Organisiere Dateien in: {download_dir}")
    if dry_run:
        logger.info("DRY RUN - Keine Dateien werden verschoben")

    try:
        for item in download_dir.iterdir():
            # Nur Dateien verarbeiten, keine Ordner
            if not item.is_file():
                continue

            # Dateien ohne Erweiterung überspringen
            if not item.suffix:
                logger.debug(f"Überspringe Datei ohne Erweiterung: {item.name}")
                files_skipped += 1
                continue

            # Kategorie/Ordner bestimmen
            ext = item.suffix.lstrip('.')
            if use_categories:
                folder_name = get_category_for_extension(ext)
            else:
                folder_name = ext.upper()

            target_folder = download_dir / folder_name

            # Zielordner erstellen falls nötig
            if not dry_run and not target_folder.exists():
                target_folder.mkdir(parents=True)
                logger.info(f"Ordner erstellt: {folder_name}")

            # Zieldatei mit Konfliktbehandlung
            target_file = target_folder / item.name
            if target_file.exists():
                target_file = get_unique_filename(target_file)
                logger.warning(f"Dateikonflikt - umbenannt zu: {target_file.name}")

            # Datei verschieben
            try:
                if dry_run:
                    logger.info(f"[DRY RUN] {item.name} -> {folder_name}/{target_file.name}")
                else:
                    shutil.move(str(item), str(target_file))
                    logger.info(f"{item.name} -> {folder_name}/{target_file.name}")
                files_moved += 1
            except Exception as e:
                logger.error(f"Fehler beim Verschieben von {item.name}: {e}")
                files_skipped += 1

    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        return

    logger.info(f"\nFertig! {files_moved} Dateien verschoben, {files_skipped} übersprungen")


def main():
    """Hauptfunktion mit Argumentverarbeitung"""
    parser = argparse.ArgumentParser(
        description='Organisiert Dateien im Download-Ordner nach Erweiterungen oder Kategorien'
    )
    parser.add_argument(
        '-p', '--path',
        default='~/Downloads',
        help='Pfad zum Download-Ordner (Standard: ~/Downloads)'
    )
    parser.add_argument(
        '--no-categories',
        action='store_true',
        help='Verwende Dateierweiterungen statt Kategorien'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Zeige nur an, was passieren würde, ohne Dateien zu verschieben'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Ausführliche Ausgabe'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    organize_downloads(
        args.path,
        use_categories=not args.no_categories,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
