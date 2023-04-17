import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def add_user(self, user_name):
        self.cursor.execute("INSERT INTO 'requests' ('user_name') VALUES (?)", (user_name,))

        return self.conn.commit

    def add_or_update_category(self, category):
        # Check if the category already exists
        self.cursor.execute("SELECT * FROM categories WHERE name=?", (category,))
        row = self.cursor.fetchone()

        if row is None:
            # If the category doesn't exist, insert it into the database
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        else:
            # If the category already exists, update it in the database
            self.cursor.execute("UPDATE categories SET name=? WHERE id=?", (category, row[0]))

        # Commit the changes to the database and close the connection
        self.conn.commit()

    def add_comment_and_code(self, comment, code):
        self.cursor.execute("INSERT INTO 'requests' ('comment') VALUES (?)", (comment,))
        self.cursor.execute("INSERT INTO 'requests' ('code') VALUES (?)", (code,))
        return self.conn.commit

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()
