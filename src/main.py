from content_generation.generator import ContentGenerator
from content_generation.user_interests import UserInterestsManager
from content_moderation.moderator import ContentModerator
from bias_detection.bias_detector import BiasDetector
from feedback_loop.feedback_handler import FeedbackHandler
from dotenv import load_dotenv

load_dotenv()

class AIContentBot:
    def __init__(self):
        self.generator = ContentGenerator()
        self.moderator = ContentModerator()
        self.bias_detector = BiasDetector()
        self.feedback_handler = FeedbackHandler()
        self.user_interests = UserInterestsManager()

    def generate_and_moderate_content(self, prompt, user_id):
        user_interests = self.user_interests.get_user_interests(user_id)
        content = self.generator.generate_content(prompt, user_interests)
        
        is_appropriate, moderation_result = self.moderator.moderate_content(content)
        bias_detected, bias_result = self.bias_detector.detect_bias(content)

        if is_appropriate and not bias_detected:
            return content
        elif not is_appropriate:
            return f"Content generation failed due to guideline violations: {moderation_result}"
        else:
            return f"Content generation failed due to detected bias: {bias_result}"

    def generate_comment(self, post, user_id):
        user_interests = self.user_interests.get_user_interests(user_id)
        comment = self.generator.generate_comment(post, user_interests)
        
        is_appropriate, moderation_result = self.moderator.moderate_content(comment)
        bias_detected, bias_result = self.bias_detector.detect_bias(comment)

        if is_appropriate and not bias_detected:
            return comment
        elif not is_appropriate:
            return f"Comment generation failed due to guideline violations: {moderation_result}"
        else:
            return f"Comment generation failed due to detected bias: {bias_result}"

    def generate_response(self, comment, user_id):
        user_interests = self.user_interests.get_user_interests(user_id)
        response = self.generator.generate_response(comment, user_interests)
        
        is_appropriate, moderation_result = self.moderator.moderate_content(response)
        bias_detected, bias_result = self.bias_detector.detect_bias(response)

        if is_appropriate and not bias_detected:
            return response
        elif not is_appropriate:
            return f"Response generation failed due to guideline violations: {moderation_result}"
        else:
            return f"Response generation failed due to detected bias: {bias_result}"

    def handle_user_interaction(self, content, user_reaction):
        self.feedback_handler.add_feedback(content, user_reaction)
        if len(self.feedback_handler.feedback_data) % 100 == 0:
            analysis = self.feedback_handler.analyze_feedback()
            print("Feedback Analysis:", analysis)
            self.feedback_handler.update_model()

    def add_user_interests(self, user_id, interests):
        self.user_interests.add_user_interests(user_id, interests)

    def get_user_interests(self, user_id):
        return self.user_interests.get_user_interests(user_id)

    def remove_user_interest(self, user_id, interest):
        self.user_interests.remove_user_interest(user_id, interest)

# Example usage
if __name__ == "__main__":
    bot = AIContentBot()

    # Add user interests
    bot.add_user_interests("user1", ["AI", "technology", "innovation"])
    bot.add_user_interests("user2", ["sports", "health", "fitness"])

    # Generate content
    content1 = bot.generate_and_moderate_content("Write a post about the future of technology", "user1")
    print("Generated content for user1:", content1)

    content2 = bot.generate_and_moderate_content("Write a post about maintaining a healthy lifestyle", "user2")
    print("Generated content for user2:", content2)

    # Generate comment
    comment = bot.generate_comment(content1, "user2")
    print("Generated comment:", comment)

    # Generate response
    response = bot.generate_response(comment, "user1")
    print("Generated response:", response)

    # Handle user interactions
    bot.handle_user_interaction(content1, "positive")
    bot.handle_user_interaction(content2, "neutral")
    bot.handle_user_interaction(comment, "negative")
    bot.handle_user_interaction(response, "positive")

    # Get feedback analysis
    analysis = bot.feedback_handler.analyze_feedback()
    print("Feedback Analysis:", analysis)

    # Save and load feedback data
    bot.feedback_handler.save_feedback_data("feedback_data.json")
    bot.feedback_handler.load_feedback_data("feedback_data.json")