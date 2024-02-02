import asyncio
from bot.config import Settings
from bot.config import config
from loguru import logger

from bot.utils.exceptions import ErrorExecutingESQuery
from bot.utils.models import Product

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan


class DataBaseService:
    def __init__(self, _config: Settings):
        self.config = _config
        self.consumer_index = _config.es.consumers
        self.products_index = _config.es.products
        self.elasticsearch_config = {
            "hosts": [f"http://{self.config.es.es_host}:{self.config.es.es_port}"],
            "basic_auth": (self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
            "maxsize": 50,
            "verify_certs": False
        }

    async def _get_elastic_instance(self):
        return AsyncElasticsearch(**self.elasticsearch_config)

    async def es_healthcheck(self) -> None:
        async with await self._get_elastic_instance() as elastic:
            for attempt in range(config.es.connection_attempt):
                try:
                    if await elastic.ping():
                        logger.warning("Elastic connect was created successfully!")
                        break
                    else:
                        logger.error("Ping return False")
                except Exception as e:
                    logger.error(f"Ошибка при подключении к Elasticsearch: {e}")
                await asyncio.sleep(5)

    async def indexing_es_query(self, index: str, document_data: dict = None):
        try:
            async with await self._get_elastic_instance() as elastic:
                result = await elastic.index(index=index, document=document_data)
                return result
        except Exception as exc:
            logger.error(f"Ошибка при индексации документа {index} значение {document_data} : {exc}")
            raise ErrorExecutingESQuery()

    async def search_es_query(self, index: str, query: dict = None):
        try:
            async with await self._get_elastic_instance() as elastic:
                # result = await elastic.search(index=index, body=query)
                result = []
                async for doc in async_scan(
                    client=elastic,
                    index=index,
                    query=query,
                ):
                    result.append(doc)
                return result
        except Exception as exc:
            logger.error(f"Ошибка при поиске {index} запрос {query} : {exc}")
            raise ErrorExecutingESQuery()

    async def delete_es_query(self, index: str, document_data: dict):
        try:
            async with await self._get_elastic_instance() as elastic:
                result = await elastic.delete_by_query(index=index, body={"query": {"match": document_data}})
                return result
        except Exception as exc:
            logger.error(f"Ошибка при удалении {index} значение {document_data} : {exc}")
            raise ErrorExecutingESQuery()

    async def update_es_query(self, index: str, doc_id: str, document_data: dict):
        try:
            async with await self._get_elastic_instance() as elastic:
                result = await elastic.update(index=index, id=doc_id, body=document_data)
                return result
        except Exception as exc:
            logger.error(f"Ошибка при обновлении поля {index} значение {document_data} : {exc}")
            raise ErrorExecutingESQuery()

    # Other methods

    async def save_consumer(self, tg_id: int, fio: str) -> None:
        """

        :param tg_id:
        :param fio:
        :return:
        """
        document_data = {
            "tg_id": tg_id,
            "fio": fio
        }
        await self.indexing_es_query(index=self.consumer_index, document_data=document_data)

    async def check_in_consumers_index(self, field: str, value: int | str):
        """

        :param field:
        :param value:
        :return:
        """
        query = {"query": {"term": {field: value}}}  # term - потому что нужно точное совпадение
        response: list = await self.search_es_query(index=self.consumer_index, query=query)
        return True if len(response) > 0 else False

    async def search_products_poll(self, request: str):
        # query: dict = {
        #     "query": {
        #         "match": {
        #             "product_name": {
        #                 "query": f"{request}",
        #                 "analyzer": "product_name_analizer"
        #             }
        #         }
        #     }
        # }
        query: dict = {
            "query": {
                "query_string": {
                    "default_field": "product_name",
                    "default_operator": "AND",
                    "query": request
                }
            },
            "size": 200
        }
        response = await self.search_es_query(index=self.products_index, query=query)
        documents = await _pars_products(response=response)
        return documents


async def _pars_products(response: list[dict]) -> list[Product]:
    return [_pars_product(product) for product in response]


def _pars_product(product: dict) -> Product:
    _product = Product()
    source: dict = product["_source"]
    _product.product_name = str(source["product_name"])
    _product.price = float(source["price"])
    _product.quantity = int(source["count"]) if source.get("count", None) is not None else "♾"
    _product.article = int(source["article"])
    _product.trader_id = int(source["trader_id"])
    return _product
