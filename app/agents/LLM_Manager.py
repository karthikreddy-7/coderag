from google import genai

from app.config.settings import GOOGLE_API_KEY


class LLM:
    """A simple wrapper for the Google Gemini LLM."""
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.1):
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the generated text."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text


# --- Example Usage ---
if __name__ == "__main__":
    try:
        llm = LLM()
        question = "HI ?"
        answer = llm.invoke(question)
        print(f"\nQuestion: {question}")
        print(f"\nAnswer:\n{answer}")
    except ValueError as e:
        print(e)
