
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from storre.models import Collection,Product
import pytest 
from model_bakery import baker

#we use the mark.django_db to have access to the database behavior
@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        # if we are testing we have the triple A the arrange, act, assert
        #Arrange
        #act
        response = api_client.post ('/store/collections/', {'title':'a'} )
        #assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self,api_client):
        # if we are testing we have the triple A the arrange, act, assert
        #Arrange
        #act
        api_client.force_authenticate(user={})
        response = api_client.post ('/store/collections/', {'title':'a'} )
        #assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self,api_client):
        # if we are testing we have the triple A the arrange, act, assert
        #Arrange
        #act
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post ('/store/collections/', {'title':''} )
        #assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self,api_client):
        # if we are testing we have the triple A the arrange, act, assert
        #Arrange
        #act
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post ('/store/collections/', {'title':'a'} )
        #assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


#our class must start with test for pytest to be able to detect it
@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_return_200(self, api_client):
        collection = baker.make(Collection)
        response = api_client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK
        response.data == {
            'id': collection.id,
            'title': collection.title
        }


