import pytest

from fe import conf
from fe.access.buyer import Buyer
import uuid

from fe.access.new_buyer import register_new_buyer


class TestSearchBook:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_new_search_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = "test_new_search_buyer_id_{}".format(str(uuid.uuid1()))
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.keyword = "hello"

    def test_keyword_search(self):
        content, code = self.buyer.search(self.keyword, "keyword")
        assert code == 200
