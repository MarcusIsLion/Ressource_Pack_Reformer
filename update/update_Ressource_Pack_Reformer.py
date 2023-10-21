import os
import urllib.request
import subprocess
from tkinter import *
from tkinter import ttk, messagebox
from time import sleep
import requests
import ctypes
from ctypes import wintypes
import sys

def close_exe(exe_path):
    message_label.config(text="Closing main app.")
    root.update()
    # Attendre un court délai avant de fermer le processus
    sleep(1)
    # Obtenir le nom de l'exécutable à partir du chemin complet
    exe_name = os.path.basename(exe_path)
    # Fermer le processus exécutable
    subprocess.run(["taskkill", "/F", "/IM", exe_name])
    message_label.config(text="App closed.")
    root.update()

def download_file(url, destination):
    file_name = url.split("/")[-1]
    file_path = os.path.join(destination, file_name)
    file_path = file_path.strip()  # Supprimer les espaces et les caractères de nouvelle ligne du chemin d'accès
    urllib.request.urlretrieve(url, file_path)

def get_local_key_version():
    app_version_file = "update/lisence_update_key.txt"
    if os.path.isfile(app_version_file):
        with open(app_version_file, 'r') as file:
            app_version = file.read().strip()
            if not app_version:
                app_version = "0.0"
        get_online_key_version(app_version)
    else:
        message = "Please make sure the lisence key is currently in here : \n \"update/lisence_update_key.txt\" \nAnd restart the main app, to reinstall the update."
        messagebox.showerror("App version", message)
        return None

def get_online_key_version(app_version):
    github_repo = "MarcusIsLion/reformate_pack.mcmeta"  # Remplacez par le nom d'utilisateur et le nom du référentiel GitHub
    app_version_file_path = "update/lisence_update_key.txt"  # Chemin du fichier d'application sur GitHub

    url = f"https://raw.githubusercontent.com/{github_repo}/main/{app_version_file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        if response.text.strip() == app_version:
            download_all_files()
    return None

def download_all_files():
    base_url = "https://raw.githubusercontent.com/MarcusIsLion/reformate_pack.mcmeta/main"
    to_download_file = "To_Download.txt"

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Utilisez le répertoire parent

    message_label.config(text="Downloading \"To_Download.txt\" file.")
    root.update()
    sleep(0.5)
    download_file("https://raw.githubusercontent.com/MarcusIsLion/reformate_pack.mcmeta/main/update/To_Download.txt", parent_dir)
    sleep(0.5)
    message_label.config(text="Downloading complete and searching for more download.")
    root.update()
    to_download_path = os.path.join(parent_dir, to_download_file)  # Chemin absolu du fichier à télécharger
    message_label.config(text="Downloading all files.")
    root.update()
    if not os.path.exists(to_download_path):
        message_label.config(text=f"File '{to_download_file}' not found.")
        root.update()
        return

    with open(to_download_path, 'r') as file:
        files_to_download = [line.strip('"') for line in file]

    total_files = len(files_to_download)
    files_remaining = total_files

    progress_label.config(text=f"Files remaining: {files_remaining}/{total_files}")
    progress_label.grid(row=1, column=2, pady=10)
    remaining_files_label.config(text="Remaining name files: \n" + " ".join(files_to_download))
    remaining_files_label.grid(row=3, column=2, pady=10)
    root.update()

    for index, file in enumerate(files_to_download):
        file_url = "{}/{}".format(base_url, file)
        destination = os.path.join(parent_dir, os.path.dirname(file))
        print("je suis l'erreur", file_url , destination)
        download_file(file_url, destination)
        files_remaining -= 1
        progress_var.set((index + 1) / total_files * 100)
        progress_label.config(text=f"Files remaining: {files_remaining}/{total_files}")
        remaining_files_label.config(text="Remaining name files: \n" + " ".join(files_to_download[index+1:]))
        root.update()
        sleep(1)

    os.remove(to_download_path)
    message_label.config(text="Downloading completed.")
    root.update()
    sleep(1)
    root.destroy()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def start_main_app():
    if messagebox.askyesno("Restarting Ressource Pack Reformer ?", "Do you want to restart the Ressource Pack Reformer app ?"):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exe_file = os.path.join(parent_dir, "Ressource_Pack_Reformer.exe")


        def run_as_admin2(exe_file):
            try:
                # Définition des constantes et des types requis
                HWND = ctypes.wintypes.HWND
                HINSTANCE = ctypes.wintypes.HINSTANCE
                LPWSTR = ctypes.wintypes.LPWSTR
                UINT = ctypes.wintypes.UINT
                SW_SHOWNORMAL = 1

                # Chargement de la bibliothèque shell32.dll
                shell32 = ctypes.windll.shell32

                # Définition de la structure SHELLEXECUTEINFO
                class SHELLEXECUTEINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", ctypes.wintypes.DWORD),
                        ("fMask", ctypes.wintypes.ULONG),
                        ("hwnd", HWND),
                        ("lpVerb", LPWSTR),
                        ("lpFile", LPWSTR),
                        ("lpParameters", LPWSTR),
                        ("lpDirectory", LPWSTR),
                        ("nShow", ctypes.c_int),
                        ("hInstApp", HINSTANCE),
                        ("lpIDList", ctypes.c_void_p),
                        ("lpClass", LPWSTR),
                        ("hkeyClass", ctypes.wintypes.HKEY),
                        ("dwHotKey", ctypes.wintypes.DWORD),
                        ("hIcon", ctypes.wintypes.HANDLE),
                        ("hProcess", ctypes.wintypes.HANDLE)
                    ]

                # Exécution du fichier avec des privilèges élevés
                sei = SHELLEXECUTEINFO()
                sei.cbSize = ctypes.sizeof(sei)
                sei.lpVerb = "runas"
                sei.lpFile = exe_file
                sei.nShow = SW_SHOWNORMAL

                result = shell32.ShellExecuteExW(ctypes.byref(sei))

            except Exception as e:
                messagebox.showerror("Error", str(e))
        run_as_admin2(exe_file)

# Création de la fenêtre racine
root = Tk()
root.title("Updating \"Ressource Pack Reformer\"")

# Création des labels
message_label = Label(root, text="Searching task...")
message_label.grid(row=0, column=2, pady=10)

progress_label = Label(root, text="Ignition...")
remaining_files_label = Label(root, text="Searching file name...")

# Création de la barre de progression
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)

# Positionnement des éléments dans la grille
message_label.grid(row=0, column=2, pady=10)
progress_label.grid(row=1, column=2, pady=10)
progress_bar.grid(row=2, column=2, pady=10)
remaining_files_label.grid(row=3, column=2, pady=10)

# Fermeture du fichier exécutable
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
exe_file = os.path.join(parent_dir, "Ressource_Pack_Reformer.exe")
close_exe(exe_file)
sleep(0.5)
message_label.config(text="Checking license key.")
root.update()
#download_all_files()
get_local_key_version()
# Démarrage de la boucle principale de l'interface graphique
root.mainloop()
start_main_app()
