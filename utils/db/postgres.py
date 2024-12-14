from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            max_size=20
        )

    async def execute(self, command, *args, fetch=False, fetchval=False, fetchrow=False, execute=False):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)  # *args bilan argumentlar yuboriladi
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)  # To'g'ri uzatilgan argumentlar
        return result

    # =================== TABLE | LINK =================
    async def create_table_link(self):
        sql = """
        CREATE TABLE IF NOT EXISTS link_table (
            id SERIAL PRIMARY KEY,
            inviter BIGINT NOT NULL,
            new_member BIGINT NOT NULL UNIQUE,
            invite_count INTEGER DEFAULT 0,
            created_at DATE DEFAULT CURRENT_DATE
        );
        """
        await self.execute(sql, execute=True)

    async def add_members(self, inviter, new_member, invite_count):
        sql = "INSERT INTO link_table (inviter, new_member, invite_count) VALUES ($1, $2, $3) returning id"
        return await self.execute(sql, inviter, new_member, invite_count, fetchrow=True)

    async def count_members(self, inviter):
        sql = "SELECT COUNT(*) FROM link_table WHERE inviter = $1"
        return await self.execute(sql, inviter, fetchval=True)

    async def delete_old_links(self):
        sql = "DELETE FROM link_table WHERE created_at != CURRENT_DATE"
        return await self.execute(sql, execute=True)

    async def drop_table_links(self):
        sql = "DROP TABLE link_table"
        return await self.execute(sql, execute=True)

    # =================== TABLE | USERS =================
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            status BOOLEAN DEFAULT TRUE            
        );
        """
        await self.execute(sql, execute=True)

    async def add_user(self, telegram_id):
        sql = "INSERT INTO users (telegram_id) VALUES ($1) returning id"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def update_status_false(self, telegram_id):
        sql = "UPDATE users SET status = FALSE WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT telegram_id FROM users"
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def delete_blockers(self):
        sql = "DELETE FROM users WHERE status = FALSE"
        return await self.execute(sql, execute=True)

    async def drop_table_users(self):
        sql = "DROP TABLE users"
        return await self.execute(sql, execute=True)
