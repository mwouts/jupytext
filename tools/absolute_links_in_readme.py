import re

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class AbsoluteLinksInReadme(BuildHookInterface):
    def initialize(self, version, build_data):
        readme_path = "README.md"
        base_url = "https://github.com/mwouts/jupytext/blob/main/"
        self.convert_links(readme_path, base_url)

    def convert_links(self, readme_path, base_url):
        with open(readme_path, "r") as file:
            content = file.read()

        # Regex to find markdown links
        pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        def replace_link(match):
            text, url = match.groups()
            if not url.startswith(("http://", "https://")):
                url = base_url + url
            return f"[{text}]({url})"

        new_content = pattern.sub(replace_link, content)

        with open(readme_path, "w") as file:
            file.write(new_content)
