import logging

logging.basicConfig(
    filename='iss.log',       # Le fichier de log où les messages seront enregistrés
    level=logging.DEBUG,          # Le niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format du message
    datefmt='%Y-%m-%d %H:%M:%S'    # Format de la date
)

