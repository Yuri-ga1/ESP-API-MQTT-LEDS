import sqlite3
import asyncio
from fastapi import HTTPException
from device.schemas import Device
from users.schemas import User
from colors.schemas import *


class Database:

    def __init__(self, db_name: str = "user_control"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    async def connect(self):
        print("create connection")
        self.connection = sqlite3.connect(f"{self.db_name}.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                MAC_addres TEXT
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                color_name TEXT NOT NULL,
                red INT DEFAULT 0,
                green INT DEFAULT 0,
                blue INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                device_id INT, 
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_colors_combination (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                color_id INT,
                `order` INT, 
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (color_id) REFERENCES colors (id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                device_id INT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        """
        )

        self.connection.commit()
        return self.cursor

    async def disconnect(self):
        print("disconnect")
        self.connection.close()

    async def is_user_exists(self, nickname: str) -> bool:
        self.cursor.execute(
            """
            SELECT nickname FROM users WHERE nickname=? 
            """,
            (nickname,),
        )

        result = self.cursor.fetchall()

        if result:
            return True
        return False

    async def get_user_id(self, nickname: str):
        if await self.is_user_exists(nickname):
            self.cursor.execute(
                """
                SELECT id FROM users WHERE nickname=? 
                """,
                (f"{nickname}",),
            )
            return self.cursor.fetchone()[0]
        else:
            raise HTTPException(status_code=404, detail=f"User {nickname} not found")

    async def create_new_user(self, user: User):
        print(self.cursor)
        print(self.connection)
        if await self.is_user_exists(user.nickname):
            raise HTTPException(status_code=409, detail="User already exists")

        self.cursor.execute(
            """
            INSERT INTO `users`
            (nickname)
            VALUES (?)""",
            (user.nickname,),
        )
        self.connection.commit()

    async def is_device_exists(self, mac: str) -> bool:
        self.cursor.execute(
            """
            SELECT MAC_addres FROM devices WHERE MAC_addres=? 
            """,
            (f"{mac}",),
        )

        result = self.cursor.fetchall()

        if result:
            return True
        return False

    async def get_device_id(self, mac: str):
        if await self.is_device_exists(mac):
            self.cursor.execute(
                """
                SELECT id FROM devices WHERE MAC_addres=? 
                """,
                (f"{mac}",),
            )
            return self.cursor.fetchone()[0]
        else:
            raise HTTPException(
                status_code=404, detail=f"Device with mac: {mac} not found"
            )

    async def register_device(self, device: Device):
        if await self.is_device_exists(device.mac):
            print("Девайс уже есть в БД")
        else:
            self.cursor.execute(
                """
                INSERT INTO `devices`
                (device_name, MAC_addres)
                VALUES (?, ?)""",
                (device.name, device.mac),
            )
            self.connection.commit()

        device_id = await self.get_device_id(device.mac)
        user_id = await self.get_user_id(device.owner)

        print(user_id, device_id)

        self.cursor.execute(
            """
            INSERT INTO `user_devices`
            (user_id, device_id)
            VALUES (?, ?)""",
            (
                user_id,
                device_id,
            ),
        )
        self.connection.commit()

    async def is_color_exists(self, owner: str, color_name: str) -> bool:
        user_id = await self.get_user_id(owner)
        self.cursor.execute(
            """
            SELECT * FROM colors WHERE user_id=? AND color_name=? 
            """,
            (user_id, color_name),
        )

        result = self.cursor.fetchall()

        if result:
            return True
        return False

    async def get_color_id(self, owner: str, color_name: str):
        if await self.is_color_exists(owner, color_name):
            user_id = await self.get_user_id(owner)
            self.cursor.execute(
                """
                SELECT id FROM colors WHERE user_id=? AND color_name=?
                """,
                (user_id, color_name),
            )
            return self.cursor.fetchone()[0]
        else:
            raise HTTPException(status_code=404, detail=f"Color {color_name} not found")

    async def add_new_color(self, color: Color):
        if await self.is_color_exists(color.owner, color.name):
            raise HTTPException(
                status_code=409, detail=f"Color {color.name} already exists"
            )

        for color_value in [color.red, color.green, color.blue]:
            if not 0 <= color_value <= 255:
                raise HTTPException(
                    status_code=400,
                    detail="Value error. Color value must be >0 and <255",
                )

        user_id = await self.get_user_id(color.owner)

        self.cursor.execute(
            """
            INSERT INTO `colors`
            (user_id, color_name, red, green, blue)
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, color.name, color.red, color.green, color.blue),
        )
        self.connection.commit()

    async def create_colors_combination(self, colors_comb: Colors_combination):
        user_id = await self.get_user_id(colors_comb.owner)
        colors = colors_comb.colors
        owner = colors_comb.owner

        for order, color_name in enumerate(colors, start=1):
            color_id = await self.get_color_id(owner, color_name)

            self.cursor.execute(
                """
                INSERT INTO `user_colors_combination`
                (user_id, color_id, `order`)
                VALUES (?, ?, ?)""",
                (
                    user_id,
                    color_id,
                    order,
                ),
            )

            self.connection.commit()

    async def get_user_colors(self, username: str) -> List[Color]:
        user_id = await self.get_user_id(username)
        self.cursor.execute(
            """
            SELECT color_name, red, green, blue FROM colors WHERE user_id=?
            """,
            (user_id,),
        )
        request = self.cursor.fetchall()

        colors_list = []

        for r in request:
            color = Color(name=r[0], owner=username, red=r[1], green=r[2], blue=r[3])
            colors_list.append(color)

        return colors_list


database = Database()
