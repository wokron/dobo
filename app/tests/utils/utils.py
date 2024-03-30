import random
import string

import httpx

candidate_urls = [
    "https://gitee.com/DataTraveler_0817/PyMuPDF-Utilities/raw/master/examples/demo1.pdf",
    # "https://gitee.com/DataTraveler_0817/PyMuPDF-Utilities/raw/master/examples/layout-demo1.pdf",
    # "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/Dart.pdf",
    # "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/Petresume.pdf",
    # "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/demo1.pdf",
]

pdf_cache: dict[str, bytes] = {}


def get_random_lower_string():
    return "".join(random.choices(string.ascii_lowercase, k=32))


def get_random_pdf():
    filename = get_random_lower_string() + ".pdf"
    url = random.choice(candidate_urls)
    if url not in pdf_cache:
        pdf_cache[url] = httpx.get(url).read()

    return filename, pdf_cache[url]
