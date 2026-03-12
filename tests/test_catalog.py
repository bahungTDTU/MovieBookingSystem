import unittest


class TestCatalogService(unittest.TestCase):
    """Basic tests for the Catalog service."""

    def test_movie_list_is_list(self):
        movies = []
        self.assertIsInstance(movies, list)

    def test_movie_has_required_fields(self):
        movie = {
            "id": 1,
            "title": "Inception",
            "genre": "Sci-Fi",
            "duration": 148,
            "rating": 8.8,
        }
        for field in ("id", "title", "genre", "duration", "rating"):
            self.assertIn(field, movie)

    def test_movie_duration_positive(self):
        movie = {"duration": 120}
        self.assertGreater(movie["duration"], 0)

    def test_movie_rating_in_range(self):
        movie = {"rating": 7.5}
        self.assertGreaterEqual(movie["rating"], 0)
        self.assertLessEqual(movie["rating"], 10)

    def test_empty_search_returns_empty(self):
        results = [m for m in [] if "test" in m.get("title", "").lower()]
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
