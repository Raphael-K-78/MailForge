import tkinter as tk
from tkinter import ttk, messagebox

from mailforge.utils.mailer import send
from mailforge.utils.template import get_templates, get_template_fields
from mailforge.utils.config import TEMPLATES_DIR
from mailforge.utils.logger import logger


class MailApp(tk.Tk):
    """
    Interface graphique reprenant le comportement de la console (main.py) :
    Sujet -> Nom expéditeur -> Identifiant du mail -> Destinataire
    -> Template -> Champs dynamiques -> Envoi.
    """

    def __init__(self):
        super().__init__()

        self.title("Envoi de mail")
        self.geometry("520x600")
        self.resizable(False, False)

        self.templates = get_templates(TEMPLATES_DIR)
        self.field_vars = {}

        self._build_static_fields()
        self._build_template_selector()
        self._build_dynamic_fields_area()
        self._build_send_button()
        self._build_status_bar()

        if not self.templates:
            messagebox.showerror(
                "Erreur",
                f"Aucun template trouvé dans : {TEMPLATES_DIR}"
            )
            logger.error(f"Aucun template trouvé dans : {TEMPLATES_DIR}")

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------

    def _build_static_fields(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="x")

        self.subject_var = tk.StringVar()
        self.sender_name_var = tk.StringVar()
        self.sender_email_var = tk.StringVar()
        self.recipient_var = tk.StringVar()

        rows = [
            ("Sujet du mail :", self.subject_var),
            ("Nom de l'expéditeur :", self.sender_name_var),
            ("Identifiant personnel du mail :", self.sender_email_var),
            ("Destinataire du mail :", self.recipient_var),
        ]

        for i, (label, var) in enumerate(rows):
            ttk.Label(frame, text=label).grid(
                row=i, column=0, sticky="w", pady=4
            )
            ttk.Entry(frame, textvariable=var, width=40).grid(
                row=i, column=1, sticky="ew", pady=4
            )

        frame.columnconfigure(1, weight=1)

    def _build_template_selector(self):
        frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame.pack(fill="x")

        ttk.Label(frame, text="Template :").grid(row=0, column=0, sticky="w")

        noms = [
            fichier.stem.replace("_", " ")
            for fichier in self.templates
        ]

        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(
            frame,
            textvariable=self.template_var,
            values=noms,
            state="readonly",
            width=37
        )
        self.template_combo.grid(row=0, column=1, sticky="ew")
        self.template_combo.bind(
            "<<ComboboxSelected>>",
            self._on_template_selected
        )

        frame.columnconfigure(1, weight=1)

    def _build_dynamic_fields_area(self):
        outer = ttk.LabelFrame(self, text="Données du template", padding=10)
        outer.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)

        self.fields_frame = ttk.Frame(canvas)
        self.fields_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_send_button(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="x")

        ttk.Button(
            frame,
            text="Envoyer",
            command=self._on_send
        ).pack(fill="x")

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Prêt.")

        ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            padding=(10, 4)
        ).pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Comportement
    # ------------------------------------------------------------------

    def _on_template_selected(self, event=None):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        self.field_vars = {}

        template_file = self._get_selected_template()

        if template_file is None:
            return

        logger.info(f"Template sélectionné : {template_file.name}")

        fields = get_template_fields(template_file)

        if not fields:
            logger.info("Aucun champ dynamique dans le template")
            ttk.Label(
                self.fields_frame,
                text="Aucun champ dynamique pour ce template."
            ).pack(anchor="w")
            return

        for field in fields:
            row = ttk.Frame(self.fields_frame)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=f"{field} :", width=20).pack(side="left")

            var = tk.StringVar()
            ttk.Entry(row, textvariable=var).pack(
                side="left", fill="x", expand=True
            )

            self.field_vars[field] = var

    def _get_selected_template(self):
        index = self.template_combo.current()

        if index < 0:
            return None

        return self.templates[index]

    def _on_send(self):
        subject = self.subject_var.get().strip()
        sender_name = self.sender_name_var.get().strip()
        sender_email = self.sender_email_var.get().strip()
        recipient = self.recipient_var.get().strip()

        if not all([subject, sender_name, sender_email, recipient]):
            messagebox.showwarning(
                "Champs manquants",
                "Merci de remplir Sujet, Nom, Identifiant et Destinataire."
            )
            return

        template_file = self._get_selected_template()

        if template_file is None:
            messagebox.showwarning(
                "Template manquant",
                "Merci de sélectionner un template."
            )
            return

        template_data = {
            field: var.get()
            for field, var in self.field_vars.items()
        }

        logger.info(f"Sujet : {subject}")
        logger.info(f"Nom de l'expéditeur : {sender_name}")
        logger.info(f"Identifiant personnel du mail : {sender_email}")
        logger.info(f"Destinataire : {recipient}")

        self.status_var.set("Envoi en cours...")
        self.update_idletasks()

        result = send(
            subject=subject,
            sender_name=sender_name,
            sender_email=sender_email,
            recipient=recipient,
            template=template_file,
            template_data=template_data
        )

        if result is not None:
            self.status_var.set(f"Mail envoyé à {recipient}.")
            messagebox.showinfo("Succès", f"Mail envoyé à {recipient}.")
        else:
            self.status_var.set("Échec de l'envoi. Voir logs/app.log.")
            messagebox.showerror(
                "Erreur",
                "Échec de l'envoi. Voir logs/app.log pour le détail."
            )


if __name__ == "__main__":
    logger.info("=== Démarrage de l'interface graphique ===")
    app = MailApp()
    app.mainloop()
