from rest_framework import serializers
from shop.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'date_created', 'date_updated']
