import pytest
from utils.response_wrapper import api_response

class TestResponseWrapper:
    def test_api_response_default_values(self):
        """Test the api_response function with default parameters."""
        response = api_response()
        assert response == {
            "status": True,
            "message": "Success",
            "data": None,
            "error": None
        }
    
    def test_api_response_with_data(self):
        """Test the api_response function with custom data."""
        test_data = {"key": "value"}
        response = api_response(data=test_data)
        assert response == {
            "status": True,
            "message": "Success",
            "data": test_data,
            "error": None
        }
    
    def test_api_response_with_error(self):
        """Test the api_response function with error."""
        test_error = "An error occurred"
        response = api_response(error=test_error, status=False, message="Error")
        assert response == {
            "status": False,
            "message": "Error",
            "data": None,
            "error": test_error
        }
    
    def test_api_response_with_custom_values(self):
        """Test the api_response function with all custom values."""
        test_data = {"result": "success"}
        test_error = None
        test_message = "Custom message"
        test_status = True
        
        response = api_response(
            data=test_data,
            message=test_message,
            status=test_status,
            error=test_error
        )
        
        assert response == {
            "status": test_status,
            "message": test_message,
            "data": test_data,
            "error": test_error
        } 