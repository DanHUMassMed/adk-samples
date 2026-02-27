import { useState, useEffect } from 'react';
import { checkBackendHealth } from '../api/services';

export const useBackendHealth = () => {
    const [isBackendReady, setIsBackendReady] = useState(false);
    const [isCheckingBackend, setIsCheckingBackend] = useState(true);

    useEffect(() => {
        const checkBackend = async () => {
            setIsCheckingBackend(true);

            // Check if backend is ready with retry logic
            const maxAttempts = 60; // 2 minutes with 2-second intervals
            let attempts = 0;

            while (attempts < maxAttempts) {
                const isReady = await checkBackendHealth();
                if (isReady) {
                    setIsBackendReady(true);
                    setIsCheckingBackend(false);
                    return;
                }

                attempts++;
                await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds between checks
            }

            // If we get here, backend didn't come up in time
            setIsCheckingBackend(false);
            console.error("Backend failed to start within 2 minutes");
        };

        checkBackend();
    }, []);

    return { isBackendReady, isCheckingBackend };
};
