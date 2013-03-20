"""
Shamlessly copied/modified from SublimeQuickFileCreator
https://github.com/noklesta/SublimeQuickFileCreator
"""
import os
import re
import sublime
import sublime_plugin
SETTINGS_KEY = 'SublimeQuickFileCreator'


class DirectoryPanel(sublime_plugin.WindowCommand):
    relative_paths = []
    full_torelative_paths = {}
    rel_path_start = 0

    def open_panel(self, cb):
        self.construct_excluded_pattern()
        self.build_relative_paths()
        if len(self.relative_paths) == 1:
            self.selected_dir = self.relative_paths[0]
            self.selected_dir = self.full_torelative_paths[self.selected_dir]
            self.window.show_input_panel(self.INPUT_PANEL_CAPTION, '', cb, None, None)
        elif len(self.relative_paths) > 1:
            self.move_current_directory_to_top()
            self.window.show_quick_panel(self.relative_paths, self.dir_selected)
        else:
            view = self.window.active_view()
            self.selected_dir = os.path.dirname(view.file_name())
            self.window.show_input_panel(self.INPUT_PANEL_CAPTION, '', cb, None, None)

    def construct_excluded_pattern(self):
        patterns = [pat.replace('|', '\\') for pat in self.get_setting('excluded_dir_patterns')]
        self.excluded = re.compile('|'.join(patterns))

    def get_setting(self, key):
        settings = None
        view = self.window.active_view()

        if view:
            settings = self.window.active_view().settings()

        if settings and settings.has(SETTINGS_KEY) and key in settings.get(SETTINGS_KEY):
            # Get project-specific setting
            results = settings.get(SETTINGS_KEY)[key]
        else:
            # Get user-specific or default setting
            settings = sublime.load_settings('%s.sublime-settings' % SETTINGS_KEY)
            results = settings.get(key)
        return results

    def build_relative_paths(self):
        folders = self.window.folders()
        self.relative_paths = []
        self.full_torelative_paths = {}
        for path in folders:
            rootfolders = os.path.split(path)[-1]
            self.rel_path_start = len(os.path.split(path)[0]) + 1
            if not self.excluded.search(rootfolders):
                self.full_torelative_paths[rootfolders] = path
                self.relative_paths.append(rootfolders)

            for base, dirs, files in os.walk(path):
                for dir in dirs:
                    relative_path = os.path.join(base, dir)[self.rel_path_start:]
                    if not self.excluded.search(relative_path):
                        self.full_torelative_paths[relative_path] = os.path.join(base, dir)
                        self.relative_paths.append(relative_path)

    def move_current_directory_to_top(self):
        view = self.window.active_view()
        if view.file_name():
            cur_dir = os.path.dirname(view.file_name())[self.rel_path_start:]
            if cur_dir in self.full_torelative_paths:
                i = self.relative_paths.index(cur_dir)
                self.relative_paths.insert(0, self.relative_paths.pop(i))
            else:
                self.relative_paths.insert(0, os.path.dirname(view.file_name()))
        return

    def dir_selected(self, selected_index):
        if selected_index != -1:
            self.selected_dir = self.relative_paths[selected_index]
            self.selected_dir = self.full_torelative_paths[self.selected_dir]
            self.window.show_input_panel(self.INPUT_PANEL_CAPTION, '', self.file_name_input, None, None)
