import typing
from dataclasses import dataclass
from io import StringIO
from itertools import islice
from pprint import pprint

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1
from pdfminer.utils import FileOrName

from xmp import xmp_to_dict

def parse_pdf(filename: str):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser=parser)
    pprint(doc.info)        # The "Info" metadata
    if 'Metadata' in doc.catalog:
        metadata = resolve1(doc.catalog['Metadata']).get_data()
        pprint(metadata)  # The raw XMP metadata
        pprint(xmp_to_dict(metadata))

    output_string = StringIO()
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
    print(output_string.getvalue())



@dataclass
class PaperMetadata:
    """
    Extracted metadata from a paper file
    """

    title: str = None
    authors: str = None
    filename: str = None

    @classmethod
    def from_file(cls, file: FileOrName) -> 'PaperMetadata':
        """
        Extract metadata from given file
        """
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer
        first_page = extract_pages(file).__next__()
        result = PaperMetadata()
        for i, element in enumerate(islice(first_page, 2)):
            if isinstance(element, LTTextContainer):
                text = element.get_text().replace("\n", " ").strip()
                if i == 0:
                    result.title = text
                elif i == 1:
                    result.authors = text
        print(result)
        result.filename = file.name
        return result

if __name__ == '__main__':
    PaperMetadata.from_file('../paper1.pdf')
