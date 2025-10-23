import yaml
from pages import *
from pathlib import Path
from glob import glob
import os
import subprocess
import re
from mako.template import Template
import frontmatter
from dirsync import sync
import shutil

def load_markdown_files(directory: str) -> list[MdPage]:
    md_file_names = glob("**/*.md", root_dir=directory, recursive=True)
    md_files: list[MdPage] = []

    for file_name in md_file_names:
        with open(directory + file_name, "r", encoding="utf-8") as file:
            file_content = file.read()

        md_files.append(MdPage(file_name[:-3], file_content))

    return md_files

def strip_wikilink_braces(wikilink: str) -> str:
    return wikilink[2:-2]

def render_html(markdown_pages: list[MdPage]) -> list[HtmlPage]:
    html_pages: list[HtmlPage] = []
    template_html = ""
    with open("./src/template.html", "r") as file:
        template_html = file.read()

    for md_page in markdown_pages:
        front_matter = frontmatter.loads(md_page.contents)
        input = subprocess.Popen(("echo", md_page.contents), stdout=subprocess.PIPE)
        html_output = subprocess.check_output((
            "pandoc", 
            "--mathjax", 
            "-f", 
            "gfm+hard_line_breaks+wikilinks_title_after_pipe",
            "-t",
            "html",
            "--metadata",
            f"title={md_page.title}",
            "--css",
            "./static/css/styles.css"
        ), stdin=input.stdout)

        input.wait()

        previous_page: str | None = front_matter.get("previous")

        if (previous_page): previous_page = strip_wikilink_braces(previous_page)

        next_page: str | None = front_matter.get("next")

        if (next_page): next_page = strip_wikilink_braces(next_page)

        series_page: str | None = front_matter.get("series")

        if (series_page): series_page = strip_wikilink_braces(series_page)

        html_output = Template(template_html).render(
            title=md_page.title,
            contents=html_output.decode("utf-8"),
            previousPage=previous_page,
            nextPage=next_page,
            seriesPage=series_page,
        )

        filename = re.sub(r'\s+', '_', md_page.title)
        html_pages.append(HtmlPage(filename, md_page.title, html_output))

    return html_pages

def delete_old_publication():
    publish_dir = "./publish"

    if not os.path.isdir(publish_dir):
        return

    try:
        shutil.rmtree(publish_dir)
        print(f"Directory '{publish_dir}' and its contents deleted successfully.")
    except OSError as e:
        print(f"Error deleting directory '{publish_dir}': {e}")
    else:
        print(f"Directory '{publish_dir}' does not exist.")

def save_html_files(html_pages: list[HtmlPage], location: Path, index: str, index_location: Path):
    old_files = glob(str(location) + '/*')
    for f in old_files:
        os.remove(f)

    location.mkdir(parents=True, exist_ok=True)

    for html_page in html_pages:
        save_name = ""

        if (html_page.title == index):
            save_name = index_location / "index.html"
        else:
            save_name = html_page.filename + ".html"
            save_name = location / save_name

        with open(save_name, "w") as file:
            file.write(html_page.contents)

def publish_css():
    sync("./src/css", "./publish/css", "sync", purge=True, create=True)

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
    delete_old_publication()
    save_html_files(html_files, Path("./publish/html"), config_data["index_file_name"], Path("./publish"))
    publish_css()
    