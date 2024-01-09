import asyncio
from bot.config import Settings
from bot.config import config
from loguru import logger

from bot.utils.exceptions import ErrorExecutingESQuery
from bot.utils.models import Product

from elasticsearch import AsyncElasticsearch


class DataBaseService:
    def __init__(self, _config: Settings):
        self.config = _config
        self.trader_index = "traders-2024-01-01"
        self.products_index = "products-2024-01-01"

    async def es_healthcheck(self) -> None:
        async with AsyncElasticsearch(
            hosts=["http://192.168.197.128:9200"],
            basic_auth=(self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
            maxsize=50,
            verify_certs=False
        ) as elastic:
            for attempt in range(config.es.connection_attempt):
                try:
                    if await elastic.ping():
                        logger.info("Elastic connect was created successfully!")
                        break
                    else:
                        logger.error("Ping return False")
                except Exception as e:
                    logger.error(f"Ошибка при подключении к Elasticsearch: {e}")
                await asyncio.sleep(5)

    async def indexing_es_query(self, index: str, document_data: dict = None):
        async with AsyncElasticsearch(
                hosts=["http://192.168.197.128:9200"],
                basic_auth=(self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
                maxsize=50,
                verify_certs=False
        ) as elastic:
            result = await elastic.index(index=index, document=document_data)
            return result

    async def search_es_query(self, index: str, query: dict = None):
        async with AsyncElasticsearch(
                hosts=["http://192.168.197.128:9200"],
                basic_auth=(self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
                maxsize=50,
                verify_certs=False
        ) as elastic:
            result = await elastic.search(index=index, body=query)
            return result

    async def delete_es_query(self, index: str, document_data: dict):
        async with AsyncElasticsearch(
                hosts=["http://192.168.197.128:9200"],
                basic_auth=(self.config.es.es_user, self.config.es.es_pass.get_secret_value()),
                maxsize=50,
                verify_certs=False
        ) as elastic:
            result = await elastic.delete_by_query(index=index, body={"query": {"match": document_data}})
            return result

    async def save_trader(self, tg_id: int, trader_name: str, fio: str) -> None:
        """

        :param tg_id:
        :param trader_name:
        :param fio:
        :return:
        """
        try:
            document_data = {
                "tg_id": tg_id,
                "name": trader_name,
                "fio": fio
            }
            await self.indexing_es_query(index=self.trader_index, document_data=document_data)
        except Exception as exc:
            logger.error(f"Ошибка при сохранении продавца : {exc}")

    async def check_in_traders_index(self, field: str, value: int | str):
        """

        :param field:
        :param value:
        :return:
        """
        try:
            query = {"query": {"match": {field: value}}}
            response = await self.search_es_query(index=self.trader_index, query=query)
            return True if len(response["hits"]["hits"]) > 0 else False
        except Exception as exc:
            logger.error(f"Ошибка при проверке {field} значение {value} : {exc}")

    async def check_in_products_index(self, field: str, value: int | str):
        """

        :param field:
        :param value:
        :return:
        """
        try:
            query = {"query": {"match": {field: value}}}
            response = await self.search_es_query(index=self.products_index, query=query)
            return True if len(response["hits"]["hits"]) > 0 else False
        except Exception as exc:
            logger.error(f"Ошибка при проверке {field} значение {value} : {exc}")

    async def save_product(self, product: Product) -> None:
        try:
            document_data = {
                "article": product.article,
                "count": product.quantity,
                "price": product.price,
                "product_name": product.product_name,
                "trader_id": product.trader_id
            }
            await self.indexing_es_query(index=self.products_index, document_data=document_data)
        except Exception as exc:
            logger.error(f"Ошибка при сохранении товара : {exc}")

    async def delete_products(self, article: int, trader_id: int) -> None:
        try:
            document_data = {
                "article": article,
                "trader_id": trader_id
            }
            await self.delete_es_query(index=self.products_index, document_data=document_data)
        except Exception as exc:
            logger.error(f"Ошибка при удалении товара : {exc}")

    async def delete_document(self, elasticsearch_url, index_name, document_id):
        url = f"{elasticsearch_url}/{index_name}/_doc/{document_id}"
        return await self.execute_es_query(url, 'DELETE')

    async def search_documents(self, elasticsearch_url, index_name, query_data):
        url = f"{elasticsearch_url}/{index_name}/_search"
        return await self.execute_es_query(url, 'POST', query_data)




    #
    # async def check_shop_name(self, shop_name):
    #     try:
    #         query = f"SELECT * FROM Traders WHERE trader_name = '{shop_name}'"
    #         result = await self.execute_query(query=query)
    #         if len(result) == 0:
    #             return False
    #         else:
    #             return True
    #     except Exception as exc:
    #         logger.error(f"Ошибка при проверке дубликата названия магазина : {exc}")
    #
    # async def check_unique_article(self, article: int):
    #     try:
    #         query = f"""SELECT * FROM Products WHERE article={article} ORDER BY article ASC;"""
    #         result = await self.execute_query(query=query)
    #         if len(result) == 0:
    #             return False
    #         else:
    #             return True
    #     except Exception as exc:
    #         logger.error(f"Ошибка проверки артикула : {exc}")
    #
    # async def save_product(self, product: Product):
    #     try:
    #         query = f"""
    #         INSERT INTO Products (product_name, price, quantity_product, article, trader_id)
    #         VALUES
    #         ('{product.product_name}',
    #         {product.price},
    #         {product.quantity if product.quantity is not None else "NULL"},
    #         {product.article},
    #         {product.trader_id})
    #         """
    #         await self.execute_query(query=query)
    #         logger.info(f"""Добавлен товар : ('{product.product_name}', {product.price}, {product.quantity}, {product.article}, {product.trader_id})""")
    #     except Exception as exc:
    #         logger.error(f"Ошибка при добавлении товара : {exc}")
    #
    # async def delete_product(self, trader_id: int, article: int):
    #     try:
    #         query = f"""
    #             DELETE FROM Products WHERE article={article} and trader_id={trader_id}
    #         """
    #         await self.execute_query(query=query)
    #         logger.info(f"Удален товар : {article} {trader_id}")
    #     except Exception as exc:
    #         logger.error(f"Ошибка при удалении товара : {exc}")
    #
    # async def get_trader_products(self, trader_id: int):
    #     try:
    #         query = f""" SELECT product_name, price, quantity_product, article, trader_id FROM Products WHERE trader_id={trader_id} """
    #         result = list(await self.execute_query(query=query))
    #         return await pars_products(result)
    #     except Exception as exc:
    #         logger.error(f"Ошибка при получении товаров продавца : {exc}")
    #
    # async def update_new_price(self, article: int, price: float):
    #     try:
    #         query = f"""
    #             UPDATE Products SET price={price} WHERE article={article}
    #         """
    #         await self.execute_query(query=query)
    #         logger.info(f"Обновлена цена товара {article} - {price}")
    #     except Exception as exc:
    #         logger.error(f"Ошибка при обновлении цены {article} {price} : {exc}")
    #
    # async def update_new_count(self, article: int, count: int):
    #     try:
    #         query = f"""
    #             UPDATE Products SET quantity_product={count} WHERE article={article}
    #         """
    #         await self.execute_query(query=query)
    #         logger.info(f"Обновлено количество товара {article} - {count}")
    #     except Exception as exc:
    #         logger.error(f"Ошибка при изменении количества {article} {count} : {exc}")


async def pars_products(result: list[tuple]) -> list[Product]:
    return [pars_product(product) for product in result]


def pars_product(product: tuple) -> Product:
    _product = Product()
    _product.product_name = str(product[0])
    _product.price = float(product[1])
    _product.quantity = int(product[2]) if product[2] is not None else "♾"
    _product.article = int(product[3])
    _product.trader_id = int(product[4])
    return _product


es = DataBaseService(config)

# try:
#     query = f"""
#
#     """
#     await self.execute_query(query=query)
# except Exception as exc:
#     logger.error(f"Ошибка при : {exc}")
