import yaml
from pages import *
from pathlib import Path
from glob import glob
import os
import subprocess
# import markdown
import re

def load_markdown_files(directory: str) -> list[MdPage]:
    md_file_names = glob("**/*.md", root_dir=directory, recursive=True)
    md_files: list[MdPage] = []

    for file_name in md_file_names:
        with open(directory + file_name, "r", encoding="utf-8") as file:
            file_content = file.read()

        md_files.append(MdPage(file_name[:-3], file_content))

    return md_files

def render_html(markdown_pages: list[MdPage]) -> list[HtmlPage]:
    html_pages: list[HtmlPage] = []

    for md_page in markdown_pages:
        input = subprocess.Popen(("echo", md_page.contents), stdout=subprocess.PIPE)
        html_output = subprocess.check_output((
            "pandoc", 
            "--standalone", 
            "--mathjax", 
            "-f", 
            "gfm+hard_line_breaks+wikilinks_title_after_pipe",
            "-t",
            "html",
            "--metadata",
            f"title={md_page.title}"
        ), stdin=input.stdout)

        input.wait()

        filename = re.sub(r'\s+', '_', md_page.title)
        html_pages.append(HtmlPage(filename, md_page.title, html_output))

    return html_pages

def save_html_files(html_pages: list[HtmlPage], location: Path, index: str, index_location: Path):
    old_files = glob(str(location) + '/*')
    for f in old_files:
        os.remove(f)

    for html_page in html_pages:
        save_name = ""

        if (html_page.title == index):
            save_name = index_location / "index.html"
        else:
            save_name = html_page.filename + ".html"
            save_name = location / save_name

        with open(save_name, "wb") as file:
            file.write(html_page.contents)

if __name__ == "__main__":
    try:
        with open("settings.yaml", "r") as file:
            config_data = yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: settings.yaml not found.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        exit(1)

    md_files = load_markdown_files(config_data["source_dir"])
    html_files = render_html(md_files)
    save_html_files(html_files, Path(config_data["html_dir"]), config_data["index_file_name"], Path(config_data["index_dir"]))
    