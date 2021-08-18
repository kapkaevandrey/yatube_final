from django.test import Client, TestCase


class StaticURLTests(TestCase):
    """Testing static page."""

    def setUp(self):
        self.guest_client = Client()
        self.templates_url_name = {
            "author.html": "/about/author/",
            "tech.html": "/about/tech/",
        }

    def test_about_url_exists_at_desired_location(self):
        """Checking the availability of static page addresses."""
        for address in self.templates_url_name.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Checking templates for static addresses."""
        for template, address in self.templates_url_name.items():
            with self.subTest(template=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
