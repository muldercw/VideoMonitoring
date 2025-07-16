#!/usr/bin/env python3
"""
Test script to verify all tabs work correctly
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_streams_tab():
    """Test all endpoints used by the Streams tab"""
    logger.info("Testing Streams tab endpoints...")
    
    # Test get all streams
    response = requests.get(f"{BASE_URL}/streams")
    assert response.status_code == 200
    streams = response.json()
    logger.info(f"✓ Retrieved {len(streams)} streams")
    
    # Test create stream
    stream_data = {
        "stream_name": "Test Stream",
        "stream_url": "0",
        "stream_type": "webcam"
    }
    response = requests.post(f"{BASE_URL}/streams", json=stream_data)
    assert response.status_code == 200
    stream = response.json()
    stream_id = stream["stream_id"]
    logger.info(f"✓ Created stream with ID: {stream_id}")
    
    # Test get specific stream
    response = requests.get(f"{BASE_URL}/streams/{stream_id}")
    assert response.status_code == 200
    logger.info(f"✓ Retrieved stream {stream_id}")
    
    # Test delete stream
    response = requests.delete(f"{BASE_URL}/streams/{stream_id}")
    assert response.status_code == 200
    logger.info(f"✓ Deleted stream {stream_id}")

def test_events_tab():
    """Test all endpoints used by the Events tab"""
    logger.info("Testing Events tab endpoints...")
    
    # First create a stream to get events from
    stream_data = {
        "stream_name": "Event Test Stream",
        "stream_url": "0",
        "stream_type": "webcam"
    }
    response = requests.post(f"{BASE_URL}/streams", json=stream_data)
    assert response.status_code == 200
    stream = response.json()
    stream_id = stream["stream_id"]
    
    # Test get stream events
    response = requests.get(f"{BASE_URL}/streams/{stream_id}/events?hours=24")
    assert response.status_code == 200
    events = response.json()
    logger.info(f"✓ Retrieved {len(events)} events for stream {stream_id}")
    
    # Test with event type filter
    response = requests.get(f"{BASE_URL}/streams/{stream_id}/events?hours=24&event_type=motion_detected")
    assert response.status_code == 200
    filtered_events = response.json()
    logger.info(f"✓ Retrieved {len(filtered_events)} filtered events")
    
    # Cleanup
    requests.delete(f"{BASE_URL}/streams/{stream_id}")

def test_analytics_tab():
    """Test all endpoints used by the Analytics tab"""
    logger.info("Testing Analytics tab endpoints...")
    
    # First create a stream to get analytics from
    stream_data = {
        "stream_name": "Analytics Test Stream",
        "stream_url": "0",
        "stream_type": "webcam"
    }
    response = requests.post(f"{BASE_URL}/streams", json=stream_data)
    assert response.status_code == 200
    stream = response.json()
    stream_id = stream["stream_id"]
    
    # Test get stream analytics
    response = requests.get(f"{BASE_URL}/streams/{stream_id}/analytics?hours=24")
    assert response.status_code == 200
    analytics = response.json()
    logger.info(f"✓ Retrieved {len(analytics)} analytics entries for stream {stream_id}")
    
    # Test with different time ranges
    for hours in [1, 6, 168]:
        response = requests.get(f"{BASE_URL}/streams/{stream_id}/analytics?hours={hours}")
        assert response.status_code == 200
        analytics = response.json()
        logger.info(f"✓ Retrieved {len(analytics)} analytics entries for {hours} hours")
    
    # Cleanup
    requests.delete(f"{BASE_URL}/streams/{stream_id}")

def test_dashboard_tab():
    """Test all endpoints used by the Dashboard tab"""
    logger.info("Testing Dashboard tab endpoints...")
    
    # Test dashboard summary
    response = requests.get(f"{BASE_URL}/dashboard/summary")
    assert response.status_code == 200
    summary = response.json()
    logger.info(f"✓ Dashboard summary: {summary}")
    
    # Test system status
    response = requests.get(f"{BASE_URL}/system/status")
    assert response.status_code == 200
    status = response.json()
    logger.info(f"✓ System status: {status['system_status']}")
    
    # Test system metrics
    response = requests.get(f"{BASE_URL}/system/metrics?hours=1")
    assert response.status_code == 200
    metrics = response.json()
    logger.info(f"✓ Retrieved {len(metrics)} system metrics")

def test_system_monitor_tab():
    """Test all endpoints used by the SystemMonitor tab"""
    logger.info("Testing SystemMonitor tab endpoints...")
    
    # Test system status
    response = requests.get(f"{BASE_URL}/system/status")
    assert response.status_code == 200
    status = response.json()
    logger.info(f"✓ System status: {status['system_status']}")
    
    # Test system metrics for 24 hours
    response = requests.get(f"{BASE_URL}/system/metrics?hours=24")
    assert response.status_code == 200
    metrics = response.json()
    logger.info(f"✓ Retrieved {len(metrics)} system metrics for 24 hours")

def main():
    """Run all tab tests"""
    logger.info("Starting comprehensive tab testing...")
    
    try:
        test_dashboard_tab()
        test_system_monitor_tab()
        test_streams_tab()
        test_events_tab()
        test_analytics_tab()
        
        logger.info("🎉 All tab tests passed! All tabs should be working correctly.")
        logger.info("Frontend URL: http://localhost:3000")
        logger.info("API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()