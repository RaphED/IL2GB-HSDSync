import os

# SSLKEYLOGFILE asks Python's ssl module to write the TLS session keys to a file (a debugging feature).
# Some software sets it machine wide to a path normal programs cannot open, e.g. \\?\Volume{...}\virtual_file.log:
# urllib3 then fails with PermissionError when requests is imported, and HSDSync crashes at startup.
# This must run before anything imports requests.
def dropUnusableSslKeyLogFile():
    keyLogFile = os.environ.get("SSLKEYLOGFILE")
    if not keyLogFile:
        return None
    try:
        open(keyLogFile, "a").close()
        return None
    except OSError:
        os.environ.pop("SSLKEYLOGFILE", None)
        return keyLogFile
