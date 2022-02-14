import aiosqlite
from modules import customErrors
import os

dbPath = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

async def run(command: str, prepared: iter = ()):
    async with aiosqlite.connect(dbPath) as conn:
        await conn.execute(command, prepared)
        await conn.commit()


async def read(command: str, prepared: iter = ()):
    async with aiosqlite.connect(dbPath) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            cur: aiosqlite.Cursor
            await cur.execute(command, prepared)
            return [dict(x) for x in await cur.fetchall()]


async def newUser(serverID: int, userID: int):
    try:
        await run(f'INSERT INTO "{serverID}" VALUES (?, 0, "")', (userID, ))
    except aiosqlite.IntegrityError:
        raise customErrors.UserAlreadyRegistered
    except aiosqlite.OperationalError:
        raise customErrors.NoServerData

async def newServer(serverID: int, roleID: int):
    try:
        await run('INSERT INTO serversData VALUES (?, "$", 0, ?, ?, null, 0, 1, 0);', (serverID, "", roleID))
        await run(f'CREATE TABLE "{serverID}"("userID" INT, "money" REAL, "items" TEXT, PRIMARY KEY("userID"));', ())
    except aiosqlite.IntegrityError as e:
        raise customErrors.ServerAlreadyRegistered(e)
    except aiosqlite.OperationalError as e:
        raise customErrors.ServerAlreadyRegistered(e)


async def getServerData(serverID: int):
    try:
        data = await read(f'SELECT * FROM "serversData" WHERE serverID=?',
                          (serverID, ))
        return data[0]
    except IndexError:
        raise customErrors.NoServerData


async def setServerData(serverID: int, data: dict):
    await run(f'''UPDATE serversData SET {", ".join([f'"{key}"=?' for key, value in data.items()])} '''
              '''WHERE serverID=?''',
              list(data.values())+[serverID])


async def getUserData(serverID: int, userID: int):
    try:
        data = await read(f'SELECT money, items FROM "{serverID}" WHERE userID=?', (userID, ))
        return data[0]
    except aiosqlite.OperationalError as err:
        if 'no such table: ' in str(err):
            raise customErrors.NoServerData
    except IndexError:
        await newUser(serverID, userID)
        return await getUserData(serverID, userID)


async def setUserData(serverID: int, userID: int, data: dict):
    await run(f'''UPDATE "{serverID}" SET {", ".join([f'"{key}"=?' for key, value in data.items()])} '''
              '''WHERE userID=?''',
              list(data.values())+[userID])


async def getUsersMoney(serverID: int, userID: int):

    serverData = await getServerData(serverID)
    userData = await getUserData(serverID, userID)
    currency = serverData["currency"]
    locate = serverData["locate"]
    if locate == 0:
        return f"{currency}{userData['money']}"
    else:
        return f"{userData['money']}{currency}"

async def getMoney(serverID: int, amount: float, serverData = None):
    if serverData is None:
        serverData = await getServerData(serverID)
    currency = serverData["currency"]
    locate = serverData["locate"]
    if locate == 0:
        return f"{currency}{amount}"
    else:
        return f"{amount}{currency}"

async def addUserMoney(serverID: int, userID: int, amount: float):
    userData = await getUserData(serverID, userID)
    userData["money"] += amount
    await setUserData(serverID, userID, userData)