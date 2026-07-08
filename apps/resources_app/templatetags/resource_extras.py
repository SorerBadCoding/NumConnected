from django import template

register = template.Library()

ICON_MAP = {
    "PDF": "bi-file-earmark-pdf",
    "DOC": "bi-file-earmark-word",
    "DOCX": "bi-file-earmark-word",
    "PPT": "bi-file-earmark-ppt",
    "PPTX": "bi-file-earmark-ppt",
    "XLS": "bi-file-earmark-excel",
    "XLSX": "bi-file-earmark-excel",
    "ZIP": "bi-file-earmark-zip",
    "PNG": "bi-file-earmark-image",
    "JPG": "bi-file-earmark-image",
    "JPEG": "bi-file-earmark-image",
    "TXT": "bi-file-earmark-text",
}


@register.filter
def file_icon(extension):
    return ICON_MAP.get((extension or "").upper(), "bi-file-earmark")
