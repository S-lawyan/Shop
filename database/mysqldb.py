import aiomysql
from bot.config import Settings
from bot.config import config
from loguru import logger
from datetime import datetime
from bot.utils.exceptions import ErrorAddingTrader


class DataBaseService:
    def __init__(self, _config: Settings):
        self.db_pool = None
        self.config = _config

    async def create_pool(self) -> None:
        try:
            self.db_pool = await aiomysql.create_pool(
                host=self.config.db.db_host,
                port=self.config.db.db_port,
                user=self.config.db.db_user,
                password=self.config.db.db_pass.get_secret_value(),
                db=self.config.db.db_name,
                minsize=1,
                maxsize=10,
                autocommit=True
            )
            logger.info("Pool was created successfully!")
        except Exception as e:
            logger.error(f"Ошибка при подключении к БД: {e}")

    async def execute_query(self, query):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                result = await cur.fetchall()
        return result

    async def close(self) -> None:
        self.db_pool.close()
        await self.db_pool.wait_closed()

    async def save_trader(self, tg_id: int, trader_name: str, fio: str) -> None:
        try:
            query = f"""
            INSERT INTO Traders
            (tg_id, trader_name, fio) 
            VALUES 
            ({tg_id}, '{trader_name}', '{fio}')
            """
            await self.execute_query(query=query)
            logger.info(f"Добавлен новый трейдер: {trader_name}, {fio}, {tg_id}")
        except Exception as exc:
            logger.error(f"Ошибка при добавлении трейдера : {exc}")

    async def check_trader(self, tg_id: int):
        try:
            query = f"SELECT * FROM Traders WHERE tg_id = {tg_id}"
            result = await self.execute_query(query=query)
            if len(result) == 0:
                return False
            else:
                return True
        except Exception as exc:
            logger.error(f"Ошибка при : {exc}")

    async def check_shop_name(self, shop_name):
        try:
            query = f"SELECT * FROM Traders WHERE trader_name = '{shop_name}'"
            result = await self.execute_query(query=query)
            if len(result) == 0:
                return False
            else:
                return True
        except Exception as exc:
            logger.error(f"Ошибка при : {exc}")




db = DataBaseService(config)

# try:
#     query = f"""
#
#     """
#     await self.execute_query(query=query)
# except Exception as exc:
#     logger.error(f"Ошибка при : {exc}")