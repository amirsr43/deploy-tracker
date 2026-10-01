import customtkinter as ctk
from tkinter import messagebox

from models import (
    get_projects,
    create_project,
    update_project,
    delete_project
)

class ProjectsView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_project_list()

        self.load_projects()

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(30, 20)
        )

        heading = ctk.CTkFrame(header, fg_color="transparent")
        heading.pack(side="left")
        ctk.CTkLabel(
            heading,
            text="Projects",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            heading,
            text="Manage your projects and repository details.",
            font=("Segoe UI", 13),
            text_color=("gray40", "gray70")
        ).pack(anchor="w", pady=(3, 0))

        add_button = ctk.CTkButton(
            header,
            text="+ New project",
            width=130,
            command=self.open_add_form
        )

        add_button.pack(side="right")

    def create_project_list(self):

        self.project_list = ctk.CTkScrollableFrame(self)

        self.project_list.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 30)
        )

    def load_projects(self):

        for widget in self.project_list.winfo_children():
            widget.destroy()

        projects = get_projects()

        if not projects:

            empty_label = ctk.CTkLabel(
                self.project_list,
                text="No projects yet."
            )

            empty_label.pack(pady=40)

            return

        for project in projects:
            self.create_project_card(project)

    def create_project_card(self, project):

        card = ctk.CTkFrame(
            self.project_list
        )

        card.pack(
            fill="x",
            pady=6
        )

        info = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        info.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=12
        )

        name = ctk.CTkLabel(
            info,
            text=project["name"],
            font=("Segoe UI", 16, "bold")
        )

        name.pack(anchor="w")

        repository = ctk.CTkLabel(
            info,
            text=project["repository"] or "No repository linked"
        )

        repository.pack(anchor="w")

        actions = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        actions.pack(
            side="right",
            padx=15
        )

        edit_button = ctk.CTkButton(
            actions,
            text="Edit",
            width=70,
            command=lambda p=project: self.open_edit_form(p)
        )

        edit_button.pack(
            side="left",
            padx=4
        )

        delete_button = ctk.CTkButton(
            actions,
            text="Delete",
            width=70,
            fg_color="#a83232",
            hover_color="#842626",
            command=lambda p=project: self.delete_project_confirm(p)
        )

        delete_button.pack(
            side="left",
            padx=4
        )

    def open_add_form(self):

        self.open_project_form()

    def open_edit_form(self, project):

        self.open_project_form(project)

    def open_project_form(self, project=None):

        is_edit = project is not None

        dialog = ctk.CTkToplevel(self)

        dialog.title(
            "Edit project" if is_edit else "New project"
        )

        dialog.geometry("500x450")

        dialog.transient(self)
        dialog.grab_set()

        title = ctk.CTkLabel(
            dialog,
            text="Edit project" if is_edit else "New project",
            font=("Segoe UI", 22, "bold")
        )

        title.pack(
            pady=(25, 20)
        )

        name_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Project name"
        )

        name_entry.pack(
            fill="x",
            padx=40,
            pady=8
        )

        repository_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Repository URL"
        )

        repository_entry.pack(
            fill="x",
            padx=40,
            pady=8
        )

        description_entry = ctk.CTkTextbox(
            dialog,
            height=120
        )

        description_entry.pack(
            fill="x",
            padx=40,
            pady=8
        )

        if is_edit:

            name_entry.insert(
                0,
                project["name"]
            )

            repository_entry.insert(
                0,
                project["repository"] or ""
            )

            description_entry.insert(
                "1.0",
                project["description"] or ""
            )

        def save():

            name = name_entry.get().strip()

            repository = repository_entry.get().strip()

            description = description_entry.get(
                "1.0",
                "end"
            ).strip()

            if not name:

                messagebox.showwarning(
                    "Validation",
                    "Project name is required."
                )

                return

            if is_edit:

                update_project(
                    project["id"],
                    name,
                    repository,
                    description
                )

            else:

                create_project(
                    name,
                    repository,
                    description
                )

            dialog.destroy()

            self.load_projects()

        save_button = ctk.CTkButton(
            dialog,
            text="Save",
            command=save
        )

        save_button.pack(
            pady=20
        )

    def delete_project_confirm(self, project):

        confirm = messagebox.askyesno(
            "Delete project",
            f"Delete '{project['name']}'?"
        )

        if not confirm:
            return

        delete_project(project["id"])

        self.load_projects()