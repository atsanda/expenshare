from django.urls import reverse
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize("url,expected_status_code,expected_template_name", [
   ('/', 200, 'main/welcome.html'),
   ('/terms', 200, 'main/terms.html'),
   ('/policy', 200, 'main/policy.html'),
   ('/sharelists/1', 200, 'main/welcome.html'),
   ('/user-autocomplete', 200, 'main/welcome.html'),
   ('/sharelists/create', 200, 'main/welcome.html')
])
def test_unathorised_access(url, expected_status_code, expected_template_name,
                            client):
    response = client.get(url, follow=True)
    assert response.status_code == expected_status_code
    assert response.templates[0].name == expected_template_name
