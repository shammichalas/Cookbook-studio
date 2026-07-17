from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category
from cookbooks.models import Cookbook
from cookbooks.pdf_utils import generate_cookbook_pdf

User = get_user_model()

class CookbookSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testchef', password='password123')
        self.category = Category.objects.create(name='Traditional', slug='traditional')
        self.recipe = Recipe.objects.create(
            title='Classic Pasta',
            slug='classic-pasta',
            author=self.user,
            category=self.category,
            prep_time=10,
            cook_time=20,
            is_draft=False
        )
        self.cookbook = Cookbook.objects.create(
            title='Italian Masterpieces',
            slug='italian-masterpieces',
            owner=self.user,
            description='Authentic Italian food compilation.'
        )
        self.cookbook.recipes.add(self.recipe)

    def test_cookbook_detail_loads(self):
        response = self.client.get(reverse('cookbook_detail', kwargs={'slug': self.cookbook.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Italian Masterpieces')
        self.assertContains(response, 'Classic Pasta')

    def test_pdf_generation_flow(self):
        self.client.login(username='testchef', password='password123')
        response = self.client.get(reverse('generate_pdf', kwargs={'slug': self.cookbook.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)

    def test_pdf_generation_utility(self):
        pdf_buffer = generate_cookbook_pdf(self.cookbook)
        self.assertTrue(pdf_buffer.getvalue())
        self.assertTrue(len(pdf_buffer.getvalue()) > 0)
