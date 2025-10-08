import re
from pathlib import Path

from hatchling.metadata.plugin.interface import MetadataHookInterface


class AbsoluteLinksInReadme(MetadataHookInterface):
    """Hook that processes README.md to make relative links absolute."""

    def update(self, metadata):
        """Process README.md when metadata is being prepared."""
        readme_src_path = Path("README.md")
        readme_output_path = Path("build/README_with_absolute_links.md")
        base_url = "https://github.com/mwouts/jupytext/blob/main/"

        # Ensure the dist directory exists
        readme_output_path.parent.mkdir(exist_ok=True)

        self.convert_links(readme_src_path, readme_output_path, base_url)
        return metadata

    def convert_links(self, src_path, output_path, base_url):
        """Convert relative links in README.md to absolute links."""
        print(f"Processing {src_path} to generate {output_path} with absolute links")
        content = src_path.read_text(encoding="utf-8")

        # Find markdown links that don't start with http:// or https://
        pattern = re.compile(r"\[([^\]]+)\]\((?!http)([^)]+)\)")

        def replace_link(match):
            text, url = match.groups()
            if not url.startswith(("http://", "https://", "#")):
                url = base_url + url
            return f"[{text}]({url})"

        new_content = pattern.sub(replace_link, content)

        # Write the processed content to the output file
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(new_content, encoding="utf-8")
        print(f"Generated {output_path} with absolute links")
