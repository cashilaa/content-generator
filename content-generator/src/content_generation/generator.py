import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

import google.generativeai as genai

class ContentGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt, user_interests):
        interests_str = ", ".join(user_interests)
        context = f"Generate a social media post about {interests_str}. Prompt: {prompt}"
        try:
            response = self.model.generate_content(context)
            if not response.text:
                return False, "Content generation failed due to safety filters. Please try a different prompt."
            return True, response.text
        except Exception as e:
            return False, f"An error occurred during content generation: {str(e)}"

    # Similar changes for generate_comment and generate_response methods

    def generate_comment(self, post, user_interests):
        interests_str = ", ".join(user_interests)
        context = f"Generate a comment for the following post, considering interests in {interests_str}: {post}"
        response = self.model.generate_content(context)
        return response.text

    def generate_response(self, comment, user_interests):
        interests_str = ", ".join(user_interests)
        context = f"Generate a response to the following comment, considering interests in {interests_str}: {comment}"
        response = self.model.generate_content(context)
        return response.text