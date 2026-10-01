import customtkinter as ctk
import sqlite3
from tkinter import filedialog, messagebox

from database import (
    backup_database,
    initialize_database,
    restore_database
)
from models import (
    count_projects,
    count_deployments,
    get_success_rate,
    get_recent_deployments,
    get_setting,
    set_setting
)

from views.projects import ProjectsView
from views.deployments import DeploymentsView
from status_styles import get_status_style


class DeployTrackApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("DeployTrack")
        self.geometry("1100x700")
        self.minsize(900, 600)

        ctk.set_appearance_mode(get_setting("appearance_mode", "dark"))
        ctk.set_default_color_theme("blue")

        self.current_view = None

        self.create_layout()
        self.show_dashboard()

    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )

        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        # Logo
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="DeployTrack",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        logo_label.pack(
            padx=20,
            pady=(30, 40)
        )

        # Navigation buttons
        self.dashboard_button = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            anchor="w",
            command=self.show_dashboard
        )

        self.dashboard_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.projects_button = ctk.CTkButton(
            self.sidebar,
            text="Projects",
            anchor="w",
            command=self.show_projects
        )

        self.projects_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.deployments_button = ctk.CTkButton(
            self.sidebar,
            text="Deployments",
            anchor="w",
            command=self.show_deployments
        )

        self.deployments_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.settings_button = ctk.CTkButton(
            self.sidebar,
            text="Settings",
            anchor="w",
            command=self.show_settings
        )

        self.settings_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

    def clear_view(self):
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_view()

        dashboard = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0
        )

        dashboard.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        header = ctk.CTkFrame(dashboard, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 18))
        ctk.CTkLabel(
            header,
            text="Overview",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="A quick look at your projects and latest deployments.",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray70")
        ).pack(anchor="w", pady=(4, 0))

        total_projects = count_projects()
        total_deployments = count_deployments()
        success_rate = get_success_rate()

        stats_frame = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        stats_frame.pack(fill="x", padx=5, pady=(0, 16))

        for column in range(3):
            stats_frame.grid_columnconfigure(column, weight=1)

        self.create_stat_card(
            stats_frame, "Projects", str(total_projects), 0
        )
        self.create_stat_card(
            stats_frame, "Total deployments", str(total_deployments), 1
        )
        self.create_stat_card(
            stats_frame,
            "Success rate",
            f"{success_rate}%",
            2,
            value_color=("#15803D", "#4ADE80")
        )

        recent_label = ctk.CTkLabel(
            dashboard,
            text="Recent deployments",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        recent_label.pack(anchor="w", padx=10, pady=(2, 8))
        recent_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        recent_frame.pack(fill="x", padx=5, pady=(0, 14))
        recent_deployments = get_recent_deployments(5)

        if not recent_deployments:
            ctk.CTkLabel(
                recent_frame,
                text="No deployments yet. Create your first deployment from the Deployments page."
            ).pack(pady=20)
        else:
            for deployment in recent_deployments:
                self.create_deployment_card(recent_frame, deployment)

        self.current_view = dashboard
    
    def create_stat_card(
        self,
        parent,
        title,
        value,
        column,
        value_color=None
    ):
        card = ctk.CTkFrame(
            parent,
            corner_radius=12
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70")
        ).pack(anchor="w", padx=16, pady=(13, 4))
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=value_color
        ).pack(anchor="w", padx=16, pady=(0, 13))
    
    def refresh_dashboard(self):
        if self.current_view is not None:
            self.show_dashboard()

    def create_deployment_card(self, parent, deployment):
        card = ctk.CTkFrame(
            parent,
            corner_radius=10
        )

        card.pack(
            fill="x",
            pady=5
        )

        status_style = get_status_style(deployment["status"])
        ctk.CTkLabel(
            card,
            text=f"{deployment['project_name']}  •  {deployment['version']}",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            card,
            text=(
                f"{deployment['environment']}   ·   "
                f"{deployment['branch'] or 'no branch'}   ·   "
                f"{deployment['deployed_at']}"
            ),
            text_color=("gray40", "gray70")
        ).pack(anchor="w", padx=14, pady=(0, 10))
        ctk.CTkLabel(
            card,
            text=deployment["status"],
            fg_color=status_style["background"],
            text_color=status_style["text"],
            corner_radius=8,
            padx=9,
            pady=4
        ).place(relx=1.0, x=-14, y=12, anchor="ne")

    def show_projects(self):
        self.clear_view()

        self.current_view = ProjectsView(
            self.content_frame
        )

        self.current_view.pack(
            fill="both",
            expand=True
        )

    def show_deployments(self):
        self.clear_view()

        self.current_view = DeploymentsView(
            self.content_frame
        )

        self.current_view.pack(
            fill="both",
            expand=True
        )

    def show_settings(self):
        self.clear_view()

        settings = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        settings.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        title = ctk.CTkLabel(
            settings,
            text="Settings",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            anchor="w"
        )

        ctk.CTkLabel(
            settings,
            text="Appearance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(24, 8))
        ctk.CTkLabel(settings, text="Theme").pack(anchor="w")
        theme_option = ctk.CTkOptionMenu(
            settings,
            values=["Dark", "Light", "System"],
            command=self.change_appearance
        )
        saved_mode = get_setting("appearance_mode", "dark")
        theme_option.set({
            "dark": "Dark",
            "light": "Light",
            "system": "System"
        }.get(saved_mode, "Dark"))
        theme_option.pack(anchor="w", pady=(6, 20))

        ctk.CTkLabel(
            settings,
            text="Application data",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(4, 8))
        ctk.CTkLabel(
            settings,
            text="Create a database backup or restore DeployTrack from a backup file."
        ).pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(
            settings,
            text="Create backup",
            command=self.create_backup
        ).pack(anchor="w", pady=5)
        ctk.CTkButton(
            settings,
            text="Restore backup",
            fg_color="#9a6b13",
            hover_color="#7d560f",
            command=self.restore_backup
        ).pack(anchor="w", pady=5)

        self.current_view = settings

    def change_appearance(self, mode):
        appearance_mode = {
            "Dark": "dark",
            "Light": "light",
            "System": "system"
        }[mode]
        set_setting("appearance_mode", appearance_mode)
        ctk.set_appearance_mode(appearance_mode)

    def create_backup(self):
        file_path = filedialog.asksaveasfilename(
            title="Save DeployTrack backup",
            defaultextension=".db",
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")],
            initialfile="deploytrack-backup.db"
        )
        if not file_path:
            return
        try:
            backup_database(file_path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Backup failed", str(error))
            return
        except Exception as error:
            messagebox.showerror("Backup failed", f"An error occurred:\n{error}")
            return
        messagebox.showinfo("Backup complete", "The database backup was saved successfully.")

    def restore_backup(self):
        file_path = filedialog.askopenfilename(
            title="Choose a DeployTrack backup",
            filetypes=[("SQLite database", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )
        if not file_path:
            return
        if not messagebox.askyesno(
            "Confirm restore",
            "Current application data will be replaced with the backup. Continue?"
        ):
            return
        try:
            restore_database(file_path)
        except (OSError, ValueError, sqlite3.Error) as error:
            messagebox.showerror("Restore failed", str(error))
            return
        except Exception as error:
            messagebox.showerror("Restore failed", f"An error occurred:\n{error}")
            return
        ctk.set_appearance_mode(get_setting("appearance_mode", "dark"))
        messagebox.showinfo("Restore complete", "The backup was restored successfully.")
        self.show_settings()

if __name__ == "__main__":
    initialize_database()

    app = DeployTrackApp()
    app.mainloop()