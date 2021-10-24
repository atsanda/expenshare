import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,expected_status_code,expected_template_name",
    [
        ("/sharelists/1", 200, "index/welcome.html"),
        ("/users/autocomplete/search", 200, "index/welcome.html"),
        ("/sharelists/create", 200, "index/welcome.html"),
    ],
)
def test_unathorised_access(url, expected_status_code, expected_template_name, client):
    response = client.get(url, follow=True)
    assert response.status_code == expected_status_code
    assert response.templates[0].name == expected_template_name
