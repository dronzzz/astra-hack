export const testBackendConnection = async () => {
    try {
        // Test a simple GET endpoint
        const testResponse = await fetch('/api/test');
        const testData = await testResponse.json();
        console.log('API test response:', testData);

        // Test the actual endpoint
        const postResponse = await fetch('/api/process-youtube', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                youtubeUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            })
        });

        const postData = await postResponse.json();
        console.log('POST test response:', postData);

        return { success: true, testData, postData };
    } catch (error) {
        console.error("API connection test failed:", error);
        return { success: false, error };
    }
};
