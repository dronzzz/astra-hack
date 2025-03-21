import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.error('Missing Supabase environment variables');
}

export const supabase = createClient(
    supabaseUrl || '',
    supabaseAnonKey || ''
);

// Auth helpers
export async function signInWithGoogle() {
    return supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${window.location.origin}/dashboard`,
        },
    });
}

export async function signInWithGitHub() {
    return supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
            redirectTo: `${window.location.origin}/dashboard`,
        },
    });
}

export async function signOut() {
    return supabase.auth.signOut();
}

// User profile helpers
export async function getUserProfile() {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
}

// YouTube credentials helpers
export async function saveYouTubeCredentials(userId: string, credentials: any) {
    return supabase
        .from('youtube_credentials')
        .upsert([
            {
                user_id: userId,
                credentials_json: credentials,
                updated_at: new Date().toISOString()
            }
        ]);
}

export async function getYouTubeCredentials(userId: string) {
    const { data, error } = await supabase
        .from('youtube_credentials')
        .select('credentials_json')
        .eq('user_id', userId)
        .single();

    if (error) {
        console.error('Error fetching YouTube credentials:', error);
        return null;
    }

    return data?.credentials_json;
} 