from src import main


def test_get_inverse_urls_ein_index():
    assert main.get_inverse_urls_ein_index(
        {
            "https://www.example.com/12345": "12345",
            "https://www.example.com/12345/1": "12345",
            "https://www.example.com/67890": "67890",
            "https://www.example.com/67890/1": "67890",
        }
    ) == {
        "12345": [
            "https://www.example.com/12345",
            "https://www.example.com/12345/1",
        ],
        "67890": [
            "https://www.example.com/67890",
            "https://www.example.com/67890/1",
        ],
    }
