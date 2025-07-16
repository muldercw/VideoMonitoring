import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test basic API endpoints"""
    try:
        # Test health check
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"Health check: {response.status_code}")
        
        # Test system status
        response = requests.get(f"{BASE_URL}/system/status")
        logger.info(f"System status: {response.status_code}")
        
        # Test dashboard summary
        response = requests.get(f"{BASE_URL}/dashboard/summary")
        logger.info(f"Dashboard summary: {response.status_code}")
        
        # Test streams endpoint
        response = requests.get(f"{BASE_URL}/streams")
        logger.info(f"Streams list: {response.status_code}")
        
        return True
    except Exception as e:
        logger.error(f"API test failed: {e}")
        return False

def test_stream_management():
    """Test stream management functionality"""
    try:
        # Create a test stream
        stream_data = {
            "stream_name": "Test Stream",
            "stream_url": "0",  # Use webcam
            "stream_type": "webcam"
        }
        
        response = requests.post(f"{BASE_URL}/streams", json=stream_data)
        logger.info(f"Create stream: {response.status_code}")
        
        if response.status_code == 200:
            stream_id = response.json()["stream_id"]
            
            # Start the stream
            response = requests.post(f"{BASE_URL}/streams/{stream_id}/start")
            logger.info(f"Start stream: {response.status_code}")
            
            # Wait a bit for processing
            time.sleep(10)
            
            # Get analytics
            response = requests.get(f"{BASE_URL}/streams/{stream_id}/analytics")
            logger.info(f"Get analytics: {response.status_code}")
            
            # Get events
            response = requests.get(f"{BASE_URL}/streams/{stream_id}/events")
            logger.info(f"Get events: {response.status_code}")
            
            # Stop the stream
            response = requests.post(f"{BASE_URL}/streams/{stream_id}/stop")
            logger.info(f"Stop stream: {response.status_code}")
            
            return True
        return False
    except Exception as e:
        logger.error(f"Stream management test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting system tests...")
    
    # Wait for system to start
    time.sleep(5)
    
    # Test API endpoints
    if test_api_endpoints():
        logger.info("API endpoints test passed")
    else:
        logger.error("API endpoints test failed")
    
    # Test stream management
    if test_stream_management():
        logger.info("Stream management test passed")
    else:
        logger.error("Stream management test failed")
    
    logger.info("System tests completed")