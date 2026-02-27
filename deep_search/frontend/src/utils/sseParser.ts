// Function to extract text and metadata from SSE data
export const extractDataFromSSE = (data: string) => {
    try {
        const parsed = JSON.parse(data);
        console.log('[SSE PARSED EVENT]:', JSON.stringify(parsed, null, 2)); // DEBUG: Log parsed event

        let textParts: string[] = [];
        let agent = '';
        let finalReportWithCitations = undefined;
        let functionCall = null;
        let functionResponse = null;
        let sources = null;

        // Check if content.parts exists and has text
        if (parsed.content && parsed.content.parts) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            textParts = parsed.content.parts
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .filter((part: any) => part.text)
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .map((part: any) => part.text);

            // Check for function calls
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const functionCallPart = parsed.content.parts.find((part: any) => part.functionCall);
            if (functionCallPart) {
                functionCall = functionCallPart.functionCall;
            }

            // Check for function responses
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const functionResponsePart = parsed.content.parts.find((part: any) => part.functionResponse);
            if (functionResponsePart) {
                functionResponse = functionResponsePart.functionResponse;
            }
        }

        // Extract agent information
        if (parsed.author) {
            agent = parsed.author;
            console.log('[SSE EXTRACT] Agent:', agent); // DEBUG: Log agent
        }

        if (
            parsed.actions &&
            parsed.actions.stateDelta &&
            parsed.actions.stateDelta.final_report_with_citations
        ) {
            finalReportWithCitations = parsed.actions.stateDelta.final_report_with_citations;
        }

        // Extract website count from research agents
        let sourceCount = 0;
        if ((parsed.author === 'section_researcher' || parsed.author === 'enhanced_search_executor')) {
            console.log('[SSE EXTRACT] Relevant agent for source count:', parsed.author); // DEBUG
            if (parsed.actions?.stateDelta?.url_to_short_id) {
                console.log('[SSE EXTRACT] url_to_short_id found:', parsed.actions.stateDelta.url_to_short_id); // DEBUG
                sourceCount = Object.keys(parsed.actions.stateDelta.url_to_short_id).length;
                console.log('[SSE EXTRACT] Calculated sourceCount:', sourceCount); // DEBUG
            } else {
                console.log('[SSE EXTRACT] url_to_short_id NOT found for agent:', parsed.author); // DEBUG
            }
        }

        // Extract sources if available
        if (parsed.actions?.stateDelta?.sources) {
            sources = parsed.actions.stateDelta.sources;
            console.log('[SSE EXTRACT] Sources found:', sources); // DEBUG
        }


        return { textParts, agent, finalReportWithCitations, functionCall, functionResponse, sourceCount, sources };
    } catch (error) {
        // Log the error and a truncated version of the problematic data for easier debugging.
        const truncatedData = data.length > 200 ? data.substring(0, 200) + "..." : data;
        console.error('Error parsing SSE data. Raw data (truncated): "', truncatedData, '". Error details:', error);
        return { textParts: [], agent: '', finalReportWithCitations: undefined, functionCall: null, functionResponse: null, sourceCount: 0, sources: null };
    }
};

export const getEventTitle = (agentName: string): string => {
    switch (agentName) {
        case "plan_generator":
            return "Planning Research Strategy";
        case "section_planner":
            return "Structuring Report Outline";
        case "section_researcher":
            return "Initial Web Research";
        case "research_evaluator":
            return "Evaluating Research Quality";
        case "EscalationChecker":
            return "Quality Assessment";
        case "enhanced_search_executor":
            return "Enhanced Web Research";
        case "research_pipeline":
            return "Executing Research Pipeline";
        case "iterative_refinement_loop":
            return "Refining Research";
        case "interactive_planner_agent":
        case "root_agent":
            return "Interactive Planning";
        default:
            return `Processing (${agentName || 'Unknown Agent'})`;
    }
};
