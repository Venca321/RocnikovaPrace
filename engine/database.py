
from datetime import datetime, timedelta
import sqlite3, uuid, random

class User:
    def __init__(self, id:str, username:str, gesture:int):
        self.id = id
        self.username = username
        self.gesture = gesture

class Session:
    def __init__(self, id:str, user1_id:str, user_1_status:int, user2_id:str, user_2_status:int):
        self.id = id
        self.user1_id = user1_id
        self.user1_status = user_1_status
        self.user2_id = user2_id
        self.user2_status = user_2_status

class UserStatusEnums:
    WAITING = 0
    READY = 1
    PLAYING = 2
    WINNER = 3
    LOSER = 4
    TIED = 5

class Database:
    def __init__(self, file_location:str="database.db"):
        self.connection = sqlite3.connect(file_location)
        self.cursor = self.connection.cursor()

    def push(self):
        """
        Push changes to database
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT,
                gesture integer,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )'''
        )

        self.cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_user_timestamp
            AFTER UPDATE ON users
            FOR EACH ROW
            BEGIN
                UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user1_id text, 
                user1_status integer, 
                user2_id text, 
                user2_status integer,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )'''
        )

        self.cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_sessions_timestamp
            AFTER UPDATE ON sessions
            FOR EACH ROW
            BEGIN
                UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;'''
        )
        self.connection.commit()

    def create_user(self, username:str, gesture:int) -> User:
        """
        Create user from username
        """
        user_id = str(uuid.uuid4())
        self.cursor.execute("insert into users (id, username, gesture) values (?, ?, ?)", (user_id, username, gesture))
        self.connection.commit()
        return User(user_id, username, gesture)

    def get_user(self, user_id:str) -> User:
        """
        Get user from id
        """
        self.cursor.execute("select * from users where id=:id", {"id": user_id})
        user = self.cursor.fetchone()
        return User(user[0], user[1], user[2])

    def update_user(self, user:User, gesture:int) -> User:
        """
        Update users gesture
        """
        self.cursor.execute("update users set gesture=:gesture where id=:id", {"gesture": gesture, "id": user.id})
        self.connection.commit()
        return User(user.id, user.username, gesture)

    def remove_old_users(self):
        """
        Remove users that are not connected anymore
        """
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        five_minutes_ago = five_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("DELETE FROM users WHERE updated_at < ?", (five_minutes_ago,))
        self.connection.commit()

    def create_session(self, user1_id, user2_id) -> Session:
        """
        Create session
        """
        session_id = str(random.randint(100000, 9999999))
        self.cursor.execute("insert into sessions (id, user1_id, user1_status, user2_id, user2_status) values (?, ?, ?, ?, ?)", (session_id, user1_id, UserStatusEnums.WAITING, user2_id, UserStatusEnums.WAITING))
        self.connection.commit()
        return Session(session_id, user2_id, UserStatusEnums.WAITING, user2_id, UserStatusEnums.WAITING)

    def get_session(self, session_id:str) -> Session:
        """
        Get session from id
        """
        self.cursor.execute("select * from sessions where id=:id", {"id": session_id})
        session = self.cursor.fetchone()
        return Session(session[0], session[1], session[2], session[3], session[4])

    def update_session(self, session:Session, user1_status:int, user2_status:int) -> Session:
        """
        Update session
        """
        self.cursor.execute("update sessions set user1_status=:user1_status, user2_status=:user2_status where id=:id", {"user1_status": user1_status, "user2_status": user2_status, "id": session.id})
        self.connection.commit()
        return Session(session.id, session.user1_id, user1_status, session.user2_id, user2_status)

    def remove_old_sessions(self):
        """
        Remove sessions that are not connected anymore
        """
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        self.cursor.execute("DELETE FROM sessions WHERE updated_at < ?", (five_minutes_ago,))
        self.connection.commit()