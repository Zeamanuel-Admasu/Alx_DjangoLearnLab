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
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)
        # Basic shape check
        self.assertIn("title", response.data[0])
        self.assertIn("publication_year", response.data[0])
        self.assertIn("author", response.data[0])

    def test_detail_book_ok(self):
        url = reverse("book-detail", kwargs={"pk": self.b1.pk})  # GET /books/<pk>/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.b1.id)
        self.assertEqual(response.data["title"], "Things Fall Apart")

    # ---------- CREATE (IsAuthenticated) ----------

    def test_create_book_unauthenticated_rejected(self):
        url = reverse("book-create")  # POST /books/create/
        payload = {
            "title": "New Book",
            "publication_year": 2001,
            "author": self.achebe.id,
        }
        response = self.client.post(url, payload, format="json")
        # Expect 401 when Basic/Session auth challenges are enabled
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authenticated_ok(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-create")
        payload = {
            "title": "Arrow of God",
            "publication_year": 1964,
            "author": self.achebe.id,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Arrow of God")
        self.assertEqual(response.data["publication_year"], 1964)

    def test_create_book_future_year_invalid(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-create")
        next_year = date.today().year + 1
        payload = {
            "title": "From the Future",
            "publication_year": next_year,
            "author": self.achebe.id,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("publication_year", response.data)

    # ---------- UPDATE (IsAuthenticated) ----------

    def test_update_book_unauthenticated_rejected(self):
        url = reverse("book-update", kwargs={"pk": self.b1.pk})  # /books/<pk>/update/
        response = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_authenticated_ok(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-update", kwargs={"pk": self.b1.pk})
        response = self.client.patch(
            url, {"title": "Things Fall Apart (Updated)"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Things Fall Apart (Updated)")

    def test_update_book_authenticated_ok_alias_query_param(self):
        """
        Alias endpoint: /books/update?id=<pk>
        """
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-update-alias")  # /books/update
        response = self.client.patch(
            url + f"?id={self.b2.id}",
            {"title": "No Longer at Ease (Rev)"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "No Longer at Ease (Rev)")

    # ---------- DELETE (IsAuthenticated) ----------

    def test_delete_book_unauthenticated_rejected(self):
        url = reverse("book-delete", kwargs={"pk": self.b3.pk})  # /books/<pk>/delete/
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_authenticated_no_content(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("book-delete", kwargs={"pk": self.b3.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.b3.pk).exists())

    def test_delete_book_authenticated_alias_query_param(self):
        """
        Alias endpoint: /books/delete?id=<pk>
        """
        self.client.login(username="tester", password="pass1234")
        tmp = Book.objects.create(title="Tmp", publication_year=2000, author=self.achebe)
        url = reverse("book-delete-alias")  # /books/delete
        response = self.client.delete(url + f"?id={tmp.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=tmp.pk).exists())

    # ---------- FILTERING / SEARCH / ORDERING (AllowAny on list) ----------

    def test_filter_by_author_id(self):
        url = reverse("book-list")
        response = self.client.get(url, {"author": self.achebe.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in response.data}
        self.assertTrue({"Things Fall Apart", "No Longer at Ease"}.issubset(titles))
        self.assertNotIn("Petals of Blood", titles)

    def test_filter_by_author_name_icontains(self):
        url = reverse("book-list")
        response = self.client.get(url, {"author_name": "achebe"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in response.data}
        self.assertIn("Things Fall Apart", titles)
        self.assertIn("No Longer at Ease", titles)
        self.assertNotIn("Petals of Blood", titles)

    def test_filter_by_title_icontains(self):
        url = reverse("book-list")
        response = self.client.get(url, {"title": "petals"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Petals of Blood")

    def test_filter_by_year_range(self):
        url = reverse("book-list")
        response = self.client.get(
            url, {"publication_year__gte": 1959, "publication_year__lte": 1977}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = {b["publication_year"] for b in response.data}
        self.assertTrue({1960, 1977}.issubset(years))

    def test_search_title_and_author(self):
        url = reverse("book-list")
        response = self.client.get(url, {"search": "achebe"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in response.data}
        self.assertIn("Things Fall Apart", titles)
        self.assertIn("No Longer at Ease", titles)

    def test_ordering_desc_publication_year(self):
        url = reverse("book-list")
        response = self.client.get(url, {"ordering": "-publication_year"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [b["publication_year"] for b in response.data]
        self.assertEqual(years, sorted(years, reverse=True))

    def test_ordering_multi_fields(self):
        Book.objects.create(title="Another 1977", publication_year=1977, author=self.ngugi)
        url = reverse("book-list")
        response = self.client.get(url, {"ordering": "-publication_year,title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        years = [b["publication_year"] for b in data]
        self.assertEqual(years, sorted(years, reverse=True))
        titles_1977 = [b["title"] for b in data if b["publication_year"] == 1977]
        self.assertEqual(titles_1977, sorted(titles_1977))
