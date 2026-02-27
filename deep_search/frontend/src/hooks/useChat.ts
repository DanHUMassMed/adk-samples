import { useState, useRef, useCallback } from 'react';
import { MessageWithAgent, ProcessedEvent, DisplayData } from '../types';
import { createSession } from '../api/services';
import { extractDataFromSSE, getEventTitle } from '../utils/sseParser';
import { retryWithBackoff } from '../utils/apiHelpers';

export const useChat = () => {
    const [userId, setUserId] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [appName, setAppName] = useState<string | null>(null);
    const [messages, setMessages] = useState<MessageWithAgent[]>([]);
    const [displayData, setDisplayData] = useState<DisplayData>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [messageEvents, setMessageEvents] = useState<Map<string, ProcessedEvent[]>>(new Map());
    const [websiteCount, setWebsiteCount] = useState<number>(0);

    const currentAgentRef = useRef('');
    const accumulatedTextRef = useRef("");

    const processSseEventData = useCallback((jsonData: string, aiMessageId: string) => {
        const { textParts, agent, finalReportWithCitations, functionCall, functionResponse, sourceCount, sources } = extractDataFromSSE(jsonData);

        if (sourceCount > 0) {
            console.log('[SSE HANDLER] Updating websiteCount. Current sourceCount:', sourceCount);
            setWebsiteCount(prev => Math.max(prev, sourceCount));
        }

        if (agent && agent !== currentAgentRef.current) {
            currentAgentRef.current = agent;
        }

        if (functionCall) {
            const functionCallTitle = `Function Call: ${functionCall.name}`;
            console.log('[SSE HANDLER] Adding Function Call timeline event:', functionCallTitle);
            setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
                title: functionCallTitle,
                data: { type: 'functionCall', name: functionCall.name, args: functionCall.args, id: functionCall.id }
            }]));
        }

        if (functionResponse) {
            const functionResponseTitle = `Function Response: ${functionResponse.name}`;
            console.log('[SSE HANDLER] Adding Function Response timeline event:', functionResponseTitle);
            setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
                title: functionResponseTitle,
                data: { type: 'functionResponse', name: functionResponse.name, response: functionResponse.response, id: functionResponse.id }
            }]));
        }

        if (textParts.length > 0 && agent !== "report_composer_with_citations") {
            if (agent !== "interactive_planner_agent") {
                const eventTitle = getEventTitle(agent);
                console.log('[SSE HANDLER] Adding Text timeline event for agent:', agent, 'Title:', eventTitle, 'Data:', textParts.join(" "));
                setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
                    title: eventTitle,
                    data: { type: 'text', content: textParts.join(" ") }
                }]));
            } else { // interactive_planner_agent text updates the main AI message
                for (const text of textParts) {
                    accumulatedTextRef.current += text + " ";
                    setMessages(prev => prev.map(msg =>
                        msg.id === aiMessageId ? { ...msg, content: accumulatedTextRef.current.trim(), agent: currentAgentRef.current || msg.agent } : msg
                    ));
                    setDisplayData(accumulatedTextRef.current.trim());
                }
            }
        }

        if (sources) {
            console.log('[SSE HANDLER] Adding Retrieved Sources timeline event:', sources);
            setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
                title: "Retrieved Sources", data: { type: 'sources', content: sources }
            }]));
        }

        if (agent === "report_composer_with_citations" && finalReportWithCitations) {
            const finalReportMessageId = Date.now().toString() + "_final";
            setMessages(prev => [...prev, { type: "ai", content: finalReportWithCitations as string, id: finalReportMessageId, agent: currentAgentRef.current, finalReportWithCitations: true }]);
            setDisplayData(finalReportWithCitations as string);
        }
    }, []);

    const handleSubmit = useCallback(async (query: string) => {
        if (!query.trim()) return;

        setIsLoading(true);
        try {
            // Create session if it doesn't exist
            let currentUserId = userId;
            let currentSessionId = sessionId;
            let currentAppName = appName;

            if (!currentSessionId || !currentUserId || !currentAppName) {
                console.log('Creating new session...');
                const sessionData = await retryWithBackoff(createSession);
                currentUserId = sessionData.userId;
                currentSessionId = sessionData.sessionId;
                currentAppName = sessionData.appName;

                setUserId(currentUserId);
                setSessionId(currentSessionId);
                setAppName(currentAppName);
                console.log('Session created successfully:', { currentUserId, currentSessionId, currentAppName });
            }

            // Add user message to chat
            const userMessageId = Date.now().toString();
            setMessages(prev => [...prev, { type: "human", content: query, id: userMessageId }]);

            // Create AI message placeholder
            const aiMessageId = Date.now().toString() + "_ai";
            currentAgentRef.current = ''; // Reset current agent
            accumulatedTextRef.current = ''; // Reset accumulated text

            setMessages(prev => [...prev, {
                type: "ai",
                content: "",
                id: aiMessageId,
                agent: '',
            }]);

            // Send the message with retry logic
            const sendMessage = async () => {
                const response = await fetch("/api/run_sse", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        appName: currentAppName,
                        userId: currentUserId,
                        sessionId: currentSessionId,
                        newMessage: {
                            parts: [{ text: query }],
                            role: "user"
                        },
                        streaming: false
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Failed to send message: ${response.status} ${response.statusText}`);
                }

                return response;
            };

            const response = await retryWithBackoff(sendMessage);

            // Handle SSE streaming
            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            let lineBuffer = "";
            let eventDataBuffer = "";

            if (reader) {
                // eslint-disable-next-line no-constant-condition
                while (true) {
                    const { done, value } = await reader.read();

                    if (value) {
                        lineBuffer += decoder.decode(value, { stream: true });
                    }

                    let eolIndex;
                    // Process all complete lines in the buffer, or the remaining buffer if 'done'
                    while ((eolIndex = lineBuffer.indexOf('\n')) >= 0 || (done && lineBuffer.length > 0)) {
                        let line: string;
                        if (eolIndex >= 0) {
                            line = lineBuffer.substring(0, eolIndex);
                            lineBuffer = lineBuffer.substring(eolIndex + 1);
                        } else { // Only if done and lineBuffer has content without a trailing newline
                            line = lineBuffer;
                            lineBuffer = "";
                        }

                        if (line.trim() === "") { // Empty line: dispatch event
                            if (eventDataBuffer.length > 0) {
                                // Remove trailing newline before parsing
                                const jsonDataToParse = eventDataBuffer.endsWith('\n') ? eventDataBuffer.slice(0, -1) : eventDataBuffer;
                                console.log('[SSE DISPATCH EVENT]:', jsonDataToParse.substring(0, 200) + "..."); // DEBUG
                                processSseEventData(jsonDataToParse, aiMessageId);
                                eventDataBuffer = ""; // Reset for next event
                            }
                        } else if (line.startsWith('data:')) {
                            eventDataBuffer += line.substring(5).trimStart() + '\n'; // Add newline as per spec for multi-line data
                        } else if (line.startsWith(':')) {
                            // Comment line, ignore
                        } // Other SSE fields (event, id, retry) can be handled here if needed
                    }

                    if (done) {
                        // If the loop exited due to 'done', and there's still data in eventDataBuffer
                        // (e.g., stream ended after data lines but before an empty line delimiter)
                        if (eventDataBuffer.length > 0) {
                            const jsonDataToParse = eventDataBuffer.endsWith('\n') ? eventDataBuffer.slice(0, -1) : eventDataBuffer;
                            console.log('[SSE DISPATCH FINAL EVENT]:', jsonDataToParse.substring(0, 200) + "..."); // DEBUG
                            processSseEventData(jsonDataToParse, aiMessageId);
                            eventDataBuffer = ""; // Clear buffer
                        }
                        break; // Exit the while(true) loop
                    }
                }
            }

            setIsLoading(false);

        } catch (error) {
            console.error("Error:", error);
            // Update the AI message placeholder with an error message
            const aiMessageId = Date.now().toString() + "_ai_error";
            setMessages(prev => [...prev, {
                type: "ai",
                content: `Sorry, there was an error processing your request: ${error instanceof Error ? error.message : 'Unknown error'}`,
                id: aiMessageId
            }]);
            setIsLoading(false);
        }
    }, [
        userId, sessionId, appName,
        processSseEventData
    ]);

    const handleCancel = useCallback(() => {
        setMessages([]);
        setDisplayData(null);
        setMessageEvents(new Map());
        setWebsiteCount(0);
        window.location.reload();
    }, []);

    return {
        messages,
        displayData,
        isLoading,
        messageEvents,
        websiteCount,
        handleSubmit,
        handleCancel
    };
};
