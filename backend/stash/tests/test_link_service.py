import pytest
import httpx

from stash.services.links import LinkService


@pytest.fixture
def link_service():
    """Create a LinkService instance for testing."""
    client = httpx.AsyncClient()
    return LinkService(client)


class TestUrlCleaning:
    def test_adds_scheme(self, link_service):
        """Test that https:// is added if missing."""
        assert link_service._clean_url("example.com") == "https://example.com"
        assert link_service._clean_url("http://example.com") == "http://example.com"
        assert link_service._clean_url("https://example.com") == "https://example.com"

    def test_normalizes_domain(self, link_service):
        """Test that domains are normalized to lowercase."""
        assert link_service._clean_url("EXAMPLE.com") == "https://example.com"
        assert link_service._clean_url("Example.COM") == "https://example.com"

    def test_removes_fragments(self, link_service):
        """Test that URL fragments are removed."""
        assert link_service._clean_url("example.com#section") == "https://example.com"
        assert link_service._clean_url("example.com/#section") == "https://example.com/"

    def test_preserves_valid_query_params(self, link_service):
        """Test that non-tracking query parameters are preserved."""
        # Test with a single parameter
        assert (
            link_service._clean_url("example.com?id=123")
            == "https://example.com?id=123"
        )

        # Test with multiple parameters
        url = "example.com?id=123&page=1&sort=desc"
        assert (
            link_service._clean_url(url)
            == "https://example.com?id=123&page=1&sort=desc"
        )

    def test_removes_tracking_params(self, link_service):
        """Test that tracking parameters are removed."""
        # Test UTM parameters
        url = "example.com?utm_source=twitter&utm_medium=social&id=123"
        assert link_service._clean_url(url) == "https://example.com?id=123"

        # Test social media parameters
        url = "example.com?fbclid=abc123&id=123"
        assert link_service._clean_url(url) == "https://example.com?id=123"

        # Test Amazon parameters
        url = "amazon.com/product?tag=affiliate&pd_rd_r=123&id=456"
        assert link_service._clean_url(url) == "https://amazon.com/product?id=456"

    def test_handles_malformed_query_params(self, link_service):
        """Test handling of malformed query parameters."""
        # Test empty parameter
        assert link_service._clean_url("example.com?") == "https://example.com"

        # Test parameter without value
        assert link_service._clean_url("example.com?key") == "https://example.com"

        # Test parameter with empty value
        assert link_service._clean_url("example.com?key=") == "https://example.com?key="

    def test_real_world_examples(self, link_service):
        """Test with real-world URL examples."""
        # Amazon product with tracking
        amazon = "amazon.com/dp/B01234?tag=affiliate&pd_rd_r=123&ref=nosim"
        assert link_service._clean_url(amazon) == "https://amazon.com/dp/B01234"

        # Twitter with tracking
        twitter = "twitter.com/user/status/123?ref_src=twsrc%5Etfw"
        assert link_service._clean_url(twitter) == "https://twitter.com/user/status/123"

        # Blog with UTM tracking
        blog = "blog.example.com/post?utm_source=newsletter&utm_medium=email&id=123"
        assert link_service._clean_url(blog) == "https://blog.example.com/post?id=123"
