import os
import shutil
import zipfile
from tkinter import Tk, Button, Toplevel, Event, Label, filedialog, messagebox, Menu, simpledialog, IntVar, Checkbutton, Entry, Frame, W, PhotoImage
from gettext import gettext as _
import sys
import polib
import webbrowser
import socket
import requests
import ctypes
from ctypes import wintypes

def restart_application():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def select_language():
    if os.path.isfile("language.txt"):
        with open("language.txt", "r") as file:
            selected_language = file.readline().strip()  # Lire uniquement la première ligne du fichier
    else:
        selected_language = "en"  # Par défaut, l'anglais est sélectionné

        with open("language.txt", "w") as file:
            file.write(selected_language)

    if selected_language in ["en","fr","al","it","es","ch"]:
        return selected_language
    else:
        return "en"

def select_reformer():
    if os.path.isfile("reformer.txt"):
        with open("reformer.txt", "r") as file:
            selected_reformer = file.readline().strip()  # Lire uniquement la première ligne du fichier
            return selected_reformer
    else:
        selected_reformer = "ressource"  # Par défaut, le ressource pack reformer est sélectionné

        with open("reformer.txt", "w") as file:
            file.write(selected_reformer)

        return selected_reformer

selected_language = select_language()
selected_reformer = select_reformer()
translation_file = f"locales/{selected_language}/LC_MESSAGES/messages.po"
try:
    po = polib.pofile(translation_file, encoding="utf-8")
except OSError:
    try:
        po = polib.pofile("locales/en/LC_MESSAGES/messages.po", encoding="utf-8")
    except OSError:
        messagebox.showerror("Erreor when reading translation file","The application failed to read the default translation file, please contact the support at cubeparticule@gmail.com. The application will stop when ok press.")
        sys.exit(1)

translation = {}
for entry in po.translated_entries():
    translation[entry.msgid] = entry.msgstr

_ = translation.get

def open_mail(event: Event):
    email = "CubeParticule@gmail.com"
    subject = "Demande de suggestion"
    body = "décrivez votre suggestion ici : \n"

    mailto_link = f"mailto:{email}?subject={subject}&body={body}"
    webbrowser.open(mailto_link)

def a_propos():
    root = Tk()
    root.withdraw()

    about_window = Toplevel(root)
    about_window.title(_("À propos"))
    about_window.iconbitmap("img/logo2.ico")

    label = Label(about_window, text=_("Cette application a été codée par MarcusIsLion.\n Tous les droits sont réservés. Voici quelques règles d'utilisation :\n 1) Ne pas revendre l'application ou la partager gratuitement.\n 2) Ne pas modifier l'application.\n 3) Pour toute demande particulière, veuillez envoyer un mail à"), justify="left", padx=10, pady=10)
    label.pack()

    link_label = Label(about_window, text="CubeParticule@gmail.com", fg="blue", cursor="hand2")
    link_label.pack()
    link_label.bind("<Button-1>", open_mail)

    about_window.mainloop()

def open_youtube_video():
    video_url = "https://youtu.be/krvZr3yJUa0"
    webbrowser.open(video_url)

def check_version():

    version_dir = "version"
    version_file = os.path.join(version_dir, "version.txt")

    # Vérification de la version de l'application
    if os.path.isfile(version_file):
        local_version = get_local_version()
        online_version = get_online_version()
        if local_version == online_version:
            messagebox.showinfo(_("Demande de mise à jour"), _("Vous êtes à jour, ne vous inquiétez pas."))
        else:
            message_template = _("Une mise à jour de l'application est disponible. Voulez-vous la télécharger ?\nVersion de votre application : {local_version} \nVersion en ligne actuelle : {online_version}")
            if message_template is not None:
                message = message_template.format(local_version=local_version, online_version=online_version)
            else:
                # Gérer le cas où la traduction échoue et fournir une valeur par défaut
                message = "An update is available."

            if messagebox.askyesno("Mise à jour", message):
                start_update()


def check_version2():
    version_dir = "version"
    version_file = os.path.join(version_dir, "version.txt")

    # Vérification de la version de l'application
    if os.path.isfile(version_file):
        local_version = get_local_version()
        online_version = get_online_version()

        if online_version is None:
            return

        if local_version == online_version:
            h = 1
        else:
            message_template = _("Une mise à jour de l'application est disponible. Voulez-vous la télécharger ?\nVersion de votre application : {local_version} \nVersion en ligne actuelle : {online_version}")
            if message_template is not None:
                message = message_template.format(local_version=local_version, online_version=online_version)
            else:
                # Gérer le cas où la traduction échoue et fournir une valeur par défaut
                message = "An update is available."

            if messagebox.askyesno(_("Mise à jour"), message):
                start_update()

def get_local_version():
    version_dir = "version"
    app_version_file = os.path.join(version_dir, "version.txt")

    if os.path.isfile(app_version_file):
        with open(app_version_file, 'r') as file:
            app_version = file.read().strip()
            if not app_version:
                app_version = 0.0
        return app_version
    else:
        return None

def is_internet_available():
    try:
        # Essayer de se connecter à un site Web Google pour vérifier la connexion Internet
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def get_online_version():
    if not is_internet_available():
        return None

    github_repo = "MarcusIsLion/reformate_pack.mcmeta"  # Remplacez par le nom d'utilisateur et le nom du référentiel GitHub
    app_version_file_path = "version/version.txt"  # Chemin du fichier d'application sur GitHub

    url = f"https://raw.githubusercontent.com/{github_repo}/main/{app_version_file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()

    return None

def start_update():
    python_file = "update/update_Ressource_Pack_Reformer.py"

    def run_as_admin(python_file):
        try:
            # Définition des constantes et des types requis
            HWND = wintypes.HWND
            HINSTANCE = wintypes.HINSTANCE
            LPWSTR = wintypes.LPWSTR
            UINT = wintypes.UINT
            SW_SHOWNORMAL = 1

            # Chargement de la bibliothèque shell32.dll
            shell32 = ctypes.windll.shell32

            # Définition de la structure SHELLEXECUTEINFO
            class SHELLEXECUTEINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("fMask", wintypes.ULONG),
                    ("hwnd", HWND),
                    ("lpVerb", LPWSTR),
                    ("lpFile", LPWSTR),
                    ("lpParameters", LPWSTR),
                    ("lpDirectory", LPWSTR),
                    ("nShow", ctypes.c_int),
                    ("hInstApp", HINSTANCE),
                    ("lpIDList", ctypes.c_void_p),
                    ("lpClass", LPWSTR),
                    ("hkeyClass", wintypes.HKEY),
                    ("dwHotKey", wintypes.DWORD),
                    ("hIcon", wintypes.HANDLE),
                    ("hProcess", wintypes.HANDLE)
                ]

            # Exécution du fichier avec des privilèges élevés
            sei = SHELLEXECUTEINFO()
            sei.cbSize = ctypes.sizeof(sei)
            sei.lpVerb = "runas"
            sei.lpFile = "python"  # Chemin vers l'interpréteur Python
            sei.lpParameters = python_file  # Fichier Python à exécuter
            sei.nShow = SW_SHOWNORMAL

            result = shell32.ShellExecuteExW(ctypes.byref(sei))
            if not result:
                raise ctypes.WinError()

        except Exception as e:
            messagebox.showerror("Erreur lors de l'exécution du programme :", e)

    run_as_admin(python_file)

def app_version():
    local_version = get_local_version()
    online_version = get_online_version()
    # Formatage du message avec les variables
    message = _("Voici la version de votre application : {local_version} \nVoici la version en ligne actuelle : {online_version} ").format(local_version=local_version, online_version=online_version)

    # Affichage de la boîte de dialogue
    messagebox.showinfo(_("App version"), message)

def open_ressource_pack_reformer_window():
    unselect_all_version()
    data_pack_reformer.pack_forget()
    ressource_pack_reformer.pack()
    selected_reformer = "ressource"
    with open("reformer.txt", "w") as file:
            file.write(selected_reformer)

def open_data_pack_reformer_window():
    unselect_all_version2()
    ressource_pack_reformer.pack_forget()
    data_pack_reformer.pack()
    selected_reformer = "data"
    with open("reformer.txt", "w") as file:
            file.write(selected_reformer)

def show_menu():

    def change_language(lang):
        with open("language.txt", "w") as file:
            file.write(lang)
        messagebox.showinfo(_("Langue"), _("La langue a été modifiée. L'application va redémarrer."))
        restart_application()

    menu = Menu(window)

    # Menu Fichier
    file_menu = Menu(menu, tearoff=False)
    file_menu.add_command(label=_("Quitter"), command=window.quit)
    menu.add_cascade(label=_("Option"), menu=file_menu)

    # Menu Application
    file_menu = Menu(menu, tearoff=False)
    file_menu.add_command(label=_("Ressource Pack Reformer"), command=open_ressource_pack_reformer_window)
    file_menu.add_command(label=_("Data Pack Reformer"), command=open_data_pack_reformer_window)
    menu.add_cascade(label=_("Application"), menu=file_menu)

    # Menu Langue
    language_menu = Menu(menu, tearoff=False)
    language_menu.add_command(label="Français", command=lambda: change_language("fr"))
    language_menu.add_command(label="English", command=lambda: change_language("en"))
    language_menu.add_command(label="Italiano", command=lambda: change_language("it"))
    language_menu.add_command(label="Español", command=lambda: change_language("es"))
    language_menu.add_command(label="Deutch", command=lambda: change_language("al"))
    language_menu.add_command(label="中文", command=lambda: change_language("ch"))
    menu.add_cascade(label=_("Langue"), menu=language_menu)

    # Afficher le menu
    about_menu = Menu(menu, tearoff=False)
    about_menu.add_command(label=_("À propos"), command=a_propos)
    online_version = get_online_version()

    if online_version is not None:
        about_menu.add_command(label=_("Vidéo Tutoriel"), command=open_youtube_video)
        about_menu.add_command(label=_("App version"), command=app_version)
        about_menu.add_command(label=_("Rechercher une mise à jour"), command=check_version)
    else:
        about_menu.add_command(label=_("Pas de connexion internet !"), background="red")
    menu.add_cascade(label=_("Aide"), menu=about_menu)

    window.config(menu=menu)

# Fonction pour modifier le fichier pack.mcmeta avec la nouvelle valeur de pack_format
def modify_pack_format(file_path, pack_format):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if 'pack_format' in lines[i]:
            lines[i] = '    "pack_format": ' + str(pack_format) + ',\n'

    with open(file_path, 'w') as f:
        f.writelines(lines)

def export_zip(source_folder, destination_folder, pack_name):
    destination_path = os.path.join(destination_folder, pack_name + ".zip")

    with zipfile.ZipFile(destination_path, 'w') as zipf:
        # Copier le contenu du dossier "assets" dans l'archive
        for foldername, subfolders, filenames in os.walk(os.path.join(source_folder, "assets")):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                relpath = os.path.relpath(filepath, source_folder)
                zipf.write(filepath, relpath)

        # Ajouter les fichiers pack.mcmeta et pack.png à l'archive
        zipf.write(os.path.join(source_folder, "pack.mcmeta"), "pack.mcmeta")
        zipf.write(os.path.join(source_folder, "pack.png"), "pack.png")

class CustomEntryDialog(simpledialog.Dialog):
    entry_text = None  # Variable de classe pour stocker le texte de l'entrée

    def __init__(self, parent, title=None, text=None, suffix_button_text=None, suffix_button_command=None, selected_folder=None):
        self.text = text
        self.suffix_button_text = suffix_button_text
        self.suffix_button_command = suffix_button_command
        self.selected_folder = selected_folder
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        if self.text:
            Label(master, text=self.text).grid(row=0, column=0, columnspan=3, sticky="w")

        self.entry = Entry(master)
        self.entry.grid(row=1, column=0, padx=10, pady=5, sticky="we")

        if self.selected_folder:
            self.entry.insert(0, self.selected_folder)  # Insère le nom du dossier sélectionné

        if self.suffix_button_text and self.suffix_button_command:
            suffix_button = Button(master, text=self.suffix_button_text)
            suffix_button.grid(row=1, column=1, padx=5, pady=5)
            suffix_button.config(command=lambda: self.suffix_button_command(self.entry))

    def apply(self):
        self.result = self.entry.get()

    @staticmethod
    def suffix_button_command(entry):
        if entry.get():
            entry.insert("end", "_{version}")
        else:
            entry.insert("end", "{version}")

# Fonction pour gérer le processus d'exportation du pack pour les versions sélectionnées
def export_ressource_packs():
    folder_path = filedialog.askdirectory(title=_("Sélectionner le dossier contenant les fichiers pack.mcmeta, pack.png et le dossier assets"))

    if not folder_path:
        return

    # Vérifier si les fichiers requis existent dans le dossier spécifié
    pack_mcmeta_path = os.path.join(folder_path, "pack.mcmeta")
    pack_png_path = os.path.join(folder_path, "pack.png")
    assets_folder_path = os.path.join(folder_path, "assets")

    if not (os.path.isfile(pack_mcmeta_path) and os.path.isfile(pack_png_path) and os.path.isdir(assets_folder_path)):
        status_label.config(text=_("Erreur : Les fichiers ou dossiers requis n'ont pas été trouvés dans le dossier spécifié."))
        return

    # Récupérer le nom du fichier à partir du chemin complet
    export_filename = os.path.basename(folder_path)

    # Création de la boîte de dialogue CustomEntryDialog avec le nom du fichier
    dialog = CustomEntryDialog(window,
                               title=_("Nom de l'export"),
                               text=_("Entrez le nom de votre ressource pack (cliquez sur 'version' pour inscrire la version automatiquement lors de l'export) :"),
                               suffix_button_text="version",
                               suffix_button_command=CustomEntryDialog.suffix_button_command,
                               selected_folder=export_filename)

    # Récupération du résultat de la boîte de dialogue
    export_name = dialog.result

    if not export_name:
        return

    selected_versions = []
    for i, checkbox_var in enumerate(version_checkboxes):
        if checkbox_var.get() == 1:
            selected_versions.append(pack_format_int_ressource_pack[i])

    if len(selected_versions) == 0:
        status_label.config(text=_("Erreur : Aucune version sélectionnée."))
        return

    # Créer le dossier "Export" dans le dossier sélectionné
    export_folder = os.path.join(folder_path, "Export")
    # Vérifier si le dossier "Export" existe déjà
    if os.path.exists(export_folder):
    # Supprimer le dossier "Export" et son contenu récursivement
        shutil.rmtree(export_folder)
    os.makedirs(export_folder, exist_ok=True)

    # Modifier et exporter le pack pour les versions sélectionnées
    for version in selected_versions:
        # Modifier le pack_format pour la version actuelle
        pack_format = int(version.replace(".", ""))
        modify_pack_format(pack_mcmeta_path, pack_format)

        # Créer un dossier pour la version actuelle dans le dossier "Export"
        version_folder = os.path.join(export_folder, version)
        if os.path.exists(version_folder):
            shutil.rmtree(version_folder)
        os.makedirs(version_folder)

        # Copier les fichiers du pack vers le dossier de destination
        shutil.copy(pack_mcmeta_path, version_folder)
        shutil.copy(pack_png_path, version_folder)
        shutil.copytree(assets_folder_path, os.path.join(version_folder, "assets"),
                        dirs_exist_ok=True)  # Copy existing "assets" folder

        # Exporter le pack au format .zip avec le fichier pack.png et le dossier assets
        export_zip(version_folder, export_folder, export_name.replace("{version}", minecraft_versions_ressource_pack[pack_format_int_ressource_pack.index(version)]))


        # Supprimer le dossier de la version actuelle
        shutil.rmtree(version_folder)

        status_label.config(text=_(f"Le pack pour la version {minecraft_versions_ressource_pack[pack_format_int_ressource_pack.index(version)]} a été exporté avec succès."))

    status_label.config(text=_("Toutes les versions sélectionnées du pack ont été exportées."))

    # Demander à l'utilisateur s'il souhaite ouvrir le dossier d'exportation
    open_export_folder = messagebox.askyesno(_("Exporter les packs"),
                                             _("L'exportation des packs est terminée. Voulez-vous ouvrir le dossier d'exportation ?"))

    if open_export_folder:
        # Ouvrir le dossier d'exportation dans l'explorateur de fichiers Windows
        os.startfile(export_folder)

def export_data_packs():
    folder_path = filedialog.askdirectory(title=_("Sélectionner le dossier contenant les fichiers pack.mcmeta, pack.png et le dossier assets"))

    if not folder_path:
        return

    # Vérifier si les fichiers requis existent dans le dossier spécifié
    pack_mcmeta_path = os.path.join(folder_path, "pack.mcmeta")
    pack_png_path = os.path.join(folder_path, "pack.png")
    assets_folder_path = os.path.join(folder_path, "assets")

    if not (os.path.isfile(pack_mcmeta_path) and os.path.isfile(pack_png_path) and os.path.isdir(assets_folder_path)):
        status_label.config(text=_("Erreur : Les fichiers ou dossiers requis n'ont pas été trouvés dans le dossier spécifié."))
        return

    # Récupérer le nom du fichier à partir du chemin complet
    export_filename = os.path.basename(folder_path)

    # Création de la boîte de dialogue CustomEntryDialog avec le nom du fichier
    dialog = CustomEntryDialog(window,
                               title=_("Nom de l'export"),
                               text=_("Entrez le nom de votre data pack (cliquez sur 'version' pour inscrire la version automatiquement lors de l'export) :"),
                               suffix_button_text="version",
                               suffix_button_command=CustomEntryDialog.suffix_button_command,
                               selected_folder=export_filename)

    # Récupération du résultat de la boîte de dialogue
    export_name = dialog.result

    if not export_name:
        return

    selected_versions2 = []
    for i, checkbox_var2 in enumerate(version_checkboxes2):
        if checkbox_var2.get() == 1:
            selected_versions2.append(pack_format_int_ressource_pack[i])

    if len(selected_versions2) == 0:
        status_label.config(text=_("Erreur : Aucune version sélectionnée."))
        return

    # Créer le dossier "Export" dans le dossier sélectionné
    export_folder = os.path.join(folder_path, "Export")
    # Vérifier si le dossier "Export" existe déjà
    if os.path.exists(export_folder):
    # Supprimer le dossier "Export" et son contenu récursivement
        shutil.rmtree(export_folder)
    os.makedirs(export_folder, exist_ok=True)

    # Modifier et exporter le pack pour les versions sélectionnées
    for version in selected_versions2:
        # Modifier le pack_format pour la version actuelle
        pack_format = int(version.replace(".", ""))
        modify_pack_format(pack_mcmeta_path, pack_format)

        # Créer un dossier pour la version actuelle dans le dossier "Export"
        version_folder = os.path.join(export_folder, version)
        if os.path.exists(version_folder):
            shutil.rmtree(version_folder)
        os.makedirs(version_folder)

        # Copier les fichiers du pack vers le dossier de destination
        shutil.copy(pack_mcmeta_path, version_folder)
        shutil.copy(pack_png_path, version_folder)
        shutil.copytree(assets_folder_path, os.path.join(version_folder, "assets"),
                        dirs_exist_ok=True)  # Copy existing "assets" folder

        # Exporter le pack au format .zip avec le fichier pack.png et le dossier assets
        export_zip(version_folder, export_folder, export_name.replace("{version}", minecraft_versions2[pack_format_int_ressource_pack.index(version)]))


        # Supprimer le dossier de la version actuelle
        shutil.rmtree(version_folder)

        status_label.config(text=_(f"Le pack pour la version {minecraft_versions2[pack_format_int_ressource_pack.index(version)]} a été exporté avec succès."))

    status_label.config(text=_("Toutes les versions sélectionnées du pack ont été exportées."))

    # Demander à l'utilisateur s'il souhaite ouvrir le dossier d'exportation
    open_export_folder = messagebox.askyesno(_("Exporter les packs"),
                                             _("L'exportation des packs est terminée. Voulez-vous ouvrir le dossier d'exportation ?"))

    if open_export_folder:
        # Ouvrir le dossier d'exportation dans l'explorateur de fichiers Windows
        os.startfile(export_folder)

def select_all_versions():
    for checkbox in version_checkboxes:
        checkbox.set(1)

def unselect_all_version():
    for checkbox in version_checkboxes:
        checkbox.set(0)

def select_all_versions2():
    for checkbox2 in version_checkboxes2:
        checkbox2.set(1)

def unselect_all_version2():
    for checkbox2 in version_checkboxes2:
        checkbox2.set(0)

# Créer une fenêtre
window = Tk()
window.title(_("Exportateur de packs Minecraft"))
window.iconbitmap("img/logo2.ico")
show_menu()

check_version2()
ressource_pack_reformer = Frame(window)
status_label = Label(ressource_pack_reformer, text=_("Sélectionnez les versions dans lesquelles vous souhaitez exporter votre pack de texture :"), wraplength=380)
status_label.grid(row=0, column=0, columnspan=5, pady=20)

minecraft_versions_ressource_pack = ["1.6.1-1.8.9", "1.9-1.10.2", "1.11-1.12.2", "1.13-1.14.4", "1.15-1.16.1", "1.16.2-1.16.5", "1.17-1.17.1", "1.18-1.18.2", "1.19-1.19.2", "1.19.3", "1.19.4", "1.20-1.20.1", "1.20.2"]
pack_format_int_ressource_pack = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "12", "13", "15","18"]
version_checkboxes = []

row = 0
col = 0
num_columns = 4

checkbox_frame = Frame(ressource_pack_reformer)
checkbox_frame.grid(row=1, column=0, columnspan=num_columns, padx=10, pady=10)

num_versions = len(minecraft_versions_ressource_pack)
num_rows = (num_versions + num_columns - 1) // num_columns

for i, version in enumerate(minecraft_versions_ressource_pack):
    checkbox_var = IntVar()
    version_checkbox = Checkbutton(checkbox_frame, text=version, variable=checkbox_var)
    version_checkbox.grid(row=row, column=col, sticky=W)
    version_checkboxes.append(checkbox_var)
    col += 1
    if col == num_columns:
        col = 0
        row += 1

select_all_button = Button(ressource_pack_reformer, text=_("Sélectionner toutes les versions."), command=select_all_versions)
select_all_button.grid(row=2, column=1, pady=10)
select_all_button = Button(ressource_pack_reformer, text=_("Désélectionner toutes les versions."), command=unselect_all_version)
select_all_button.grid(row=2, column=2, pady=10)


# Étiquettes et bouton d'exportation
status_label2 = Label(ressource_pack_reformer, text=_("Sélectionnez le dossier contenant 1 dossier ('assets') et 2 fichiers ('pack.mcmeta' & 'pack.PNG') :"), wraplength=380)
status_label2.grid(row=3, column=0, columnspan=num_columns, padx=10, pady=10)

export_button = Button(ressource_pack_reformer, text=_("Choisir le fichier à exporter"), command=export_ressource_packs)
export_button.grid(row=4, column=0, columnspan=num_columns, padx=10, pady=10)

logo = PhotoImage(file="img/logo.png")
label_img = Label(ressource_pack_reformer, image=logo)
label_img.grid(row=5, column=0, columnspan=num_columns, padx=10, pady=10)


data_pack_reformer = Frame(window)


status_label2 = Label(data_pack_reformer, text=_("Sélectionnez les versions dans lesquelles vous souhaitez exporter votre data pack :"), wraplength=380)
status_label2.grid(row=0, column=0, columnspan=5, pady=20)

minecraft_versions2 = ["1.13-1.14.4", "1.15-1.16.1", "1.16.2-1.16.5", "1.17-1.17.1", "1.18-1.18.1", "1.18.2", "1.19-1.19.3", "1.19.4", "1.20-1.20.1", "1.20.2"]
pack_format_int2 = ["4", "5", "6", "7", "8", "9", "10", "12", "15", "18"]
version_checkboxes2 = []

row = 0
col = 0
num_columns = 4

checkbox_frame2 = Frame(data_pack_reformer)
checkbox_frame2.grid(row=1, column=0, columnspan=num_columns, padx=10, pady=10)

num_versions2 = len(minecraft_versions2)
num_rows2 = (num_versions + num_columns - 1) // num_columns

for i, version in enumerate(minecraft_versions2):
    checkbox_var2 = IntVar()
    version_checkbox2 = Checkbutton(checkbox_frame2, text=version, variable=checkbox_var2)
    version_checkbox2.grid(row=row, column=col, sticky=W)
    version_checkboxes2.append(checkbox_var2)
    col += 1
    if col == num_columns:
        col = 0
        row += 1

select_all_button2 = Button(data_pack_reformer, text=_("Sélectionner toutes les versions."), command=select_all_versions2)
select_all_button2.grid(row=2, column=1, pady=10)
select_all_button2 = Button(data_pack_reformer, text=_("Désélectionner toutes les versions."), command=unselect_all_version2)
select_all_button2.grid(row=2, column=2, pady=10)

# Étiquettes et bouton d'exportation
status_label2 = Label(data_pack_reformer, text=_("Sélectionnez le dossier contenant 1 dossier ('assets') et 2 fichiers ('pack.mcmeta' & 'pack.PNG') :"), wraplength=380)
status_label2.grid(row=3, column=0, columnspan=num_columns, padx=10, pady=10)

export_button2 = Button(data_pack_reformer, text=_("Choisir le fichier à exporter"), command=export_data_packs)
export_button2.grid(row=4, column=0, columnspan=num_columns, padx=10, pady=10)
logo2 = PhotoImage(file="img/logo3.png")
label_img2 = Label(data_pack_reformer, image=logo2)
label_img2.grid(row=5, column=0, columnspan=num_columns, padx=10, pady=10)

if selected_reformer == "ressource":
    data_pack_reformer.pack_forget()
    ressource_pack_reformer.pack()
else:
    ressource_pack_reformer.pack_forget()
    data_pack_reformer.pack()

# Lancer la boucle principale de la fenêtre
window.mainloop()
 