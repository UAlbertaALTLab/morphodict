# mypy: ignore-errors
import json
from urllib import response
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from .views import word_details_api, search_api


import requests

'''
By using https://www.sisense.com/blog/rest-api-testing-strategy-what-exactly-should-you-test/ as a resource on
RESTful application testing
'''

class Testing(APITestCase):
    def test_database_search(self):
        self.factory = APIRequestFactory()
        '''
        1. case where the search data in the database  
        '''
        word = "atâhk"
        expectedResponse1 = {"atâhk" : {
                    "Latn-x-macron": "atāhk",
                    "Latn": "atâhk",
                    "Cans": "ᐊᑖᕽ"}, 
                    
                }
        expectedResponse2 = {"atâhk" : True}
        expectedResponse3 = {"atâhk" : "atâhk"}
        data = {"name": word}  
        request = self.factory.post('/api/search/', data, format='json')
        #TESTING CORRECT STATUS CODE HTTP 200
        response = search_api(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        content = json.loads(response.content)
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["text"], expectedResponse1[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["is_lemma"], expectedResponse2[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["slug"], expectedResponse3[word])
        return

    def test_simple_word_search(self):
        self.factory = APIRequestFactory()
        '''
        2. in database simple word
        '''
        word = "one"
        expectedResponse1 = { word: {
                    "Latn-x-macron": "awa",
                    "Latn": "awa",
                    "Cans": "ᐊᐘ"},
                }
        expectedResponse2 = {"one": True}
        expectedResponse3 = {"one": "awa@pra"}
        data = {"name": word}  
        request = self.factory.post('/api/search/', data, format='json')
        #TESTING CORRECT STATUS CODE HTTP 200
        response = search_api(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        content = json.loads(response.content)
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["text"], expectedResponse1[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["is_lemma"], expectedResponse2[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["slug"], expectedResponse3[word])
        return

    def test_word_space(self):
        self.factory = APIRequestFactory()
        '''
        3. in database with space
        '''
        word = "to run"
        expectedResponse1 = {word: {
                    "Latn-x-macron": "nōhtēpayiw",
                    "Latn": "nôhtêpayiw",
                    "Cans": "ᓅᐦᑌᐸᔨᐤ"}
                }
        expectedResponse2 = {"to run": True}
        expectedResponse3 = {"to run": "nôhtêpayiw@vai"}
        data = {"name": word}  
        request = self.factory.post('/api/search/', data, format='json')
        #TESTING CORRECT STATUS CODE HTTP 200
        response = search_api(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        content = json.loads(response.content)
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["text"], expectedResponse1[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["is_lemma"], expectedResponse2[word])
        self.assertEqual(content["search_results"][0]["lemma_wordform"]["slug"], expectedResponse3[word])
        return
    
    def test_not_in_database(self):
        self.factory = APIRequestFactory()
        '''
        4. SAD PATH testing: not in the database
        '''
        word = "%yes@yes"
        data = {"name": word}  
        request = self.factory.post('/api/search/', data, format='json')
        #TESTING CORRECT STATUS CODE HTTP 200
        response = search_api(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        content = json.loads(response.content)
        self.assertEqual(content["search_results"], [])
        return
        
    def test_word_with_a_path(self):
        self.factory = APIRequestFactory()
        '''
        5. SAD PATH testing: not in the database
        '''
        word = "/dsadasdas/asdafasfafasasf"
        data = {"name": word}  
        request = self.factory.post('/api/search/', data, format='json')
        #TESTING CORRECT STATUS CODE HTTP 200
        response = search_api(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        content = json.loads(response.content)
        self.assertEqual(content["search_results"], [])
        return

    def test_slug_word_edgecase1(self):
        self.factory = APIRequestFactory()
        word = "atâhk"
        expectedResponse1 = {word : {
                    "Latn-x-macron": "atāhk",
                    "Latn": "atâhk",
                    "Cans": "ᐊᑖᕽ"}, 
                }
        sluglist = {"atâhk" : "atâhk"}
        url = "/api/word/" + sluglist[word] + "/"
        request = self.factory.get(url, format='json')
        response = word_details_api(request, sluglist[word])
        content = json.loads(response.content)
        #TESTING CORRECT STATUS CODE HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        self.assertEqual(content["nipaw_wordform"]["wordform"]["text"], expectedResponse1[word])

    def test_slug_word_edgecase2(self):
        self.factory = APIRequestFactory()
        word = "one"
        expectedResponse1 = {word : {
                    "Latn-x-macron": "awa",
                    "Latn": "awa",
                    "Cans": "ᐊᐘ"},
                }
        sluglist = {"one": "awa@pra"}
        url = "/api/word/" + sluglist[word] + "/"
        request = self.factory.get(url, format='json')
        response = word_details_api(request, sluglist[word])
        content = json.loads(response.content)
        #TESTING CORRECT STATUS CODE HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        self.assertEqual(content["nipaw_wordform"]["wordform"]["text"], expectedResponse1[word])

    def test_slug_word_edgecase3(self):
        self.factory = APIRequestFactory()
        word = "to run"
        expectedResponse1 = {word : {
                    "Latn-x-macron": "nōhtēpayiw",
                    "Latn": "nôhtêpayiw",
                    "Cans": "ᓅᐦᑌᐸᔨᐤ"}
                }
        sluglist = {"to run": "nôhtêpayiw@vai"}
        url = "/api/word/" + sluglist[word] + "/"
        request = self.factory.get(url, format='json')
        response = word_details_api(request, sluglist[word])
        content = json.loads(response.content)
        #TESTING CORRECT STATUS CODE HTTP 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TESTING RESPONSE PAYLOAD
        self.assertEqual(content["nipaw_wordform"]["wordform"]["text"], expectedResponse1[word])
    
    def test_slug_word_bad_path(self):
        #bad path
        self.factory = APIRequestFactory()
        word = "helloitsme" #random characters
        url = "/api/word/" + word + "/"
        request = self.factory.get(url, format='json')
        response = word_details_api(request, word)
        #TESTING CORRECT STATUS CODE HTTP 200
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_slug_word_bad_path_sql_injection(self):
        #bad path
        self.factory = APIRequestFactory()
        word = "`SELECT`*`DROP" #random characters
        url = "/api/word/" + word + "/"
        request = self.factory.get(url, format='json')
        response = word_details_api(request, word)
        #TESTING CORRECT STATUS CODE HTTP 200
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
if __name__ == "__main__":
    test = Testing()
    test.test_database_search()
    test.test_simple_word_search()
    test.test_word_space()
    test.test_not_in_database()
    test.test_word_with_a_path()
    test.test_slug_word_edgecase1()
    test.test_slug_word_edgecase2()
    test.test_slug_word_edgecase3()
    test.test_slug_word_bad_path()
    test.test_slug_word_bad_path_sql_injection()
