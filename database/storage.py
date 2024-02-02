import asyncio
from bot.config import Settings
from bot.config import config
from loguru import logger

from bot.utils.exceptions import ErrorExecutingESQuery, DocumentIsNotExist
from bot.utils.models import Product

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan
from elasticsearch.helpers import async_bulk


class DataBaseService:
    def __init__(self, _config: Settings):
        self.config = _config
        self.trader_index = _config.es.traders
        self.products_index = _config.es.products
        self.elasticsearch_config = {
            "hosts": [f"http://{self.config.es.es_host}:{self.config.es.es_port}"],
            "basic_auth": (self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
            "maxsize": 50,
            "verify_certs": False
        }

    async def _get_elastic_instance(self) -> AsyncElasticsearch:
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
        finally:
            await elastic.close()

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
        finally:
            await elastic.close()

    async def delete_es_query(self, index: str, document_data: dict):
        try:
            async with await self._get_elastic_instance() as elastic:
                result = await elastic.delete_by_query(index=index, body={"query": {"match": document_data}})
                return result
        except Exception as exc:
            logger.error(f"Ошибка при удалении {index} значение {document_data} : {exc}")
            raise ErrorExecutingESQuery()
        finally:
            await elastic.close()

    async def update_es_query(self, index: str, doc_id: str, document_data: dict):
        try:
            async with await self._get_elastic_instance() as elastic:
                result = await elastic.update(index=index, id=doc_id, body=document_data)
                return result
        except Exception as exc:
            logger.error(f"Ошибка при обновлении поля {index} значение {document_data} : {exc}")
            raise ErrorExecutingESQuery()
        finally:
            await elastic.close()

    # Other methods

    async def save_trader(self, tg_id: int, trader_name: str, fio: str) -> None:
        """

        :param tg_id:
        :param trader_name:
        :param fio:
        :return:
        """
        document_data = {
            "tg_id": tg_id,
            "name": trader_name,
            "fio": fio
        }
        await self.indexing_es_query(index=self.trader_index, document_data=document_data)

    async def check_in_traders_index(self, field: str, value: int | str):
        """

        :param field:
        :param value:
        :return:
        """
        query = {"query": {"term": {field: value}}}  # term - потому что нужно точное совпадение
        response: list = await self.search_es_query(index=self.trader_index, query=query)
        return True if len(response) > 0 else False

    async def check_in_products_index(self, field: str, value: int | str):
        """

        :param field:
        :param value:
        :return:
        """
        query = {"query": {"term": {field: value}}}
        response: list = await self.search_es_query(index=self.products_index, query=query)
        return True if len(response) > 0 else False

    async def save_product(self, product: Product) -> None:
        """

        :param product:
        :return:
        """
        document_data = {
            "article": product.article,
            "count": product.quantity,
            "price": product.price,
            "product_name": product.product_name,
            "trader_id": product.trader_id
        }
        await self.indexing_es_query(index=self.products_index, document_data=document_data)
        logger.info(
            f"""
            Пользователем {product.trader_id} добавлен новый товар\n{product.article}\n
            {product.product_name}\n{product.price}\n{product.quantity}
            """
        )

    async def delete_product(self, article: int) -> None:
        """

        :param article:
        :return:
        """
        document_data = {
            "article": article,
        }
        await self.delete_es_query(index=self.products_index, document_data=document_data)
        logger.info(f"Товар {article} удален.")

    async def update_product_document(self, article: str, update_field: str, update_value: int | str):
        """

        :param article:
        :param update_field:
        :param update_value:
        :return:
        """
        query = {"query": {"term": {"article": article}}}
        response = await self.search_es_query(index=self.products_index, query=query)
        if response[0]["_source"]:
            doc_id = response[0]["_id"]
            update_data = {"doc": {update_field: update_value}}
            await self.update_es_query(index=self.products_index, doc_id=doc_id, document_data=update_data)
            logger.info(f"Поле {update_field} в документе с article={article} успешно обновлено.")
        else:
            logger.error(f"Документ с article={article} не был найден.")
            raise DocumentIsNotExist()

    async def get_trader_products(self, trader_id: int) -> list:
        """

        :param trader_id:
        :return:
        """
        query = {"query": {"term": {"trader_id": trader_id}}}
        response = await self.search_es_query(index=self.products_index, query=query)
        documents = await pars_products(response=response)
        return documents

    # async def save_bulk_products(self, products: list[Product]) -> None:
    #     try:
    #         for product in products:
    #             document_data = {
    #                 "product_name": product.product_name,
    #                 "price": product.price,
    #                 "article": product.article,
    #                 "count": product.quantity,
    #                 "trader_id": product.trader_id
    #             }
    #             await self.indexing_es_query(index=self.products_index, document_data=document_data)
    #         logger.info(f"Успешно проиндексировано документов : {len(products)}")
    #     except (Exception,) as exc:
    #         logger.error(f"Ошибка добавление позиций bulk : {exc}")

    async def save_bulk_products(self, products: list[Product]) -> None:
        try:
            actions: list = []
            for product in products:
                actions.append(
                    {
                        "_op_type": "index",  # Операция (index, create, update, delete)
                        "_index": "products_alias",
                        "_source": {
                            "product_name": product.product_name,
                            "price": product.price,
                            "article": product.article,
                            "count": product.quantity,
                            "trader_id": product.trader_id
                        }
                    }
                )
            elastic: AsyncElasticsearch = await self._get_elastic_instance()
            success, failed = await async_bulk(
                client=elastic,
                index="products_alias",
                actions=actions
            )
            # TODO посмотреть что возвращает список, возможно получится разделить успешные и неуспешные строки
            logger.info(f"Успешно проиндексировано документов : {len(products)}")
        except (Exception,) as exc:
            logger.error(f"Ошибка добавление позиций bulk : {exc}")
        finally:
            await elastic.close()


async def pars_products(response: list[dict]) -> list[Product]:
    return [pars_product(product) for product in response]


def pars_product(product: dict) -> Product:
    _product = Product()
    source: dict = product["_source"]
    _product.product_name = str(source["product_name"])
    _product.price = float(source["price"])
    _product.quantity = int(source["count"]) if source.get("count", None) is not None else "♾"
    _product.article = int(source["article"])
    _product.trader_id = int(source["trader_id"])
    return _product


es = DataBaseService(config)
