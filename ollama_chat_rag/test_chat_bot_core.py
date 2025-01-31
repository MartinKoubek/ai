import pytest
from chat_bot_core import ChatBotCore
from langchain.evaluation import load_evaluator

class TestChatBot:
    @pytest.fixture(scope="class")
    def chatbot(self):
        return ChatBotCore()


    def evaluate_response(self, response, expected_answer):
        evaluator = load_evaluator("qa")
        result = evaluator.evaluate(predictions=[response], references=[expected_answer])
        return 1 if result["score"] > 0.5 else 0

    @pytest.mark.parametrize("question, expected_answer", [
        ("What is 2+2?", "4"),
        # ("What is the capital of France?", "Paris"),
        # ("Who wrote Hamlet?", "William Shakespeare")
        ]
    )
    def test_chatbot_responses(self, chatbot, question, expected_answer):
        chatbot.set_question(question)
        response = chatbot.get_answer()

        print (response)
        score = self.evaluate_response(response, expected_answer)
        assert score == 1  # Ensure response matches expected answer
