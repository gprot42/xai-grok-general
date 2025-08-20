#!/bin/bash

# xAI offers $150 in free monthly API credits if you opt in to share your API usage data for training
# 1. But to use for the first time, you need to purchase USD $5 inititally from the console, select purchase
# 2. Generate API Key https://console.x.ai/team/
# 3. export GROK_API_KEY=123455
# 4. ./run-this-script.sh


# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}
# Check dependencies
if ! command_exists curl; then
  echo "Error: curl is not installed. Please install curl to proceed."
  exit 1
fi
if ! command_exists jq; then
  echo "Error: jq is not installed. Please install jq to proceed."
  exit 1
fi
if ! command_exists bc; then
  echo "Error: bc is not installed. Please install bc to proceed."
  exit 1
fi
# Set your xAI API key (store securely, e.g., as an environment variable)
export GROK_API_KEY="${GROK_API_KEY:-YOUR_API_KEY}" # Fallback; set via export for security
if [ "$GROK_API_KEY" = "YOUR_API_KEY" ]; then
  echo "Error: Please set your actual GROK_API_KEY environment variable or update the script."
  exit 1
fi
# API endpoint
ENDPOINT="https://api.x.ai/v1/chat/completions"
# Model to use - https://docs.x.ai/docs/models
#MODEL="grok-3"
MODEL="grok-4-0709"
# System prompt (optional, defines the AI's behavior)
SYSTEM_PROMPT="You are Grok, a helpful AI built by xAI."
# Get user input for the query
echo "Enter your query (press Ctrl-D when done):"
USER_QUERY=$(cat)
echo "Processing ..."
if [ -z "$USER_QUERY" ]; then
  echo "Error: Query cannot be empty."
  exit 1
fi
# JSON payload for the POST request
PAYLOAD=$(jq -n \
  --arg system_prompt "$SYSTEM_PROMPT" \
  --arg user_query "$USER_QUERY" \
  --arg model "$MODEL" \
  '{
    messages: [
      { role: "system", content: $system_prompt },
      { role: "user", content: $user_query }
    ],
    model: $model,
    stream: false,
    temperature: 0.7
  }') || {
  echo "Error: Failed to create JSON payload with jq."
  exit 1
}
# Send the POST request with curl
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROK_API_KEY" \
  -d "$PAYLOAD" \
  --write-out "%{http_code}" \
  --output /tmp/grok_response_body.$$) # Store body in temp file
HTTP_CODE="${RESPONSE: -3}" # Last 3 chars are HTTP code
RESPONSE_BODY=$(cat /tmp/grok_response_body.$$)
rm -f /tmp/grok_response_body.$$
if [ $? -ne 0 ]; then
  echo "Error: curl command failed. Check your network connection."
  exit 1
fi
# Check HTTP status code
if [ "$HTTP_CODE" -ne 200 ]; then
  echo "Error: API request failed with HTTP code $HTTP_CODE."
  # Improved jq to handle if .error is a string or object
  ERROR_MSG=$(echo "$RESPONSE_BODY" | jq -r 'if .error? | type == "string" then .error else .error.message // "Unknown error (raw response: \($RESPONSE_BODY))" end' 2>/dev/null || echo "Unknown error (response may not be JSON: $RESPONSE_BODY)")
  echo "Details: $ERROR_MSG"
  exit 1
fi
# Extract and print the response content
CONTENT=$(echo "$RESPONSE_BODY" | jq -r '.choices[0].message.content // empty')
if [ -z "$CONTENT" ]; then
  echo "Error: No content found in API response. Raw response:"
  echo "$RESPONSE_BODY"
  exit 1
fi
echo "$CONTENT"
# Extract token usage
PROMPT_TOKENS=$(echo "$RESPONSE_BODY" | jq -r '.usage.prompt_tokens // 0')
COMPLETION_TOKENS=$(echo "$RESPONSE_BODY" | jq -r '.usage.completion_tokens // 0')
TOTAL_TOKENS=$(echo "$RESPONSE_BODY" | jq -r '.usage.total_tokens // 0')
echo ""
echo "Input tokens: $PROMPT_TOKENS"
echo "Output tokens: $COMPLETION_TOKENS"
echo "Total tokens: $TOTAL_TOKENS"
# Calculate estimated cost (pricing: $3 per 1M input tokens, $15 per 1M output tokens)
INPUT_COST=$(echo "scale=6; $PROMPT_TOKENS * 3 / 1000000" | bc)
OUTPUT_COST=$(echo "scale=6; $COMPLETION_TOKENS * 15 / 1000000" | bc)
TOTAL_COST=$(echo "scale=6; $INPUT_COST + $OUTPUT_COST" | bc)
echo "Estimated cost (USD): Input \$${INPUT_COST}, Output \$${OUTPUT_COST}, Total \$${TOTAL_COST}"
