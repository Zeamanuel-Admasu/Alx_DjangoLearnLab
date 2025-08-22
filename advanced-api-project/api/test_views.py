# api/test_views.py
"""
End-to-end API tests for the Book endpoints using Django REST Framework.

Covers:
- CRUD: list, detail, create, update, delete (including alias endpoints)
- Permissions: unauthenticated vs authenticated access
- Validation: publication_year not in the future
- Filtering: title, author id, author_name, year ranges
- Search: on title & author__name
- Ordering: by publication_year, title (asc/desc)
"""

from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Author, Book


class BookAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Users
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="pass1234"
        )

        # Authors
        cls.achebe = Author.objects.create(name="Chinua Achebe")
        cls.ngugi = Author.objects.create(name="Ngũgĩ wa Thiong'o")

        # Books
        cls.b1 = Book.objects.create(
            title="Things Fall Apart", publication_year=1958, author=cls.achebe
        )
        cls.b2 = Book.objects.create(
            title="No Longer at Ease", publication_year=1960, author=cls.achebe
        )
        cls.b3 = Book.objects.create(
            title="Petals of Blood", publication_year=1977, author=cls.ngugi
        )

    # ---------- READ (AllowAny) ----------

    def test_list_books_ok(self):
        url = reverse("book-list")  # GET /books/
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 3)
        # Basic shape check
        self.assertIn("title", res.data[0])
        self.assertIn("publication_year", res.data[0])
        self.assertIn("author", res.data[0])

    def test_detail_book_ok(self):
        url = reverse("book-detail", kwargs={"pk": self.b1.pk})  # GET /books/<pk>/
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.b1.id)
        self.assertEqual(res.data["title"], "Things Fall Apart")

    # ---------- CREATE (IsAuthenticated) ----------

    def test_create_book_unauthenticated_rejected(self):
        url = reverse("book-create")  # POST /books/create/
        payload = {
            "title": "New Book",
            "publication_year": 2001,
            "author": self.achebe.id,
        }
        res = self.client.post(url, payload, format="json")
        # With Basic/Session auth configured, unauthenticated usually returns 401
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authenticated_ok(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-create")
        payload = {
            "title": "Arrow of God",
            "publication_year": 1964,
            "author": self.achebe.id,
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Arrow of God")
        self.assertEqual(res.data["publication_year"], 1964)

    def test_create_book_future_year_invalid(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-create")
        next_year = date.today().year + 1
        payload = {
            "title": "From the Future",
            "publication_year": next_year,
            "author": self.achebe.id,
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("publication_year", res.data)

    # ---------- UPDATE (IsAuthenticated) ----------

    def test_update_book_unauthenticated_rejected(self):
        url = reverse("book-update", kwargs={"pk": self.b1.pk})  # /books/<pk>/update/
        res = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_authenticated_ok(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-update", kwargs={"pk": self.b1.pk})
        res = self.client.patch(url, {"title": "Things Fall Apart (Updated)"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Things Fall Apart (Updated)")

    def test_update_book_authenticated_ok_alias_query_param(self):
        """
        Alias endpoint: /books/update?id=<pk>
        """
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-update-alias")  # /books/update
        res = self.client.patch(
            url + f"?id={self.b2.id}",
            {"title": "No Longer at Ease (Rev)"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "No Longer at Ease (Rev)")

    # ---------- DELETE (IsAuthenticated) ----------

    def test_delete_book_unauthenticated_rejected(self):
        url = reverse("book-delete", kwargs={"pk": self.b3.pk})  # /books/<pk>/delete/
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_authenticated_no_content(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-delete", kwargs={"pk": self.b3.pk})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.b3.pk).exists())

    def test_delete_book_authenticated_alias_query_param(self):
        """
        Alias endpoint: /books/delete?id=<pk>
        """
        self.client.login(username="tester", password="pass1234")
        # Create a throwaway book to delete through the alias
        tmp = Book.objects.create(title="Tmp", publication_year=2000, author=self.achebe)
        url = reverse("book-delete-alias")  # /books/delete
        res = self.client.delete(url + f"?id={tmp.id}")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=tmp.pk).exists())

    # ---------- FILTERING / SEARCH / ORDERING (AllowAny on list) ----------

    def test_filter_by_author_id(self):
        url = reverse("book-list")
        res = self.client.get(url, {"author": self.achebe.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only Achebe's books should appear
        titles = {b["title"] for b in res.data}
        self.assertTrue({"Things Fall Apart", "No Longer at Ease"}.issubset(titles))
        self.assertNotIn("Petals of Blood", titles)

    def test_filter_by_author_name_icontains(self):
        url = reverse("book-list")
        res = self.client.get(url, {"author_name": "achebe"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in res.data}
        self.assertIn("Things Fall Apart", titles)
        self.assertIn("No Longer at Ease", titles)
        self.assertNotIn("Petals of Blood", titles)

    def test_filter_by_title_icontains(self):
        url = reverse("book-list")
        res = self.client.get(url, {"title": "petals"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Petals of Blood")

    def test_filter_by_year_range(self):
        url = reverse("book-list")
        res = self.client.get(url, {"publication_year__gte": 1959, "publication_year__lte": 1977})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        years = {b["publication_year"] for b in res.data}
        self.assertTrue({1960, 1977}.issubset(years))

    def test_search_title_and_author(self):
        url = reverse("book-list")
        res = self.client.get(url, {"search": "achebe"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in res.data}
        self.assertIn("Things Fall Apart", titles)
        self.assertIn("No Longer at Ease", titles)

    def test_ordering_desc_publication_year(self):
        url = reverse("book-list")
        res = self.client.get(url, {"ordering": "-publication_year"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        years = [b["publication_year"] for b in res.data]
        self.assertEqual(years, sorted(years, reverse=True))

    def test_ordering_multi_fields(self):
        # Add another 1977 book to ensure secondary ordering by title is applied
        Book.objects.create(title="Another 1977", publication_year=1977, author=self.ngugi)
        url = reverse("book-list")
        res = self.client.get(url, {"ordering": "-publication_year,title"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        # Confirm non-increasing by year; ties respected by title asc
        years = [b["publication_year"] for b in data]
        self.assertEqual(years, sorted(years, reverse=True))
        # Check relative order of the 1977 entries by title
        titles_1977 = [b["title"] for b in data if b["publication_year"] == 1977]
        self.assertEqual(titles_1977, sorted(titles_1977))
