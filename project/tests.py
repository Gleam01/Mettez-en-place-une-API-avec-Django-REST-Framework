from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase

from shop.models import Category, Product

class ShopAPITestCase(APITestCase):
    def format_datetime(self, value):
        # Cette méthode est un helper permettant de formater une date en chaine de caractères sous le même format que celui de l’api
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    def get_product_detail_data(self, products):
        # Cette méthode est un helper permettant de formater les données des produits liés à une catégorie
        data = []
        for product in products:
            data.append({
                'id': product.pk,
                'name': product.name,
                'description': product.description,
                'category': product.category_id,
                'date_created': self.format_datetime(product.date_created),
                'date_updated': self.format_datetime(product.date_updated),
            })
        return data


class TestCategory(ShopAPITestCase):
    # Nous stockons l’url de l'endpoint dans un attribut de classe pour pouvoir l’utiliser plus facilement dans chacun de nos tests
    url = reverse_lazy('category-list')

    def setUp(self):
        # Créons deux catégories dont une seule est active
        self.category = Category.objects.create(name='Fruits', active=True)
        Category.objects.create(name='Légumes', active=False)

        # active product (should appear in detail's products)
        Product.objects.create(name='Apple', category=self.category, active=True)
        # inactive product (should NOT appear)
        Product.objects.create(name='Banana', category=self.category, active=False)

    def test_list(self):
        # On réalise l’appel en GET en utilisant le client de la classe de test
        response = self.client.get(self.url)
        # Nous vérifions que le status code est bien 200
        # et que les valeurs retournées sont bien celles attendues
        self.assertEqual(response.status_code, 200)
        excepted = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': self.category.pk,
                    'name': self.category.name,
                    'date_created': self.format_datetime(self.category.date_created),
                    'date_updated': self.format_datetime(self.category.date_updated),
                }
            ]
        }

        self.assertEqual(excepted, response.json())
    
    def test_detail(self):
        # Nous utilisons l'url de détail
        url_detail = reverse('category-detail',kwargs={'pk': self.category.pk})
        response = self.client.get(url_detail)
        # Nous vérifions également le status code de retour ainsi que les données reçues
        self.assertEqual(response.status_code, 200)
        excepted = {
            'id': self.category.pk,
            'name': self.category.name,
            'description': self.category.description,
            'date_created': self.format_datetime(self.category.date_created),
            'date_updated': self.format_datetime(self.category.date_updated),
            'products': self.get_product_detail_data(self.category.products.filter(active=True)),
        }
        self.assertEqual(excepted, response.json())


    def test_create(self):
        # Nous vérifions qu’aucune catégorie n'existe avant de tenter d’en créer une
        self.assertTrue(Category.objects.exists())
        response = self.client.post(self.url, data={'name': 'Nouvelle catégorie'})
        # Vérifions que le status code est bien en erreur et nous empêche de créer une catégorie
        self.assertEqual(response.status_code, 405)
        # Enfin, vérifions qu'aucune nouvelle catégorie n’a été créée malgré le status code 405
        self.assertFalse(Category.objects.filter(name='Nouvelle catégorie').exists())