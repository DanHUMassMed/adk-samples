// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const retryWithBackoff = async (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    fn: () => Promise<any>,
    maxRetries: number = 10,
    maxDuration: number = 120000 // 2 minutes
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any> => {
    const startTime = Date.now();
    let lastError: Error;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        if (Date.now() - startTime > maxDuration) {
            throw new Error(`Retry timeout after ${maxDuration}ms`);
        }

        try {
            return await fn();
        } catch (error) {
            lastError = error as Error;
            const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // Exponential backoff, max 5s
            console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms...`, error);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError!;
};
