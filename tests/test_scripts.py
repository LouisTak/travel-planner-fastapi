import pytest
import os
import subprocess
import tempfile
import json
from unittest.mock import patch, MagicMock

class TestAuthScript:
    
    @pytest.fixture
    def mock_token_file(self):
        """Fixture to create a temporary file for tokens."""
        _, temp_file = tempfile.mkstemp()
        original_file = os.environ.get('HOME', '') + '/.travel_planner_tokens'
        
        # Patch the CONFIG_FILE in the script
        with patch.dict('os.environ', {'CONFIG_FILE': temp_file}):
            yield temp_file
            
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    @patch('subprocess.run')
    def test_login_success(self, mock_run, mock_token_file):
        """Test successful login with the auth.sh script."""
        # Mock the curl response
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }).encode()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Run the login command
        result = subprocess.run(
            ['./scripts/auth.sh', 'login', 'test@example.com', 'password'],
            capture_output=True,
            text=True
        )
        
        # Verify the result
        assert 'Login successful' in result.stdout
        
        # Verify token file was created with correct content
        with open(mock_token_file, 'r') as f:
            content = f.read()
            assert 'ACCESS_TOKEN=test_access_token' in content
            assert 'REFRESH_TOKEN=test_refresh_token' in content
    
    @patch('subprocess.run')
    def test_login_failure(self, mock_run, mock_token_file):
        """Test login failure with the auth.sh script."""
        # Mock the curl response for a failed login
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({
            'detail': 'Incorrect email or password'
        }).encode()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Run the login command
        result = subprocess.run(
            ['./scripts/auth.sh', 'login', 'test@example.com', 'wrongpassword'],
            capture_output=True,
            text=True
        )
        
        # Verify the result
        assert 'Login failed' in result.stdout
        
        # Verify token file was not created
        assert not os.path.exists(mock_token_file)
    
    def test_show_token(self, mock_token_file):
        """Test showing the current token with auth.sh script."""
        # Create a token file
        with open(mock_token_file, 'w') as f:
            f.write('ACCESS_TOKEN=test_access_token\n')
            f.write('REFRESH_TOKEN=test_refresh_token\n')
        
        # Run the show token command
        result = subprocess.run(
            ['./scripts/auth.sh', 'token'],
            capture_output=True,
            text=True,
            env={'CONFIG_FILE': mock_token_file}
        )
        
        # Verify the result
        assert 'Access Token: test_access_token' in result.stdout
    
    def test_clear_tokens(self, mock_token_file):
        """Test clearing tokens with auth.sh script."""
        # Create a token file
        with open(mock_token_file, 'w') as f:
            f.write('ACCESS_TOKEN=test_access_token\n')
            f.write('REFRESH_TOKEN=test_refresh_token\n')
        
        # Run the clear command
        result = subprocess.run(
            ['./scripts/auth.sh', 'clear'],
            capture_output=True,
            text=True,
            env={'CONFIG_FILE': mock_token_file}
        )
        
        # Verify the result
        assert 'Tokens cleared successfully' in result.stdout
        
        # Verify token file was deleted
        assert not os.path.exists(mock_token_file)

class TestApiScript:
    
    @pytest.fixture
    def mock_token_file(self):
        """Fixture to create a temporary file for tokens."""
        _, temp_file = tempfile.mkstemp()
        
        # Create a token file
        with open(temp_file, 'w') as f:
            f.write('ACCESS_TOKEN=test_access_token\n')
            f.write('REFRESH_TOKEN=test_refresh_token\n')
        
        yield temp_file
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    @patch('subprocess.run')
    def test_get_request(self, mock_run, mock_token_file):
        """Test making a GET request with the api.sh script."""
        # Mock the curl response
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({
            'data': [{'id': '1', 'title': 'Test Plan'}]
        }).encode()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Run the GET command
        result = subprocess.run(
            ['./scripts/api.sh', 'get', '/travel-plans'],
            capture_output=True,
            text=True,
            env={'CONFIG_FILE': mock_token_file}
        )
        
        # Verify the result contains the expected data
        assert '"id": "1"' in result.stdout
        assert '"title": "Test Plan"' in result.stdout
    
    @patch('subprocess.run')
    def test_post_request(self, mock_run, mock_token_file):
        """Test making a POST request with the api.sh script."""
        # Mock the curl response
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({
            'id': '1',
            'title': 'New Plan',
            'destination': 'Paris'
        }).encode()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Run the POST command
        result = subprocess.run(
            ['./scripts/api.sh', 'post', '/travel-plans', '{"title":"New Plan","destination":"Paris"}'],
            capture_output=True,
            text=True,
            env={'CONFIG_FILE': mock_token_file}
        )
        
        # Verify the result contains the expected data
        assert '"id": "1"' in result.stdout
        assert '"title": "New Plan"' in result.stdout
        assert '"destination": "Paris"' in result.stdout
    
    def test_no_tokens(self):
        """Test behavior when no tokens are available."""
        # Use a non-existent token file
        non_existent_file = '/tmp/nonexistent_token_file'
        
        # Run the GET command
        result = subprocess.run(
            ['./scripts/api.sh', 'get', '/travel-plans'],
            capture_output=True,
            text=True,
            env={'CONFIG_FILE': non_existent_file}
        )
        
        # Verify the result
        assert 'No tokens found' in result.stdout 