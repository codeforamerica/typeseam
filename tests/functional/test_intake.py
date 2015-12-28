from tests.test_base import SeleniumBaseTestCase

class TestIntakeTasks(SeleniumBaseTestCase):

    def test_index_get(self):
        self.get('/')
        self.assertIn('Clean Slate', self.browser.title)
        self.screenshot('index.png')