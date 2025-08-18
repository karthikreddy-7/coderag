DECISION_PROMPT = """
You are a helpful agent with access to tools and a retriever.

Your task is to decide what to do next based on the user's question.

- If the question requires factual knowledge that may exist in the knowledge base, call the retriever.
- If the question involves computation, call the calculator tool.
- If you can answer directly without tools, do so.
- Always explain briefly why you chose that action.

Question: {question}

Respond with one of:
- "RETRIEVE"
- "CALCULATE"
- "ANSWER"
"""

SYNTHESIS_PROMPT = """
You are a reasoning agent synthesizing a final response.

You have the following information:
- User question: {question}
- Retrieved documents: {documents}
- Intermediate reasoning: {reasoning}

Using all the above, provide a clear, helpful, and accurate answer to the user.

If documents are irrelevant or empty, answer to the best of your knowledge or say you don’t know.
"""

