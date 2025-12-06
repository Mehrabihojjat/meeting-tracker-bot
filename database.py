"""
Database layer for Meeting Tracker Bot using SQLite
"""
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def init_database(self):
        """Initialize database and create tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                title TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                participants_count INTEGER NOT NULL,
                time_of_day TEXT NOT NULL,
                meeting_type TEXT NOT NULL,
                team_name TEXT NOT NULL,
                is_team_lead BOOLEAN NOT NULL,
                satisfaction_rating INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_meeting(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        title: str,
        duration_minutes: int,
        participants_count: int,
        time_of_day: str,
        meeting_type: str,
        team_name: str,
        is_team_lead: bool,
        satisfaction_rating: int
    ) -> int:
        """Add a new meeting record"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO meetings (
                user_id, username, first_name, last_name, title,
                duration_minutes, participants_count, time_of_day,
                meeting_type, team_name, is_team_lead, satisfaction_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, username, first_name, last_name, title,
            duration_minutes, participants_count, time_of_day,
            meeting_type, team_name, is_team_lead, satisfaction_rating
        ))

        meeting_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return meeting_id

    def get_user_meetings(self, user_id: int) -> List[Dict]:
        """Get all meetings for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM meetings
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))

        meetings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return meetings

    def user_logged_today(self, user_id: int) -> bool:
        """Check if user has logged any meeting today"""
        conn = self.get_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()

        cursor.execute('''
            SELECT COUNT(*) as count FROM meetings
            WHERE user_id = ?
            AND DATE(created_at) = DATE(?)
        ''', (user_id, today))

        result = cursor.fetchone()
        conn.close()

        return result['count'] > 0

    def get_all_users(self) -> List[int]:
        """Get all unique user IDs who have logged meetings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT user_id FROM meetings
        ''')

        users = [row['user_id'] for row in cursor.fetchall()]
        conn.close()

        return users

    # Statistics queries for /report command

    def get_total_meetings_count(self) -> int:
        """Get total number of meetings logged"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM meetings')
        result = cursor.fetchone()
        conn.close()

        return result['count']

    def get_unique_users_count(self) -> int:
        """Get number of unique users"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM meetings')
        result = cursor.fetchone()
        conn.close()

        return result['count']

    def get_average_satisfaction(self) -> float:
        """Get overall average satisfaction rating"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT AVG(satisfaction_rating) as avg FROM meetings')
        result = cursor.fetchone()
        conn.close()

        return round(result['avg'], 2) if result['avg'] else 0

    def get_satisfaction_by_time(self) -> Dict[str, float]:
        """Get average satisfaction by time of day"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT time_of_day, AVG(satisfaction_rating) as avg
            FROM meetings
            GROUP BY time_of_day
        ''')

        results = {row['time_of_day']: round(row['avg'], 2) for row in cursor.fetchall()}
        conn.close()

        return results

    def get_meetings_count_by_time(self) -> Dict[str, int]:
        """Get meeting count by time of day"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT time_of_day, COUNT(*) as count
            FROM meetings
            GROUP BY time_of_day
        ''')

        results = {row['time_of_day']: row['count'] for row in cursor.fetchall()}
        conn.close()

        return results

    def get_total_hours(self) -> float:
        """Get total hours spent in meetings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(duration_minutes) as total FROM meetings')
        result = cursor.fetchone()
        conn.close()

        total_minutes = result['total'] if result['total'] else 0
        return round(total_minutes / 60, 2)

    def get_average_hours_per_person(self) -> float:
        """Get average hours per person"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT AVG(total_minutes) as avg FROM (
                SELECT user_id, SUM(duration_minutes) as total_minutes
                FROM meetings
                GROUP BY user_id
            )
        ''')

        result = cursor.fetchone()
        conn.close()

        avg_minutes = result['avg'] if result['avg'] else 0
        return round(avg_minutes / 60, 2)

    def get_top_users_by_hours(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get top users by total meeting hours"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COALESCE(first_name || ' ' || last_name, username, CAST(user_id AS TEXT)) as name,
                SUM(duration_minutes) / 60.0 as hours
            FROM meetings
            GROUP BY user_id
            ORDER BY hours DESC
            LIMIT ?
        ''', (limit,))

        results = [(row['name'], round(row['hours'], 2)) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_team_statistics(self) -> List[Dict]:
        """Get statistics by team"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                team_name,
                COUNT(*) as meeting_count,
                SUM(duration_minutes) / 60.0 as total_hours,
                AVG(satisfaction_rating) as avg_satisfaction
            FROM meetings
            GROUP BY team_name
            ORDER BY total_hours DESC
        ''')

        results = [{
            'team': row['team_name'],
            'meetings': row['meeting_count'],
            'hours': round(row['total_hours'], 2),
            'satisfaction': round(row['avg_satisfaction'], 2)
        } for row in cursor.fetchall()]

        conn.close()
        return results

    def get_meeting_type_statistics(self) -> List[Dict]:
        """Get statistics by meeting type"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                meeting_type,
                COUNT(*) as count,
                AVG(satisfaction_rating) as avg_satisfaction
            FROM meetings
            GROUP BY meeting_type
            ORDER BY count DESC
        ''')

        results = [{
            'type': row['meeting_type'],
            'count': row['count'],
            'satisfaction': round(row['avg_satisfaction'], 2)
        } for row in cursor.fetchall()]

        conn.close()
        return results

    def get_user_statistics(self, user_id: int) -> Dict:
        """Get statistics for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_meetings,
                SUM(duration_minutes) / 60.0 as total_hours,
                AVG(satisfaction_rating) as avg_satisfaction,
                AVG(duration_minutes) as avg_duration
            FROM meetings
            WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row and row['total_meetings'] > 0:
            return {
                'total_meetings': row['total_meetings'],
                'total_hours': round(row['total_hours'], 2),
                'avg_satisfaction': round(row['avg_satisfaction'], 2),
                'avg_duration': round(row['avg_duration'], 2)
            }

        return None


# Create a singleton instance
db = Database()
