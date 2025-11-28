from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase

from shop.models import Category, Product


class ShopAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Fruits', description='Fruits category', active=True)
        Category.objects.create(name='Ordinateur', description='Ordinateur category', active=False)

        cls.product = cls.category.products.create(name='Ananas', active=True)
        cls.category.products.create(name='Banane', active=False)

        cls.category_2 = Category.objects.create(name='Légumes', description='Légumes category', active=True)
        cls.product_2 = cls.category_2.products.create(name='Tomate', active=True)

    def format_datetime(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def get_article_list_data(self, articles):
        return [
            {
                'id': article.pk,
                'name': article.name,
                'date_created': self.format_datetime(article.date_created),
                'date_updated': self.format_datetime(article.date_updated),
                'product': article.product_id
            } for article in articles
        ]

    def get_product_list_data(self, products):
        return [
            {
                'id': product.pk,
                'name': product.name,
                'date_created': self.format_datetime(product.date_created),
                'date_updated': self.format_datetime(product.date_updated),
                'category': product.category_id,
            } for product in products
        ]

    def get_category_list_data(self, categories):
        return [
            {
                'id': category.id,
                'name': category.name,
                'date_created': self.format_datetime(category.date_created),
                'date_updated': self.format_datetime(category.date_updated),
            } for category in categories
        ]
    
    def get_admin_category_list_data(self, categories):
        return [
            {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'active': category.active,
                'date_created': self.format_datetime(category.date_created),
                'date_updated': self.format_datetime(category.date_updated),
            } for category in categories
        ]



class TestCategory(ShopAPITestCase):

    url = reverse_lazy('category-list')

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], self.get_admin_category_list_data([self.category, self.category_2]))

    def test_create(self):
        category_count = Category.objects.count()
        response = self.client.post(self.url, data={'name': 'Nouvelle catégorie'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Category.objects.count(), category_count)

    '''
    def test_admin_list_returns_all_categories_including_inactive(self):
        # call the admin category list endpoint
        response = self.client.get(reverse('admin-category-list'))
        self.assertEqual(response.status_code, 200)
    
        # build expected payload from DB so ordering matches
        data = response.json()
        expected_results = self.get_admin_category_list_data(list(Category.objects.all()))

        # ensure total count matches and returned page results match expected serialized objects
        self.assertEqual(data['count'], Category.objects.count())
        # API may paginate results or change ordering — compare by ids and membership
        returned = data['results']
        returned_ids = {item['id'] for item in returned}
        expected_ids = {item['id'] for item in expected_results}
        # returned ids must be a subset of expected ids (page may be partial)
        self.assertTrue(returned_ids.issubset(expected_ids))
        # ensure each returned item matches one of the expected serialized dicts
        for item in returned:
            self.assertIn(item, expected_results)
    '''

    def test_disable(self):
        response = self.client.post(reverse('category-disable', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertFalse(self.category.active)
        for product in self.category.products.all():
            self.assertFalse(product.active)
            for article in product.articles.all():
                self.assertFalse(article.active)


class TestProduct(ShopAPITestCase):

    url = reverse_lazy('product-list')

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_product_list_data([self.product, self.product_2]), response.json()['results'])

    def test_list_filter(self):
        response = self.client.get(self.url + '?category_id=%i' % self.category.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_product_list_data([self.product]), response.json()['results'])

    def test_create(self):
        product_count = Product.objects.count()
        response = self.client.post(self.url, data={'name': 'Nouvelle catégorie'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Product.objects.count(), product_count)

    def test_disable(self):
        response = self.client.post(reverse('product-disable', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertFalse(self.product.active)
        for article in self.product.articles.all():
            self.assertFalse(article.active)

    def test_delete(self):
        response = self.client.delete(reverse('product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 405)
        self.product.refresh_from_db()
