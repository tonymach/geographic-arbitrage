#!/usr/bin/env python3
"""
Turso HTTP Client - Reliable HTTP API based connection

Since WebSocket (libsql-client) has 505 errors, this uses the proven HTTP API.
Test results show HTTP API works perfectly while WebSocket fails.
"""

import requests
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TursoHTTPClient:
    """
    HTTP-based Turso client that mimics libsql_client interface

    Uses Turso's HTTP API which is more reliable than WebSocket
    """

    def __init__(self, url: str, auth_token: str):
        """
        Initialize Turso HTTP client

        Args:
            url: Turso database URL (libsql://...)
            auth_token: Turso auth token
        """
        # Convert libsql:// to https://
        self.http_url = url.replace('libsql://', 'https://')
        self.auth_token = auth_token

        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }

        logger.info(f"✅ Turso HTTP client initialized: {self.http_url}")

    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> Dict:
        """
        Execute SQL query via HTTP API

        Mimics libsql_client.execute() interface for compatibility

        Args:
            sql: SQL query string
            params: Optional list of parameters for placeholders

        Returns:
            Result dictionary with rows, columns, etc.
        """
        try:
            # Replace ? placeholders with actual values for HTTP API
            # Turso HTTP API doesn't support parameterized queries the same way
            if params:
                # Simple parameter substitution for INSERT/UPDATE
                # For security: this is OK for our use case (controlled inputs)
                query = self._substitute_params(sql, params)
            else:
                query = sql

            payload = {
                'statements': [query]
            }

            response = requests.post(
                self.http_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"✅ SQL executed successfully")

                # Return in format compatible with libsql_client
                return self._format_response(result)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ SQL execution failed: {error_msg}")
                raise Exception(error_msg)

        except requests.RequestException as e:
            logger.error(f"❌ HTTP request failed: {e}")
            raise

    def _substitute_params(self, sql: str, params: List[Any]) -> str:
        """
        Substitute ? placeholders with actual values

        Note: This is safe for our use case with controlled inputs.
        For production with user input, use proper escaping.
        """
        query = sql
        for param in params:
            # Convert Python None to SQL NULL
            if param is None:
                value = 'NULL'
            elif isinstance(param, str):
                # Escape single quotes for SQL strings
                escaped = param.replace("'", "''")
                value = f"'{escaped}'"
            elif isinstance(param, (int, float)):
                value = str(param)
            elif isinstance(param, bool):
                value = '1' if param else '0'
            else:
                # For other types, try string conversion
                value = f"'{str(param)}'"

            # Replace first occurrence of ?
            query = query.replace('?', value, 1)

        return query

    def _format_response(self, raw_response: Dict) -> Dict:
        """
        Format HTTP API response to match libsql_client format

        HTTP API returns: [{'results': {'columns': [...], 'rows': [...]}}]
        libsql_client returns: {'rows': [...], 'columns': [...]}
        """
        if not raw_response or len(raw_response) == 0:
            return {'rows': [], 'columns': []}

        first_result = raw_response[0]
        if 'results' in first_result:
            results = first_result['results']
            return {
                'rows': results.get('rows', []),
                'columns': results.get('columns', [])
            }

        # Fallback for different response format
        return {'rows': [], 'columns': []}


def create_http_client(url: str, auth_token: str) -> TursoHTTPClient:
    """
    Factory function to create Turso HTTP client

    Matches libsql_client.create_client() interface
    """
    return TursoHTTPClient(url, auth_token)


async def test_connection(url: str, auth_token: str) -> bool:
    """
    Test Turso connection via HTTP API

    Returns:
        True if connection works, False otherwise
    """
    try:
        client = create_http_client(url, auth_token)
        result = await client.execute("SELECT 1 as test")

        if result.get('rows'):
            logger.info("✅ Turso HTTP connection test PASSED")
            return True
        else:
            logger.warning("⚠️ Turso HTTP connection test returned no rows")
            return False

    except Exception as e:
        logger.error(f"❌ Turso HTTP connection test FAILED: {e}")
        return False
