from src.clients.trivia_client import HttpTriviaClient
from src.logic.text_utils import decode_html_text


def main() -> None:
    client = HttpTriviaClient()
    questions = client.fetch_questions(question_count=5)

    print("--- 5 Questions from Open Trivia DB (Raw vs Decoded) ---")
    for index, question in enumerate(questions, start=1):
        raw_text = question.text
        decoded_text = decode_html_text(raw_text)
        print(f"[{index}] Raw:     {raw_text}")
        print(f"    Decoded: {decoded_text}")

    print("\n--- Example String Decoding ---")
    example_input = "  &quot;Hi&quot; &amp; bye "
    print(decode_html_text(example_input))


if __name__ == "__main__":
    main()
