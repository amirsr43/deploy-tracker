import customtkinter as ctk
from tkinter import messagebox, filedialog
from collections import Counter
from status_styles import get_status_style

from models import (
    get_projects,
    create_deployment,
    update_deployment,
    delete_deployment,
    search_deployments,
    export_deployments_to_csv,
    export_deployments_to_excel
)


class DeploymentsView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.projects = get_projects()
        self.selected_status = "All"
        self.status_options = {
            "All statuses": "All",
            "Pending": "Pending",
            "Building": "Building",
            "Deploying": "Deploying",
            "Success": "Success",
            "Failed": "Failed",
            "Rolled Back": "Rolled Back"
        }
        self.status_labels = {
            value: label for label, value in self.status_options.items()
        }
        project_name_counts = Counter(
            project["name"] for project in self.projects
        )
        self.project_filter_values = {"All projects": None}
        for project in self.projects:
            project_name = project["name"]
            label = project_name
            if project_name_counts[project_name] > 1 or project_name == "All projects":
                label = f"{project_name} (#{project['id']})"
            self.project_filter_values[label] = project["id"]

        self.grid_columnconfigure(0, weight=1)
        self.create_header()
        self.create_deployment_list()

        self.load_deployments()

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
            text="Deployments",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            heading,
            text="Search, review, and export deployment history.",
            font=("Segoe UI", 13),
            text_color=("gray40", "gray70")
        ).pack(anchor="w", pady=(3, 0))

        export_button = ctk.CTkButton(
            header,
            text="Export",
            width=100,
            command=self.show_export_options
        )

        export_button.pack(side="right", padx=(10, 0))

        add_button = ctk.CTkButton(
            header,
            text="+ New deployment",
            width=130,
            command=self.open_add_form
        )

        add_button.pack(side="right")

    def create_deployment_list(self):

        filter_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        filter_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15)
        )

        filter_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search project, version, branch, or commit"
        )

        self.search_entry.grid(
            row=0,
            column=0,
            columnspan=1,
            sticky="ew",
            padx=(0, 8)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.on_filter_change
        )

        self.result_count_label = ctk.CTkLabel(
            filter_frame,
            text="",
            width=120,
            anchor="e"
        )
        self.result_count_label.grid(row=0, column=1, padx=8)

        self.advanced_filter_button = ctk.CTkButton(
            filter_frame,
            text="Filter",
            width=110,
            fg_color="transparent",
            hover_color=("#E2E8F0", "#334155"),
            text_color=("#1F2937", "#E5E7EB"),
            border_color=("#94A3B8", "#64748B"),
            border_width=1,
            command=self.toggle_advanced_filters
        )
        self.advanced_filter_button.grid(row=0, column=2)

        self.advanced_filters = ctk.CTkFrame(
            filter_frame,
            fg_color=("#F1F5F9", "#1B1B1B"),
            border_color=("#CBD5E1", "#333333"),
            border_width=1,
            corner_radius=10
        )
        self.advanced_filters.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(10, 0)
        )
        for column in range(2):
            self.advanced_filters.grid_columnconfigure(column, weight=1)

        for column, label in enumerate(("Environment", "Project")):
            ctk.CTkLabel(
                self.advanced_filters,
                text=label,
                anchor="w",
                font=("Segoe UI", 12, "bold")
            ).grid(
                row=0,
                column=column,
                sticky="ew",
                padx=8,
                pady=(9, 0)
            )

        self.environment_filter = ctk.CTkOptionMenu(
            self.advanced_filters,
            values=[
                "All environments",
                "Development",
                "Staging",
                "Production"
            ],
            command=self.on_filter_change,
            width=150
        )

        self.environment_filter.set("All environments")
        self.environment_filter.grid(
            row=1, column=0, sticky="ew", padx=6, pady=(10, 5)
        )

        self.project_filter = ctk.CTkOptionMenu(
            self.advanced_filters,
            values=list(self.project_filter_values),
            command=self.on_filter_change,
            width=170
        )
        self.project_filter.set("All projects")
        self.project_filter.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=6,
            pady=(10, 5)
        )

        ctk.CTkButton(
            self.advanced_filters,
            text="Clear filters",
            fg_color="transparent",
            hover_color=("#E2E8F0", "#334155"),
            text_color=("#1F2937", "#E5E7EB"),
            border_color=("#94A3B8", "#64748B"),
            border_width=1,
            command=self.reset_filters
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=8)

        self.advanced_filters.grid_remove()
        self.filters_expanded = False

        self.status_filter_frame = ctk.CTkFrame(
            filter_frame,
            fg_color="transparent"
        )
        self.status_filter_frame.grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0)
        )
        ctk.CTkLabel(
            self.status_filter_frame,
            text="Status",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=(0, 8))
        self.status_filter = ctk.CTkOptionMenu(
            self.status_filter_frame,
            values=list(self.status_options),
            command=self.on_status_filter_change,
            width=180
        )
        self.status_filter.set("All statuses")
        self.status_filter.pack(side="left")

        self.deployment_list = ctk.CTkScrollableFrame(
            self
        )

        self.deployment_list.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 30)
        )

        self.grid_rowconfigure(
            2,
            weight=1
        )

    def toggle_advanced_filters(self):
        self.filters_expanded = not self.filters_expanded
        if self.filters_expanded:
            self.advanced_filters.grid()
        else:
            self.advanced_filters.grid_remove()
        self.update_filter_button()

    def update_filter_button(self):
        active_count = sum((
            self.environment_filter.get() != "All environments",
            self.project_filter.get() != "All projects"
        ))
        if self.filters_expanded:
            text = "Hide filters"
            if active_count:
                text = f"{text} ({active_count} active)"
        elif active_count:
            text = f"Filters ({active_count} active)"
        else:
            text = "Filter"
        self.advanced_filter_button.configure(text=text)

    def on_status_filter_change(self, selected_label):
        self.selected_status = self.status_options[selected_label]
        self.on_filter_change()

    def load_deployments(self):
        self.on_filter_change()

    def render_deployments(self, deployments):

        for widget in self.deployment_list.winfo_children():
            widget.destroy()

        if not deployments:

            empty_label = ctk.CTkLabel(
                self.deployment_list,
                text="No deployments match the selected filters."
            )

            empty_label.pack(
                pady=30
            )

            return

        for deployment in deployments:

            self.create_deployment_card(
                deployment
            )

    def create_deployment_card(self, deployment):

        card = ctk.CTkFrame(
            self.deployment_list
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

        project_label = ctk.CTkLabel(
            info,
            text=deployment["project_name"],
            font=("Segoe UI", 16, "bold")
        )

        project_label.pack(anchor="w")

        details = (
            f"{deployment['version']}  •  "
            f"{deployment['environment']}  •  "
            f"{deployment['branch'] or 'No branch'}"
        )

        details_label = ctk.CTkLabel(
            info,
            text=details
        )

        details_label.pack(anchor="w")

        status_style = get_status_style(deployment["status"])
        status_label = ctk.CTkLabel(
            card,
            text=deployment["status"],
            width=100,
            fg_color=status_style["background"],
            text_color=status_style["text"],
            corner_radius=8
        )

        status_label.pack(
            side="left",
            padx=10
        )

        details_button = ctk.CTkButton(
            card,
            text="Details",
            width=80,
            fg_color="transparent",
            hover_color=("#E2E8F0", "#334155"),
            text_color=("#1F2937", "#E5E7EB"),
            border_color=("#94A3B8", "#64748B"),
            border_width=1,
            command=lambda d=deployment: self.show_details(d)
        )
        details_button.pack(side="left", padx=(4, 15))

    def show_details(self, deployment):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Deployment details")
        dialog.geometry("400x580")
        dialog.transient(self)
        dialog.grab_set()

        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(
            content,
            text=f"{deployment['project_name']} · {deployment['version']}",
            font=("Segoe UI", 22, "bold"),
            wraplength=480
        ).pack(anchor="w", pady=(0, 15))

        fields = [
            ("Status", deployment["status"]),
            ("Environment", deployment["environment"]),
            ("Branch", deployment["branch"] or "-"),
            ("Commit", deployment["commit_hash"] or "-"),
            ("Deployed by", deployment["deployed_by"] or "-"),
            ("Duration", f"{deployment['duration'] or 0} seconds"),
            ("Deployed at", deployment["deployed_at"]),
            ("Notes", deployment["notes"] or "-"),
            ("Failure reason", deployment["error_reason"] or "-")
        ]
        for label, value in fields:
            ctk.CTkLabel(
                content,
                text=label,
                font=("Segoe UI", 13, "bold")
            ).pack(anchor="w", pady=(7, 1))
            ctk.CTkLabel(
                content,
                text=value,
                justify="left",
                anchor="w",
                wraplength=480
            ).pack(fill="x", anchor="w")

        actions = ctk.CTkFrame(dialog, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 18))
        ctk.CTkButton(
            actions,
            text="Edit",
            command=lambda: self.edit_from_details(dialog, deployment)
        ).pack(side="left")
        ctk.CTkButton(
            actions,
            text="Delete",
            fg_color="#a83232",
            hover_color="#842626",
            command=lambda: self.delete_from_details(dialog, deployment)
        ).pack(side="left", padx=8)
        # ctk.CTkButton(
        #     actions,
        #     text="Close",
        #     fg_color="transparent",
        #     hover_color=("#E2E8F0", "#334155"),
        #     text_color=("#1F2937", "#E5E7EB"),
        #     border_color=("#94A3B8", "#64748B"),
        #     border_width=1,
        #     command=dialog.destroy
        # ).pack(side="right")

    def edit_from_details(self, dialog, deployment):
        dialog.destroy()
        self.open_edit_form(deployment)

    def delete_from_details(self, dialog, deployment):
        dialog.destroy()
        self.delete_deployment_confirm(deployment)

    def open_add_form(self):

        self.open_deployment_form()

    def open_edit_form(self, deployment):

        self.open_deployment_form(deployment)

    def open_deployment_form(self, deployment=None):

        is_edit = deployment is not None
        projects = get_projects()

        if not is_edit and not projects:
            messagebox.showwarning(
                "Project required",
                "Create a project before adding a deployment."
            )
            return

        dialog = ctk.CTkToplevel(self)

        dialog.title(
            "Edit deployment"
            if is_edit
            else "New deployment"
        )

        dialog.geometry("520x770")

        dialog.transient(self)
        dialog.grab_set()

        title = ctk.CTkLabel(
            dialog,
            text=(
                "Edit deployment"
                if is_edit
                else "New deployment"
            ),
            font=("Segoe UI", 22, "bold")
        )

        title.pack(pady=(25, 20))

        project_names = [
            project["name"]
            for project in projects
        ]

        project_combo = ctk.CTkOptionMenu(
            dialog,
            values=project_names
        )

        ctk.CTkLabel(
            dialog,
            text="Project",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=40, pady=(3, 0))
        project_combo.pack(
            fill="x",
            padx=40,
            pady=7
        )

        version_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Version (e.g. v1.2.0)"
        )

        version_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        environment_combo = ctk.CTkOptionMenu(
            dialog,
            values=[
                "Development",
                "Staging",
                "Production"
            ]
        )

        ctk.CTkLabel(
            dialog,
            text="Environment",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=40, pady=(5, 0))
        environment_combo.pack(
            fill="x",
            padx=40,
            pady=7
        )

        branch_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Branch (e.g. main)"
        )

        branch_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        commit_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Commit hash"
        )

        commit_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        status_combo = ctk.CTkOptionMenu(
            dialog,
            values=[
                "Pending",
                "Building",
                "Deploying",
                "Success",
                "Failed",
                "Rolled Back"
            ]
        )

        ctk.CTkLabel(
            dialog,
            text="Status",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=40, pady=(5, 0))
        status_combo.pack(
            fill="x",
            padx=40,
            pady=7
        )

        deployed_by_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Deployed by"
        )

        deployed_by_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        duration_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Duration in seconds"
        )

        duration_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        notes_entry = ctk.CTkTextbox(
            dialog,
            height=80
        )

        notes_entry.pack(
            fill="x",
            padx=40,
            pady=7
        )

        error_reason_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Failure reason (if failed)"
        )
        error_reason_entry.pack(fill="x", padx=40, pady=7)

        if is_edit:

            project_combo.set(
                deployment["project_name"]
            )

            version_entry.insert(
                0,
                deployment["version"]
            )

            environment_combo.set(
                deployment["environment"]
            )

            branch_entry.insert(
                0,
                deployment["branch"] or ""
            )

            commit_entry.insert(
                0,
                deployment["commit_hash"] or ""
            )

            status_combo.set(
                deployment["status"]
            )

            deployed_by_entry.insert(
                0,
                deployment["deployed_by"] or ""
            )

            duration_entry.insert(
                0,
                str(deployment["duration"] or 0)
            )

            notes_entry.insert(
                "1.0",
                deployment["notes"] or ""
            )
            error_reason_entry.insert(
                0,
                deployment["error_reason"] or ""
            )

        def save():

            project_name = project_combo.get()
            version = version_entry.get().strip()
            environment = environment_combo.get()
            branch = branch_entry.get().strip()
            commit_hash = commit_entry.get().strip()
            status = status_combo.get()
            deployed_by = deployed_by_entry.get().strip()
            notes = notes_entry.get("1.0", "end").strip()
            error_reason = error_reason_entry.get().strip()

            if not project_name or not version:
                messagebox.showwarning(
                    "Validation",
                    "Project and version are required."
                )
                return

            project_id = next(
                (
                    project["id"]
                    for project in projects
                    if project["name"] == project_name
                ),
                None
            )

            if project_id is None:
                messagebox.showerror(
                    "Error",
                    "Project not found."
                )
                return

            try:
                duration = int(
                    duration_entry.get() or 0
                )
            except ValueError:
                messagebox.showwarning(
                    "Validation",
                    "Duration must be a number."
                )
                return

            if is_edit:

                update_deployment(
                    deployment["id"],
                    project_id,
                    version,
                    environment,
                    branch,
                    commit_hash,
                    status,
                    deployed_by,
                    duration,
                    notes,
                    error_reason
                )

            else:

                create_deployment(
                    project_id,
                    version,
                    environment,
                    branch,
                    commit_hash,
                    status,
                    deployed_by,
                    duration,
                    notes,
                    error_reason
                )

            dialog.destroy()
            self.load_deployments()

        save_button = ctk.CTkButton(
            dialog,
            text="Save",
            command=save
        )

        save_button.pack(pady=15)

    def delete_deployment_confirm(self, deployment):

        confirm = messagebox.askyesno(
            "Delete deployment",
            f"Delete deployment {deployment['version']}?"
        )

        if not confirm:
            return

        delete_deployment(deployment["id"])

        self.load_deployments()
    
    def on_filter_change(self, event=None):
        search = self.search_entry.get().strip()

        environment = self.environment_filter.get()

        project_id = self.project_filter_values.get(
            self.project_filter.get()
        )
        self.update_filter_button()

        deployments = search_deployments(
            search=search,
            environment=environment,
            status=self.selected_status,
            project_id=project_id
        )

        count = len(deployments)
        self.result_count_label.configure(
            text=f"{count} deployment"
        )
        self.render_deployments(deployments)

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.environment_filter.set("All environments")
        self.project_filter.set("All projects")
        self.selected_status = "All"
        self.status_filter.set(self.status_labels[self.selected_status])
        self.on_filter_change()

    def get_export_filters(self):
        project_id = self.project_filter_values.get(
            self.project_filter.get()
        )
        return {
            "search": self.search_entry.get().strip(),
            "environment": self.environment_filter.get(),
            "status": self.selected_status,
            "project_id": project_id
        }

    def show_export_options(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Export data")
        dialog.geometry("340x210")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Choose an export format",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(24, 16))

        options = ctk.CTkFrame(dialog, fg_color="transparent")
        options.pack(fill="x", padx=24)
        ctk.CTkButton(
            options,
            text="CSV",
            command=lambda: self.choose_export_format(dialog, self.export_csv)
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(
            options,
            text="Excel",
            command=lambda: self.choose_export_format(dialog, self.export_excel)
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkButton(
            dialog,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        ).pack(pady=14)

    @staticmethod
    def choose_export_format(dialog, export_action):
        dialog.destroy()
        export_action()

    def export_csv(self):

        file_path = filedialog.asksaveasfilename(
            title="Export deployment history",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ],
            initialfile="deployment-history.csv"
        )

        if not file_path:
            return
        try:
            export_deployments_to_csv(
                file_path,
                **self.get_export_filters()
            )

            messagebox.showinfo(
                "Export complete",
                "Deployment history exported successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Export failed",
                f"An error occurred while exporting:\n{error}"
            )

    def export_excel(self):

        file_path = filedialog.asksaveasfilename(
            title="Export deployment history",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Files", "*.xlsx")
            ],
            initialfile="deployment-history.xlsx"
        )

        if not file_path:
            return
        try:
            export_deployments_to_excel(
                file_path,
                **self.get_export_filters()
            )

            messagebox.showinfo(
                "Export complete",
                "Deployment history exported to Excel successfully."
            )
        except Exception as error:
            messagebox.showerror(
                "Export failed",
                f"An error occurred while exporting:\n{error}"
            )