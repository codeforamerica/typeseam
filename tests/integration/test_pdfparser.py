from unittest import TestCase

from tests.mock.factories import SubmissionFactory
from typeseam.form_filler.pdfparser import PDFParser

class TestPDFParser(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_fill_rap_request(self):
        pdf_path = "data/pdfs/CleanSlateCombined.pdf"
        pdfparser = PDFParser()
        result = pdfparser.fill_pdf(pdf_path, {
                'LastName': "Orbison",
                'FirstName': "Roy",
                'DOB': '4/23/36',
                })
        self.assertEqual(type(result), bytes)

