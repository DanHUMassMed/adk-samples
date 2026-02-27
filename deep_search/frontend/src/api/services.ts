import { v4 as uuidv4 } from 'uuid';

export const createSession = async (): Promise<{ userId: string, sessionId: string, appName: string }> => {
    const generatedSessionId = uuidv4();
    const response = await fetch(`/api/apps/app/users/u_999/sessions/${generatedSessionId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    });

    if (!response.ok) {
        throw new Error(`Failed to create session: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return {
        userId: data.userId,
        sessionId: data.id,
        appName: data.appName
    };
};

export const checkBackendHealth = async (): Promise<boolean> => {
    try {
        // Use the docs endpoint or root endpoint to check if backend is ready
        const response = await fetch("/api/docs", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });
        return response.ok;
    } catch (error) {
        console.log("Backend not ready yet:", error);
        return false;
    }
};
