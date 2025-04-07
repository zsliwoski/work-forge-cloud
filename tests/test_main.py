import pytest
from unittest.mock import patch, MagicMock, call
import os
import sys
import psycopg2
from cuid2 import Cuid

# Import the module we're testing
sys.path.append('.')  # Adding the current directory to the path
from src.main import main

@pytest.fixture
def mock_cursor():
    return MagicMock()

@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn

@pytest.fixture
def env_setup():
    # Set environment variables for testing
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'
    os.environ['DB_HOST'] = 'test_host'
    os.environ['DB_PORT'] = '5678'
    os.environ['DB_NAME'] = 'test_db'
    
    # Yield control back to the test
    yield
    
    # Clean up environment variables after test completes
    for var in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']:
        if var in os.environ:
            del os.environ[var]

def test_fetchCurrentSprints(mock_cursor):
    # Set up the mock cursor
    mock_cursor.fetchall.return_value = [('sprint1',), ('sprint2',)]
    
    # Call the function
    result = main.fetchCurrentSprints(mock_cursor)
    
    # Verify the function execution
    mock_cursor.execute.assert_called_once_with(
        '''SELECT "currentSprintId" FROM "Team" WHERE "currentSprintId" IS NOT NULL'''
    )
    mock_cursor.fetchall.assert_called_once()
    assert result == [('sprint1',), ('sprint2',)]

def test_fetchSprintTickets(mock_cursor):
    # Set up the mock cursor
    mock_cursor.fetchall.return_value = [
        ('OPEN', 3),
        ('IN PROGRESS', 2),
        ('BLOCKED', 1),
        ('CLOSED', 4)
    ]
    
    # Call the function
    result = main.fetchSprintTickets(mock_cursor, ('sprint1',))
    
    # Verify the function execution
    mock_cursor.execute.assert_called_once_with(
        '''SELECT "status", count(*) FROM "Ticket" WHERE "sprintId"=%s GROUP BY "status"''',
        ('sprint1',)
    )
    mock_cursor.fetchall.assert_called_once()
    assert result == [
        ('OPEN', 3),
        ('IN PROGRESS', 2),
        ('BLOCKED', 1),
        ('CLOSED', 4)
    ]

def test_insertSprintDailyProgress(mock_cursor):
    # Set up the test data
    progress = ('progress_id', 'sprint_id', 4, 1, 5)
    
    # Call the function
    main.insertSprintDailyProgress(mock_cursor, progress)
    
    # Verify the function execution
    mock_cursor.execute.assert_called_once_with(
        '''INSERT INTO "SprintDailyProgress"("id", "sprintId", "completed", "blocked", "remaining") VALUES(%s, %s, %s, %s, %s)''',
        progress
    )

@patch('psycopg2.connect')
@patch('main.fetchCurrentSprints')
@patch('main.fetchSprintTickets')
@patch('main.insertSprintDailyProgress')
@patch('cuid2.Cuid')
def test_main_success(mock_cuid, mock_insert, mock_fetch_tickets, mock_fetch_sprints, mock_connect, env_setup):
    # Set up mocks
    mock_cuid_instance = MagicMock()
    mock_cuid_instance.generate.return_value = 'generated_id'
    mock_cuid.return_value = mock_cuid_instance
    
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    mock_fetch_sprints.return_value = [('sprint1',), ('sprint2',)]
    mock_fetch_tickets.side_effect = [
        [('OPEN', 2), ('IN PROGRESS', 1), ('BLOCKED', 1), ('CLOSED', 3)],
        [('OPEN', 1), ('IN PROGRESS', 2), ('BLOCKED', 2), ('CLOSED', 4)]
    ]
    
    # Call the main function
    main.main({}, {})
    
    # Verify calls
    mock_connect.assert_called_once_with("postgres://test_user:test_password@test_host:5678/test_db")
    mock_fetch_sprints.assert_called_once_with(mock_cursor)
    
    # Check fetchSprintTickets was called twice, once for each sprint
    assert mock_fetch_tickets.call_count == 2
    mock_fetch_tickets.assert_has_calls([
        call(mock_cursor, ('sprint1',)),
        call(mock_cursor, ('sprint2',))
    ])
    
    # Check insertSprintDailyProgress was called twice, once for each sprint
    assert mock_insert.call_count == 2
    mock_insert.assert_has_calls([
        call(mock_cursor, ('generated_id', 'sprint1', 3, 1, 3)),
        call(mock_cursor, ('generated_id', 'sprint2', 4, 2, 3))
    ])
    
    # Check the connection was closed
    mock_conn.close.assert_called_once()

@patch('psycopg2.connect')
@patch('main.fetchCurrentSprints')
@patch('builtins.print')
def test_main_sprint_tickets_exception(mock_print, mock_fetch_sprints, mock_connect, env_setup):
    # Set up mocks for the error case when fetching sprint tickets
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    mock_fetch_sprints.return_value = [('sprint1',)]
    mock_cursor.execute.side_effect = [None, psycopg2.Error("DB error")]
    
    # Call the main function
    main.main({}, {})
    
    # Verify error was printed and connection was closed
    mock_print.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('psycopg2.connect')
@patch('builtins.print')
def test_main_connection_exception(mock_print, mock_connect, env_setup):
    # Set up mock for connection error
    mock_connect.side_effect = psycopg2.Error("Connection error")
    
    # Call the main function
    main.main({}, {})
    
    # Verify error was printed
    mock_print.assert_called_once_with(mock_connect.side_effect)

def test_main_missing_env_vars():
    # Clear environment variables
    for var in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']:
        if var in os.environ:
            del os.environ[var]
    
    # Set only some environment variables
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_HOST'] = 'test_host'
    
    with patch('builtins.print') as mock_print:
        # Call the main function
        main.main({}, {})
        
        # Verify error was printed
        mock_print.assert_called_once()
        # Check that the error message indicates missing parameters
        assert "Missing one or more database connection parameters" in str(mock_print.call_args[0][0])