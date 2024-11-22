from rest_framework import serializers

from .models import Product, File, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("title", "description", "avatar")

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "title", "file", "file_type")

        def get_file_type(self, obj):
            return obj.get_file_type_display()


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ("id", "title", "description", "avatar", "categories", "url")