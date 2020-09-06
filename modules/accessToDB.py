import sqlite3
import aiosqlite
import io


async def run(command: str, prepared: iter = ()):
    async with aiosqlite.connect("data/data.db") as conn:
        await conn.execute(command, prepared)
        await conn.commit()


async def read(command: str, prepared: iter = ()):
    async with aiosqlite.connect("data/data.db") as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            cur: aiosqlite.Cursor
            await cur.execute(command, prepared)
            return await cur.fetchall()


async def newServer(serverID: int, roleID: int):
    await run('INSERT INTO serversData VALUES (?, "$", 0, ?, ?);', (serverID, "", roleID))
    await run(f'CREATE TABLE "{serverID}"("userID" INT, "money" REAL, "items" TEXT, PRIMARY KEY("userID"));', ())


async def newUser(serverID: int, userID: int):
    await run(f'INSERT INTO "{serverID}" VALUES (?, 0, "")', (userID, ))


async def getUserData(serverID: int, userID: int):
    return await read(f'SELECT money, items FROM "{serverID}" WHERE userID=?', (userID, ))


async def getServerData(serverID: int):
    return await read(f'SELECT currency, locate, customItems, controlRoleID FROM "serversData" WHERE serverID=?', (serverID, ))


async def setServerData(serverID: int, currency: int, locate: int, customItems: str, controlRoleID: int):
    await run(f'')