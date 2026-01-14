"""
Lessons Learned Database
Each agent learns from errors and successful solutions
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class LessonsLearned:
    """Database for storing and retrieving lessons learned"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to memory directory
            db_path = Path(__file__).parent.parent.parent / "memory" / "lessons.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS lessons_learned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT,
                context TEXT,
                solution TEXT,
                success BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_error 
            ON lessons_learned(agent_name, error_type)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_success 
            ON lessons_learned(success, agent_name)
        """)
        
        self.conn.commit()
    
    def record_error(self, agent_name: str, error_type: str, 
                    error_msg: str, context: str, metadata: Dict = None):
        """Record an error that occurred"""
        self.conn.execute("""
            INSERT INTO lessons_learned 
            (agent_name, error_type, error_message, context, success, metadata)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (
            agent_name, 
            error_type, 
            error_msg, 
            context,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
    
    def record_solution(self, agent_name: str, error_type: str, 
                       solution: str, context: str = None, metadata: Dict = None):
        """Record a successful solution"""
        self.conn.execute("""
            INSERT INTO lessons_learned 
            (agent_name, error_type, solution, context, success, metadata)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (
            agent_name, 
            error_type, 
            solution,
            context,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
    
    def get_solutions(self, agent_name: str, error_type: str, 
                     limit: int = 5) -> List[Dict]:
        """Get successful solutions for a specific error type"""
        cursor = self.conn.execute("""
            SELECT solution, context, timestamp, metadata
            FROM lessons_learned
            WHERE agent_name = ? 
            AND error_type = ?
            AND success = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_name, error_type, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'solution': row['solution'],
                'context': row['context'],
                'timestamp': row['timestamp'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None
            })
        
        return results
    
    def has_seen_error(self, agent_name: str, error_type: str) -> bool:
        """Check if this error has been seen before"""
        cursor = self.conn.execute("""
            SELECT COUNT(*) as count FROM lessons_learned
            WHERE agent_name = ? AND error_type = ?
        """, (agent_name, error_type))
        
        return cursor.fetchone()['count'] > 0
    
    def get_error_count(self, agent_name: str, error_type: str) -> int:
        """Get how many times this error occurred"""
        cursor = self.conn.execute("""
            SELECT COUNT(*) as count FROM lessons_learned
            WHERE agent_name = ? AND error_type = ? AND success = 0
        """, (agent_name, error_type))
        
        return cursor.fetchone()['count']
    
    def get_all_lessons(self, agent_name: str = None, 
                       success_only: bool = True) -> List[Dict]:
        """Get all lessons, optionally filtered by agent"""
        query = """
            SELECT agent_name, error_type, error_message, solution, 
                   context, success, timestamp, metadata
            FROM lessons_learned
            WHERE 1=1
        """
        params = []
        
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)
        
        if success_only:
            query += " AND success = 1"
        
        query += " ORDER BY timestamp DESC"
        
        cursor = self.conn.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'agent_name': row['agent_name'],
                'error_type': row['error_type'],
                'error_message': row['error_message'],
                'solution': row['solution'],
                'context': row['context'],
                'success': bool(row['success']),
                'timestamp': row['timestamp'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None
            })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about lessons learned"""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as solutions,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as errors,
                COUNT(DISTINCT agent_name) as agents,
                COUNT(DISTINCT error_type) as error_types
            FROM lessons_learned
        """)
        
        row = cursor.fetchone()
        
        return {
            'total_entries': row['total'],
            'solutions': row['solutions'],
            'errors': row['errors'],
            'unique_agents': row['agents'],
            'unique_error_types': row['error_types']
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()
