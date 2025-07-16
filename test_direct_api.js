// Simple test to verify the API call works directly
const axios = require('axios');

async function testDirectAPI() {
    try {
        console.log('Making direct API call to streams endpoint...');
        const response = await axios.get('http://localhost:8000/streams');
        console.log('Response status:', response.status);
        console.log('Response data:', response.data);
        console.log('Number of streams:', response.data.length);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testDirectAPI();