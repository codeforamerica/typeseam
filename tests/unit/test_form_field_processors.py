from unittest import TestCase

from typeseam.form_filler.form_field_processors import (
        initials,
        add,
        yesno
    )

class TestFormFieldProcessors(TestCase):

    def test_initials(self):
        self.assertEqual("H", initials(None, "hello"))
        self.assertEqual("", initials(None, ""))
        self.assertEqual("", initials(None, None))
        self.assertEqual("H", initials(None, " hello\n"))

    def test_add(self):
        goodargs = ["one", "two", "three"]
        noargs = []
        self.assertEqual("one two three", add(None, *goodargs))
        self.assertEqual(" ".join(goodargs), add(None, *goodargs))
        self.assertEqual("", add(None, *noargs))

    def test_yesno(self):
        self.assertEqual("Yes", yesno(None, "1"))
        self.assertEqual("No", yesno(None, "0"))
        self.assertEqual("No", yesno(None, None))
        self.assertEqual("No", yesno(None, 1))
        self.assertEqual("No", yesno(None, ""))
