import subprocess
from pathlib import Path
from datetime import datetime
import sys


# ============================================================
# CONFIGURAZIONE
# ============================================================
#Esempio
#SERVER = r"NB-NPRUNELLA2\SQLEXPRESS"
#DATABASE = "NETPRO-DEMO"
#BACKUP_DIR = Path(r"C:\BackupSQL")
#BACKUP_LOG_DIR = Path(r"C:\LogBackupSQL")
#SQLCMD = r"C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE"
#LOG_FILE = BACKUP_LOG_DIR / "backup.log"

SERVER = r"FAGSRVMES\SQLEXPRESS"
DATABASE = "NETPRO"
BACKUP_DIR = Path(r"C:\BackupSQL")
BACKUP_LOG_DIR = Path(r"C:\LogBackupSQL")
SQLCMD = r"C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE"
LOG_FILE = BACKUP_LOG_DIR / "backup.log"


# ============================================================
# FUNZIONE SCRITTURA LOG
# ============================================================

def scrivi_log(messaggio):
    """Scrive un messaggio nel file di log con data e ora."""

    data_ora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    riga = f"[{data_ora}] {messaggio}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(riga)


# ============================================================
# CREAZIONE CARTELLA
# ============================================================

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# NOME FILE BACKUP
# ============================================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_file = BACKUP_DIR / f"{DATABASE}_FULL_{timestamp}.bak"


# ============================================================
# COMANDO SQL
# ============================================================

sql = (
    f"BACKUP DATABASE [{DATABASE}] "
    f"TO DISK = N'{backup_file}' "
    f"WITH INIT, CHECKSUM, STATS = 10;"
)


# ============================================================
# INIZIO
# ============================================================

print("=" * 60)
print("BACKUP SQL SERVER")
print("=" * 60)

print(f"Server   : {SERVER}")
print(f"Database : {DATABASE}")
print(f"File     : {backup_file}")
print()

scrivi_log("============================================================")
scrivi_log("AVVIO BACKUP")
scrivi_log(f"Server: {SERVER}")
scrivi_log(f"Database: {DATABASE}")
scrivi_log(f"File: {backup_file}")


try:

    print("Avvio backup...")
    print()

    # ========================================================
    # ESECUZIONE SQLCMD
    # ========================================================

    result = subprocess.run(
        [
            SQLCMD,
            "-S", SERVER,
            "-E",
            "-Q", sql
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


    # ========================================================
    # OUTPUT SQLCMD
    # ========================================================

    if result.stdout:
        print(result.stdout)

        # Salviamo anche l'output SQL nel log
        scrivi_log(result.stdout.strip())


    if result.stderr:
        print("MESSAGGI:")
        print(result.stderr)

        scrivi_log("MESSAGGI SQLCMD:")
        scrivi_log(result.stderr.strip())


    # ========================================================
    # CONTROLLO CODICE RITORNO
    # ========================================================

    if result.returncode != 0:

        print()
        print("=" * 60)
        print("ERRORE DURANTE IL BACKUP")
        print("=" * 60)

        print(f"Codice errore: {result.returncode}")

        scrivi_log(
            f"BACKUP FALLITO - Codice errore: {result.returncode}"
        )

        sys.exit(result.returncode)


    # ========================================================
    # CONTROLLO FILE
    # ========================================================

    if not backup_file.exists():

        print()
        print("=" * 60)
        print("ERRORE")
        print("=" * 60)

        print("Il backup è terminato ma il file non esiste:")
        print(backup_file)

        scrivi_log(
            "ERRORE: backup terminato ma file .bak non trovato"
        )

        sys.exit(1)


    # ========================================================
    # DIMENSIONE FILE
    # ========================================================

    file_size = backup_file.stat().st_size

    file_size_mb = file_size / (1024 * 1024)


    # ========================================================
    # SUCCESSO
    # ========================================================

    print()
    print("=" * 60)
    print("BACKUP COMPLETATO CON SUCCESSO")
    print("=" * 60)

    print(f"File      : {backup_file}")
    print(f"Dimensione: {file_size_mb:.2f} MB")
    print(
        f"Data/Ora  : "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )


    # ========================================================
    # LOG SUCCESSO
    # ========================================================

    scrivi_log("BACKUP COMPLETATO CON SUCCESSO")
    scrivi_log(f"File: {backup_file}")
    scrivi_log(f"Dimensione: {file_size_mb:.2f} MB")

    scrivi_log("FINE BACKUP")
    scrivi_log("============================================================")


except FileNotFoundError:

    print()
    print("=" * 60)
    print("ERRORE")
    print("=" * 60)

    print("sqlcmd.exe non è stato trovato:")
    print(SQLCMD)

    scrivi_log("ERRORE: sqlcmd.exe non trovato")
    scrivi_log(f"Percorso cercato: {SQLCMD}")

    sys.exit(1)


except Exception as e:

    print()
    print("=" * 60)
    print("ERRORE IMPREVISTO")
    print("=" * 60)

    print(str(e))

    scrivi_log("ERRORE IMPREVISTO")
    scrivi_log(str(e))

    sys.exit(1)

