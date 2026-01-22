
const { Storage } = require('@google-cloud/storage');

exports.handler = async (event, context) => {
    const filename = event.queryStringParameters.file;

    if (!filename) {
        return {
            statusCode: 400,
            body: "Missing 'file' parameter",
        };
    }

    // Security: Ensure we have credentials
    if (!process.env.GCS_CREDENTIALS) {
        console.error("GCS_CREDENTIALS not set");
        return { statusCode: 500, body: "Server Configuration Error" };
    }

    try {
        const credentials = JSON.parse(process.env.GCS_CREDENTIALS);
        const storage = new Storage({
            credentials,
            projectId: 'gen-lang-client-0854320022' // Project Tantan
        });

        const bucketName = 'cahcblr-pdfs';
        const bucket = storage.bucket(bucketName);
        const file = bucket.file(filename);

        // Optional: Check existence (adds latency, but good for UX)
        const [exists] = await file.exists();
        if (!exists) {
            console.warn(`File not found: ${filename}`);
            return { statusCode: 404, body: "PDF not found in archive." };
        }

        // Generate Signed URL
        const options = {
            version: 'v4',
            action: 'read',
            expires: Date.now() + 15 * 60 * 1000, // 15 minutes
        };

        const [url] = await file.getSignedUrl(options);

        return {
            statusCode: 302,
            headers: {
                Location: url,
                'Cache-Control': 'no-cache, no-store, must-revalidate' // Don't cache the redirect itself heavily
            },
            body: "",
        };

    } catch (error) {
        console.error("Error generating signed URL:", error);
        return {
            statusCode: 500,
            body: "Internal Server Error"
        };
    }
};
