import re

from jinja2 import Template

from utils.logger import logger


def get_templates(templates_dir):
    return [
        fichier
        for fichier in templates_dir.iterdir()
        if fichier.is_file()
        and fichier.name != ".gitkeep"
    ]


def display_templates(templates):
    print("\nTemplates disponibles :")

    for i, fichier in enumerate(templates, start=1):
        nom = fichier.stem.replace("_", " ")
        print(f"{i}. {nom}")


def get_template_fields(template_file):
    with open(template_file, encoding="utf-8") as f:
        content = f.read()

    fields = list(dict.fromkeys(
        re.findall(r"{{\s*(\w+)\s*}}", content)
    ))

    logger.info(
        "Liste des champs nécessaires :\n"
        + "\n".join(f"- {field}" for field in fields)
    )

    return fields


def render_template(template_file, data):
    with open(template_file, encoding="utf-8") as f:
        template = Template(f.read())

    return template.render(**data)