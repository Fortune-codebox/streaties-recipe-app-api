"""Tests for tags Api"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from core import models

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(**params):
    """Create a user and return"""
    return get_user_model().objects.create_user(**params)


def create_tag(user, name):
    """Create and retrun tag"""
    return Tag.objects.create(user=user, name=name)


class PublicClassApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retreiving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClassApiTests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.user = create_user(email='user@example.com', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        create_tag(self.user, 'Vegan')
        create_tag(self.user, 'Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tag limited to authenticated user."""
        user2 = create_user(email='mary@example.com', password='test123')
        create_tag(user2, 'Fruity')
        tag = create_tag(self.user, 'Comfort')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
