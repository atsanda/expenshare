import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,expected_status_code,expected_template_name",
    [
        ("/", 200, "index/welcome.html"),
        ("/terms", 200, "pages/terms.html"),
        ("/policy", 200, "pages/policy.html"),
    ],
)
def test_access(url, expected_status_code, expected_template_name, client):
    response = client.get(url, follow=True)
    assert response.status_code == expected_status_code
    assert response.templates[0].name == expected_template_name
