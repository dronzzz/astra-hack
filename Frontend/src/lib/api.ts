const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5050';

/**
 * Makes a GET request to the API
 * @param endpoint - The API endpoint to call (without leading slash)
 * @returns Promise with the response data
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
    const response = await fetch(`/${endpoint}`);

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
    }

    return response.json();
}

/**
 * Makes a POST request to the API
 * @param endpoint - The API endpoint to call (without leading slash)
 * @param data - The data to send in the request body
 * @returns Promise with the response data
 */
export async function apiPost<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
    }

    return response.json();
}

/**
 * Gets the full URL for a resource (like a video or image)
 * @param path - The resource path (without leading slash)
 * @returns The full URL to the resource
 */
export function getResourceUrl(path: string): string {
    return `${API_BASE_URL}/${path.startsWith('/') ? path.substring(1) : path}`;
}

export default {
    apiGet,
    apiPost,
    getResourceUrl,
    API_BASE_URL
}; 