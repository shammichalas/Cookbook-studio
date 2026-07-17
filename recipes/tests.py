from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category, Tag, RecipeComment, RecipeLike, NewsletterSubscriber

User = get_user_model()

class RecipeSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testchef', password='password123')
        self.category = Category.objects.create(name='Lunch', slug='lunch')
        self.recipe = Recipe.objects.create(
            title='Tasty Roasted Potatoes',
            slug='tasty-roasted-potatoes',
            author=self.user,
            category=self.category,
            prep_time=15,
            cook_time=30,
            servings=4,
            difficulty='Easy',
            description='Perfect crispy potatoes with rosemary.',
            is_draft=False
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Discover Recipes Worth Remembering")

    def test_recipe_detail_loads(self):
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasty Roasted Potatoes')

    def test_recipe_search(self):
        response = self.client.get(reverse('recipe_list') + '?q=Potatoes')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasty Roasted Potatoes')

    def test_newsletter_subscribe(self):
        response = self.client.post(reverse('subscribe_newsletter'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(NewsletterSubscriber.objects.filter(email='test@example.com').exists())

    def test_recipe_like_toggle(self):
        self.client.login(username='testchef', password='password123')
        response = self.client.post(reverse('like_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(RecipeLike.objects.filter(recipe=self.recipe, user=self.user).count(), 1)

        # Toggle again to unlike
        response = self.client.post(reverse('like_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(RecipeLike.objects.filter(recipe=self.recipe, user=self.user).count(), 0)
