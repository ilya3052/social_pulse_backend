# Create your tests here.
from django.db import IntegrityError
from django.test import TestCase

from social_entities.models import Group, Platform
from users.models import CustomUser


class TestUserModel(TestCase):
    def setUp(self):
        self.vk = Platform.objects.create(name="VK", alias="vk")
        self.tg = Platform.objects.create(name="TG", alias="tg")

        self.group1 = Group.objects.create(name='group1', link='link1', external_id=1, slug='group1', platform=self.vk)
        self.group2 = Group.objects.create(name='group1', link='link1', external_id=1, slug='group2', platform=self.tg)
        self.group3 = Group.objects.create(name='group1', link='link1', external_id=2, slug='group3', platform=self.vk)
        self.group4 = Group.objects.create(name='group1', link='link1', external_id=2, slug='group4', platform=self.tg)

        self.user1 = CustomUser.objects.create_user(username='test_name', email='test@test.ru', password='HardP@ssw0rd9527')
        self.user2 = CustomUser.objects.create_user(username='test_name2', email='test1@test.ru', password='HardP@ssw0rd9527')

    def test_create_user(self):
        self.assertEqual(self.user1.id, 1)
        self.assertEqual(self.user2.id, 2)
        self.assertEqual(CustomUser.objects.count(), 2)

    def test_email_unique(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(username='test_name2', email='test@test.ru', password='HardP@ssw0rd95271')

    def test_username_unique(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(username='test_name', email='test@test.ru', password='HardP@ssw0rd95271')

    def test_str(self):
        self.assertEqual(str(self.user1), 'test_name')



