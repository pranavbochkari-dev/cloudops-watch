
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

from monitor import check_website


class TestWebsiteMonitor(unittest.TestCase):

    @patch("monitor.urllib.request.urlopen")
    def test_website_is_up(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        mock_urlopen.return_value.__enter__.return_value = response

        result = check_website("https://example.com")

        self.assertTrue(result["is_up"])
        self.assertEqual(result["status_code"], 200)

    @patch("monitor.urllib.request.urlopen")
    def test_website_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "https://example.com", 500, "Server Error", {}, None
        )

        result = check_website("https://example.com")

        self.assertFalse(result["is_up"])
        self.assertEqual(result["status_code"], 500)

    @patch("monitor.urllib.request.urlopen")
    def test_website_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection failed")

        result = check_website("https://example.com")

        self.assertFalse(result["is_up"])
        self.assertIsNone(result["status_code"])


if __name__ == "__main__":
    unittest.main()
