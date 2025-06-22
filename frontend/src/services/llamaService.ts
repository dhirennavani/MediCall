interface StructuredQuery {
  original_query: string;
  doctor_type: string;
  location: string;
  date: string;
  insurance_provider: string;
}

export async function extractQueryStructure(customerQuery: string): Promise<StructuredQuery> {
  try {
    console.log('Starting Llama API call with query:', customerQuery);
    const apiKey = import.meta.env.VITE_LLAMA_API_KEY;
    console.log('API Key available:', !!apiKey);

    if (!apiKey) {
        throw new Error("VITE_LLAMA_API_KEY is not set in the environment variables.");
    }
    
    const response = await fetch('https://api.llama.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: "Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages: [
          {
            role: "user",
            content: `Extract the following information from this customer query and return it as JSON: doctor type, location, and date. If any information is not mentioned, use "N/A". Query: "${customerQuery}"`
          }
        ],
        response_format: {
          type: "json_schema",
          json_schema: {
            name: "QueryExtraction",
            description: "Extracted information from customer query",
            schema: {
              type: "object",
              properties: {
                original_query: {
                  type: "string",
                  description: "The original customer query"
                },
                doctor_type: {
                  type: "string",
                  description: "Type of doctor or specialist needed"
                },
                location: {
                  type: "string",
                  description: "Location or city for the appointment"
                },
                date: {
                  type: "string",
                  description: "Preferred date for appointment"
                },
                insurance_provider: {
                  type: "string",
                  description: "Insurance provider mentioned"
                }
              },
              required: ["original_query", "doctor_type", "location", "date", "insurance_provider"]
            }
          }
        }
      })
    });

    console.log('Llama API response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Llama API error:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const result = await response.json();
    console.log('Llama API result:', result);
    
    const content = result.completion_message?.content;
    
    if (content && typeof content === 'object' && content.text) {
      const parsed = JSON.parse(content.text);
      console.log('Parsed structured data:', parsed);
      return parsed;
    } else {
      console.log('No structured content found, using fallback');
      return {
        original_query: customerQuery,
        doctor_type: "N/A",
        location: "N/A",
        date: "N/A",
        insurance_provider: "N/A"
      };
    }
  } catch (error) {
    console.error('Error extracting query structure:', error);
    return {
      original_query: customerQuery,
      doctor_type: "N/A",
      location: "N/A",
      date: "N/A",
      insurance_provider: "N/A"
    };
  }
} 