import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import json
import os

class ProductivityApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Productivity App")
        self.set_default_size(600, 400)

        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.todos_file = os.path.join(self.data_dir, "todos.json")
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.notes_file = os.path.join(self.data_dir, "notes.json")
        self.urls_file = os.path.join(self.data_dir, "urls.json")

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # To-Do Tab
        self.todo_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.notebook.append_page(self.todo_page, Gtk.Label(label='To-Do'))

        self.todo_entry = Gtk.Entry()
        self.todo_entry.set_placeholder_text("Add a new task")
        self.todo_page.pack_start(self.todo_entry, False, True, 0)

        self.todo_list = Gtk.ListBox()
        self.todo_page.pack_start(self.todo_list, True, True, 0)

        self.todo_entry.connect("activate", self.add_todo)
        self.load_todos()

        # Projects Tab
        self.projects_page = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.notebook.append_page(self.projects_page, Gtk.Label(label='Projects'))

        projects_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.projects_page.pack_start(projects_list_box, False, True, 0)

        self.project_entry = Gtk.Entry()
        self.project_entry.set_placeholder_text("New Project Name")
        projects_list_box.pack_start(self.project_entry, False, True, 0)

        self.project_list = Gtk.ListBox()
        projects_list_box.pack_start(self.project_list, True, True, 0)

        self.project_entry.connect("activate", self.add_project)
        self.project_list.connect("row-selected", self.project_selected)
        self.load_projects()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.projects_page.pack_start(scrolled_window, True, True, 0)

        self.project_notes_view = Gtk.TextView()
        self.project_notes_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.project_notes_view)

        # Notes Tab
        self.notes_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.notebook.append_page(self.notes_page, Gtk.Label(label='Notes'))

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.notes_page.pack_start(scrolled_window, True, True, 0)

        self.notes_view = Gtk.TextView()
        self.notes_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.notes_view)
        self.notes_buffer = self.notes_view.get_buffer()
        self.notes_buffer.connect("changed", self.save_notes)
        self.load_notes()

        # URLs Tab
        self.urls_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.notebook.append_page(self.urls_page, Gtk.Label(label='URLs'))

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Add a new URL")
        self.urls_page.pack_start(self.url_entry, False, True, 0)

        self.url_list = Gtk.ListBox()
        self.urls_page.pack_start(self.url_list, True, True, 0)

        self.url_entry.connect("activate", self.add_url)
        self.load_urls()

    def add_todo(self, entry):
        task = entry.get_text()
        if task:
            self.todos.append(task)
            self.save_todos()
            self.load_todos()
            entry.set_text("")

    def add_url(self, entry):
        url = entry.get_text()
        if url:
            self.urls.append(url)
            self.save_urls()
            self.load_urls()
            entry.set_text("")

    def add_project(self, entry):
        project_name = entry.get_text()
        if project_name:
            self.projects[project_name] = ""
            self.save_projects()
            self.load_projects()
            entry.set_text("")

    def load_todos(self):
        if os.path.exists(self.todos_file):
            with open(self.todos_file, 'r') as f:
                self.todos = json.load(f)
        else:
            self.todos = []

        for child in self.todo_list.get_children():
            self.todo_list.remove(child)

        for task in self.todos:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            label = Gtk.Label(label=task, xalign=0)
            check = Gtk.CheckButton()
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(check, False, True, 0)
            self.todo_list.add(row)

    def save_todos(self):
        with open(self.todos_file, 'w') as f:
            json.dump(self.todos, f)

    def load_projects(self):
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            self.projects = {}

        for child in self.project_list.get_children():
            self.project_list.remove(child)

        for project_name in self.projects:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=project_name, xalign=0)
            row.add(label)
            self.project_list.add(row)

    def save_projects(self):
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f)

    def project_selected(self, listbox, row):
        if row:
            project_name = row.get_child().get_label()
            self.project_notes_view.get_buffer().set_text(self.projects[project_name])
            self.current_project = project_name
            self.project_notes_view.get_buffer().connect("changed", self.save_project_notes)

    def save_project_notes(self, text_buffer):
        if hasattr(self, 'current_project'):
            notes = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), False)
            self.projects[self.current_project] = notes
            self.save_projects()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r') as f:
                notes = f.read()
                self.notes_buffer.set_text(notes)

    def save_notes(self, buffer):
        notes = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        with open(self.notes_file, 'w') as f:
            f.write(notes)

    def load_urls(self):
        if os.path.exists(self.urls_file):
            with open(self.urls_file, 'r') as f:
                self.urls = json.load(f)
        else:
            self.urls = []

        for child in self.url_list.get_children():
            self.url_list.remove(child)

        for url in self.urls:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=url, xalign=0)
            row.add(label)
            self.url_list.add(row)

    def save_urls(self):
        with open(self.urls_file, 'w') as f:
            json.dump(self.urls, f)

win = ProductivityApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
