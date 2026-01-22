
require('dotenv').config(); // Load .env file
const { handler } = require('./netlify/functions/authorize-pdf');

async function test() {
    console.log("Testing authorize-pdf function with KNOWN EXISTING file...");

    // Mock Event with a file path we know exists from 'gsutil ls'
    const event = {
        queryStringParameters: {
            file: "assets/ijhs/01-IJHS59_1.pdf"
        }
    };

    // Mock Context
    const context = {};

    try {
        const response = await handler(event, context);
        console.log("Response Status:", response.statusCode);

        if (response.statusCode === 302) {
            console.log("SUCCESS: Redirect generated.");
            console.log("Location:", response.headers.Location);
            console.log("This URL is a Signed URL for the private object.");
        } else {
            console.log("Response Body:", response.body);
        }

    } catch (e) {
        console.error("Test Failed:", e);
    }
}

test();
