#!/usr/bin/env python3
"""
Unit tests for Claude Orchestrator

Tests the core orchestration logic for platform discovery and database operations.
"""

import pytest
import sqlite3
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from claude_orchestrator import ClaudeOrchestrator


class TestClaudeOrchestrator:
    """Tests for ClaudeOrchestrator class"""

    def test_init_with_local_sqlite_when_no_turso_env(self):
        """Test that orchestrator defaults to local SQLite when Turso env vars not set"""
        # Arrange - Clear Turso env vars
        with patch.dict(os.environ, {}, clear=True):
            # Act
            orch = ClaudeOrchestrator(db_path='data/test_arbitrage.db')

            # Assert
            assert orch.use_turso is False
            assert orch.db_path == 'data/test_arbitrage.db'
            assert orch.turso_client is None

    def test_init_with_turso_when_env_vars_set(self):
        """Test that orchestrator uses Turso when env vars are set"""
        # Arrange
        with patch.dict(os.environ, {
            'TURSO_URL': 'libsql://test.turso.io',
            'TURSO_TOKEN': 'test_token'
        }):
            # Act
            orch = ClaudeOrchestrator()

            # Assert
            assert orch.use_turso is True
            assert orch.turso_url == 'libsql://test.turso.io'
            assert orch.turso_token == 'test_token'

    def test_save_platform_to_local_succeeds_with_valid_data(self):
        """Test that saving platform to local SQLite works with valid data"""
        # Arrange
        test_db = 'data/test_save.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        orch = ClaudeOrchestrator(db_path=test_db, use_turso=False)

        # Create table
        conn = sqlite3.connect(test_db)
        conn.execute("""
            CREATE TABLE local_platforms (
                id INTEGER PRIMARY KEY,
                region TEXT, country TEXT, name TEXT, url TEXT,
                type TEXT, language TEXT, description TEXT, data_source TEXT
            )
        """)
        conn.close()

        platform_data = {
            'region': 'Romania',
            'country': 'Romania',
            'name': 'Test Platform',
            'url': 'https://test.com',
            'type': 'forum',
            'language': 'Romanian',
            'description': 'Test description'
        }

        # Act
        orch._save_platform_to_local(platform_data)

        # Assert - Verify data was saved
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM local_platforms WHERE name = 'Test Platform'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[3] == 'Test Platform'
        assert result[1] == 'Romania'

        # Cleanup
        os.remove(test_db)

    def test_save_platform_to_local_handles_missing_fields_gracefully(self):
        """Test that saving platform handles missing optional fields"""
        # Arrange
        test_db = 'data/test_missing.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        orch = ClaudeOrchestrator(db_path=test_db, use_turso=False)

        # Create table
        conn = sqlite3.connect(test_db)
        conn.execute("""
            CREATE TABLE local_platforms (
                id INTEGER PRIMARY KEY,
                region TEXT, country TEXT, name TEXT, url TEXT,
                type TEXT, language TEXT, description TEXT, data_source TEXT
            )
        """)
        conn.close()

        # Minimal platform data (only required fields)
        platform_data = {
            'region': 'Poland',
            'country': 'Poland',
            'name': 'Minimal Platform'
        }

        # Act
        orch._save_platform_to_local(platform_data)

        # Assert
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM local_platforms")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[3] == 'Minimal Platform'

        # Cleanup
        os.remove(test_db)

    @pytest.mark.parametrize("region,country,expected_language", [
        ("Romania", "Romania", "Romanian"),
        ("Poland", "Poland", "Polish"),
        ("Japan", "Japan", "Japanese"),
        ("Singapore", "Singapore", "English"),
    ])
    def test_get_primary_language_returns_correct_language(self, region, country, expected_language):
        """Test that _get_primary_language returns correct language for each country"""
        # Arrange
        orch = ClaudeOrchestrator(use_turso=False)

        # Act
        language = orch._get_primary_language(country)

        # Assert
        assert language == expected_language


@pytest.mark.integration
class TestClaudeOrchestratorIntegration:
    """Integration tests for full pipeline"""

    @pytest.mark.asyncio
    async def test_full_pipeline_save_and_query(self):
        """Test complete flow: Save platform → Query from database"""
        # Arrange
        test_db = 'data/test_integration.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        orch = ClaudeOrchestrator(db_path=test_db, use_turso=False)

        # Create table
        conn = sqlite3.connect(test_db)
        conn.execute("""
            CREATE TABLE local_platforms (
                id INTEGER PRIMARY KEY,
                region TEXT, country TEXT, name TEXT, url TEXT,
                type TEXT, language TEXT, description TEXT, data_source TEXT
            )
        """)
        conn.close()

        platform_data = {
            'region': 'Thailand',
            'country': 'Thailand',
            'name': 'Pantip',
            'url': 'https://pantip.com',
            'type': 'forum',
            'language': 'Thai',
            'description': 'Thailand largest webboard'
        }

        # Act - Save
        await orch._save_platform_to_db(platform_data)

        # Act - Query
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM local_platforms WHERE name = 'Pantip'")
        result = cursor.fetchone()
        conn.close()

        # Assert
        assert result is not None
        assert result[3] == 'Pantip'
        assert result[5] == 'forum'
        assert result[6] == 'Thai'

        # Cleanup
        os.remove(test_db)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
