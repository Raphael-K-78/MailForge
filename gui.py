import html
from pathlib import Path

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, ttk, messagebox

from mailforge.utils.mailer import send
from mailforge.utils.template import get_templates, get_template_fields
from mailforge.utils.config import TEMPLATES_DIR
from mailforge.utils.logger import logger


class RichField:
    """
    Champ de saisie qui démarre en simple ligne (Entry) et peut s'étendre,
    via le bouton crayon, en zone de texte multi-lignes avec mise en forme
    (gras, souligné, surligné, petit texte, exposant).
    """

    # (tag, icône bouton, config du bouton, wrapper HTML)
    _STYLES = [
        ("bold", "B", {"font_weight": "bold"}, "strong"),
        ("underline", "U", {"font_underline": True}, "u"),
        ("highlight", "🖍", {"bg": "#fff59d"}, "mark"),
        ("small", "A⁻", {"font_size_delta": -2}, "small"),
        ("superscript", "x²", {"font_size_delta": -2, "offset": 6}, "sup"),
    ]

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.expanded = False
        self.text = None
        self.text_container = None

        self.top_row = ttk.Frame(self.frame)
        self.top_row.pack(side="top", fill="x")

        self.var = tk.StringVar()
        self.entry = ttk.Entry(self.top_row, textvariable=self.var)
        self.entry.pack(side="left", fill="x", expand=True)

        self.toggle_btn = ttk.Button(
            self.top_row, text="✎", width=3, command=self._toggle
        )
        self.toggle_btn.pack(side="left", padx=(4, 0))

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def _toggle(self):
        if self.expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        current = self.var.get()

        self.entry.pack_forget()

        self.text_container = ttk.Frame(self.frame)
        self.text_container.pack(side="top", fill="x", pady=(4, 0))

        toolbar = ttk.Frame(self.text_container)
        toolbar.pack(fill="x")

        self.text = tk.Text(self.text_container, height=4, width=1, wrap="word")

        base_font = tkfont.Font(font=self.text.cget("font"))

        for tag, icon, style, _ in self._STYLES:
            self._add_style_button(toolbar, tag, icon, style)

            tag_font = base_font.copy()
            tag_font.configure(
                weight="bold" if style.get("font_weight") else tag_font.cget("weight"),
                underline=style.get("font_underline", False),
                size=base_font.cget("size") + style.get("font_size_delta", 0)
            )

            self.text.tag_configure(
                tag,
                font=tag_font,
                background=style.get("bg", ""),
                offset=style.get("offset", 0)
            )

        self.text.pack(fill="x", expand=True, pady=(2, 0))
        self.text.insert("1.0", current)

        self.expanded = True
        self.toggle_btn.configure(text="↩")

    def _add_style_button(self, parent, tag, icon, style):
        button_font = ("Segoe UI", 9, "bold" if style.get("font_weight") else "normal")

        btn = tk.Button(
            parent,
            text=icon,
            width=3,
            font=button_font,
            underline=0 if style.get("font_underline") else -1,
            bg=style.get("bg", "SystemButtonFace"),
            relief="raised",
            command=lambda: self._toggle_tag(tag)
        )
        btn.pack(side="left", padx=(0, 2))

    def _collapse(self):
        self.var.set(self.text.get("1.0", "end-1c"))

        self.text_container.destroy()
        self.text_container = None
        self.text = None

        self.entry.pack(side="left", fill="x", expand=True, before=self.toggle_btn)

        self.expanded = False
        self.toggle_btn.configure(text="✎")

    def _toggle_tag(self, tag):
        try:
            start, end = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            return

        if tag in self.text.tag_names(start):
            self.text.tag_remove(tag, start, end)
        else:
            self.text.tag_add(tag, start, end)

    def get_value(self):
        if not self.expanded:
            return self.var.get()

        return self._render_html()

    def _char_offset(self, index):
        result = self.text.count("1.0", index, "chars")
        return result[0] if result else 0

    def _active_tags_at(self, char_index):
        names = self.text.tag_names(f"1.0+{char_index}c")
        return {tag for tag, *_ in self._STYLES if tag in names}

    def _wrap(self, element, style, chunk):
        if element == "mark":
            return f'<span style="background-color:{style["bg"]};">{chunk}</span>'

        return f"<{element}>{chunk}</{element}>"

    def _render_html(self):
        content = self.text.get("1.0", "end-1c")
        n = len(content)

        pieces = []
        i = 0

        while i < n:
            current_tags = self._active_tags_at(i)

            j = i
            while j < n and self._active_tags_at(j) == current_tags:
                j += 1

            chunk = html.escape(content[i:j])

            for tag, _, style, element in self._STYLES:
                if tag in current_tags:
                    chunk = self._wrap(element, style, chunk)

            pieces.append(chunk)
            i = j

        return "".join(pieces).replace("\n", "<br>\n")


class MailApp(tk.Tk):
    """
    Interface graphique reprenant le comportement de la console (main.py) :
    Sujet -> Nom expéditeur -> Identifiant du mail -> Destinataire
    -> Template -> Champs dynamiques -> Envoi.
    """

    def __init__(self):
        super().__init__()

        self.title("Envoi de mail")
        self.geometry("520x720")
        self.resizable(False, False)

        self.templates = get_templates(TEMPLATES_DIR)
        self.field_vars = {}
        self.attachments = []

        self._build_static_fields()
        self._build_template_selector()
        self._build_dynamic_fields_area()
        self._build_attachments_area()
        self._build_send_button()
        self._build_status_bar()

        if not self.templates:
            messagebox.showerror(
                "Erreur",
                f"Aucun template trouvé dans : {TEMPLATES_DIR}"
            )
            logger.error(f"Aucun template trouvé dans : {TEMPLATES_DIR}")

    # Construction de l'interface

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

        window_id = canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(window_id, width=e.width)
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_attachments_area(self):
        outer = ttk.LabelFrame(self, text="Pièces jointes", padding=10)
        outer.pack(fill="x", padx=10, pady=(0, 10))

        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(0, 6))

        ttk.Button(
            buttons,
            text="Ajouter des fichiers...",
            command=self._on_add_attachments
        ).pack(side="left")

        ttk.Button(
            buttons,
            text="Retirer la sélection",
            command=self._on_remove_attachment
        ).pack(side="left", padx=(6, 0))

        list_frame = ttk.Frame(outer)
        list_frame.pack(fill="x")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.attachments_list = tk.Listbox(
            list_frame,
            height=5,
            selectmode="extended",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.attachments_list.yview)

        self.attachments_list.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_add_attachments(self):
        paths = filedialog.askopenfilenames(title="Choisir des pièces jointes")

        for path in paths:
            path = Path(path)

            if path not in self.attachments:
                self.attachments.append(path)
                self.attachments_list.insert("end", path.name)

        if paths:
            logger.info(f"{len(paths)} pièce(s) jointe(s) ajoutée(s)")

    def _on_remove_attachment(self):
        selection = list(self.attachments_list.curselection())

        for index in reversed(selection):
            self.attachments_list.delete(index)
            del self.attachments[index]

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

    # Comportement
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

            ttk.Label(row, text=f"{field} :", width=20).pack(side="left", anchor="n")

            rich_field = RichField(row)
            rich_field.pack(side="left", fill="x", expand=True)

            self.field_vars[field] = rich_field

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
            field: rich_field.get_value()
            for field, rich_field in self.field_vars.items()
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
            template_data=template_data,
            attachments=self.attachments
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
