import pytest

from api_scripts.common import URLBuilder


URL_ALL = 'http://localhost/abc/def/question?key1=1&key2=2&key3=3'
URL_WITH_PATH = 'http://localhost/abc/def'
URL_BASE = 'http://localhost'
URL_SHORTHAND = 'localhost'


class TestAPIScripts:    
    def test_url_builder_indempotent(self):
        assert URLBuilder(URL_ALL).build() == URL_ALL
        assert URLBuilder(URL_WITH_PATH).build() == URL_WITH_PATH
        assert URLBuilder(URL_BASE).build() == URL_BASE
        assert URLBuilder(URL_SHORTHAND).build() == URL_BASE  # Should automatically append default 'http' scheme on URL shorthand

    def test_url_builder_add_path(self):
        assert URLBuilder(URL_ALL).add_path('ghi').build() == 'http://localhost/abc/def/question/ghi?key1=1&key2=2&key3=3'
        assert URLBuilder(URL_WITH_PATH).add_path('ghi').build() == 'http://localhost/abc/def/ghi'
        assert URLBuilder(URL_BASE).add_path('ghi').build() == 'http://localhost/ghi'

    def test_url_builder_add_existed_query_param(self):
        with pytest.raises(AttributeError):
            URLBuilder(URL_ALL).add_query_param('key1', 10)
            

    def test_url_builder_add_query_param(self):
        u = URLBuilder(URL_WITH_PATH).add_query_param('key1', 1)
        assert u.build() == 'http://localhost/abc/def?key1=1'
        u.add_query_param('key2', 2)
        assert u.build() == 'http://localhost/abc/def?key1=1&key2=2'
            
    def test_url_builder_mixed(self):
        assert URLBuilder(URL_SHORTHAND).add_path('api/v1/question').add_query_param('key1', 1).add_query_param('key2', 2).build() == 'http://localhost/api/v1/question?key1=1&key2=2'
