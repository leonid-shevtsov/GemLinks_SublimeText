import sublime
import sublime_plugin
import os.path
import os
import sys
import inspect
import subprocess
import json
import webbrowser
import locale

PLUGIN_PATH = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

class GemLinksListCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return self.gemfile_search_path() != None

    def run(self):
        view = self.window.active_view()
        path = self.gemfile_search_path()

        ruby_file = os.path.join(PLUGIN_PATH, "list_gems.rb")
        pipe = subprocess.Popen(['ruby', "-C" + path, ruby_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
        output, error = pipe.communicate()

        if pipe.returncode != 0:
            self.window.show_quick_panel([
                ["Failed to get list of gems", self._sanitize_output(error)]
                ], None)
        else:
            self.gems = json.loads(self._sanitize_output(output))
            gem_labels = [[ '%s %s' % (gem["name"],  gem["version"]), gem["summary"]] for gem in self.gems]
            self.window.show_quick_panel(gem_labels, self.show_gem_menu)

    def show_gem_menu(self, gem_index):
        if gem_index == -1:
            return
        self.gem = self.gems[gem_index]
        self.gem["rubygems_url"] = 'https://rubygems.org/gems/%s/versions/%s' % (self.gem["name"], self.gem["version"])
        self.gem["rubydocs_url"] = 'http://www.rubydoc.info/gems/%s/%s' % (self.gem["name"], self.gem["version"])
        self.gem["omniref_url"] = 'https://www.omniref.com/ruby/gems/%s/%s' % (self.gem["name"], self.gem["version"])

        self.gem_options = [
                [ self.gem["name"] + " homepage", self.gem["homepage_url"]],
                ["Rubygems", self.gem["rubygems_url"]],
                ["Rubydocs", self.gem["rubydocs_url"]],
                ["Omniref", self.gem["omniref_url"]],
                ["Open gem folder in new editor window", self.gem["path"]]
                ]

        sublime.set_timeout(lambda:
            self.window.show_quick_panel(self.gem_options, self.goto_result)
            ,10)

    def goto_result(self, option_index):
        param = self.gem_options[option_index][1]
        if option_index >=0 and option_index <= 3:
            webbrowser.open(param)
        else:
            if option_index == 4:
                sublime.run_command("new_window")
                sublime.active_window().set_project_data({"folders": [{"path": param}]})
                sublime.active_window().open_file(self.gem["spec_path"])

    def _sanitize_output(self, output):
        return output.decode(locale.getpreferredencoding(), 'ignore').strip()

    def gemfile_search_path(self):
        folders = self.window.folders()
        if len(folders) > 0:
            return folders[0]
        else:
            view = self.window.active_view()
            if view:
                filename = view.file_name()
                if filename:
                    return os.path.dirname(filename)
        return None
