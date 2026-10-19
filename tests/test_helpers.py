import os
import unittest
from unittest.mock import MagicMock, patch

import requests

import helper


class HelperTests(unittest.TestCase):
    """Check timeout settings and scraper failure results without real I/O."""

    def test_mongo_timeouts(self):
        """Bound MongoDB waits while retaining the configured database."""
        with (
            patch.dict(
                os.environ,
                {
                    "MONGO_CLUSTER": "example",
                    "MONGO_USER": "user",
                    "MONGO_PASSWORD": "test",
                },
            ),
            patch.object(helper, "MongoClient") as client,
        ):
            helper.connectMongo()
        client.assert_called_once()
        self.assertEqual(
            client.call_args.kwargs,
            {
                "serverSelectionTimeoutMS": 3000,
                "connectTimeoutMS": 2000,
                "socketTimeoutMS": 3000,
            },
        )

    def test_scraper_timeouts(self):
        """All four scrapers make one timed request and return their failure result."""
        scrapers = (
            helper.scrapeProductInfo_amzn,
            helper.scrapeProductInfo_flkt,
            helper.scrapeProductInfo_mntr,
            helper.scrapeProductInfo_boat,
        )
        for scraper in scrapers:
            for failure in (requests.ConnectTimeout, requests.ReadTimeout):
                with self.subTest(scraper=scraper.__name__, failure=failure.__name__):
                    with patch.object(
                        helper.requests, "get", side_effect=failure
                    ) as get:
                        self.assertEqual(scraper("https://example.test/item"), [-1, -1])
                    get.assert_called_once()
                    self.assertEqual(get.call_args.kwargs["timeout"], (2, 3))

    def test_successful_scrapes(self):
        """Keep successful product parsing unchanged for each supported shop."""
        amazon = MagicMock()
        amazon.content = b'<div id="productTitle">Product</div><span class="a-price-whole">1,299.</span>'
        flipkart = MagicMock()
        flipkart.json.return_value = {"name": "Product", "current_price": 1299}
        myntra = MagicMock()
        myntra.text = '<script></script><script>{"name":"Product","offers":{"price":1299}}</script>'
        boat = MagicMock()
        boat.text = '<h1 class="product-meta__title heading h3">Product</h1><span class="price price--highlight price--large">₹1,299</span>'
        for scraper, response in (
            (helper.scrapeProductInfo_amzn, amazon),
            (helper.scrapeProductInfo_flkt, flipkart),
            (helper.scrapeProductInfo_mntr, myntra),
            (helper.scrapeProductInfo_boat, boat),
        ):
            with (
                self.subTest(scraper=scraper.__name__),
                patch.object(helper.requests, "get", return_value=response),
            ):
                self.assertEqual(
                    scraper("https://example.test/item"), ["Product", 1299]
                )
