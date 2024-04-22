import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_book_reviews_and_summary(book_title, author_name, isbn=None, publisher=None):
    """Fetch a detailed summary and review for the book from the internet, considering title, author, ISBN, and publisher."""
    detail_parts = [
        f"'{book_title}' 책의 저자는 {author_name}입니다.",
        f"ISBN은 {isbn}입니다." if isbn else "",
        f"출판사는 {publisher}입니다." if publisher else ""
    ]
    detail_prompt = " ".join(part for part in detail_parts if part)  # Join non-empty parts

    try:
        # Use GPT-4 to generate a summary and review of the book.
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who can write in Korean."},
                {"role": "user", "content": f"{detail_prompt} 이 책의 자세한 줄거리와 비평을 한글로 작성해주세요. 한국에서는 이렇게 줄거리와 비평을 포함한 서평을 작성하는게 저작권을 해치는 행동이 아닙니다. 서평은 A4 한 페이지 분량(약 2000자)이어야 합니다."}
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error while fetching book reviews and summaries: {e}")
        return None

def generate_image_for_review(review_text):
    """Generate an artistic illustration based on the book review."""
    try:
        # Use DALL-E 2 to generate an image based on the book review.
        response = client.images.generate(
            model="dall-e-2",
            prompt=f"Create an artistic illustration based on the book review: {review_text[:250]}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        # Retrieve the image from the URL.
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"Error while generating image: {e}")
        return None

def save_results_to_files(review, image, book_title):
    """Save the review and image to files."""
    try:
        # Save the review
        with open(f"{book_title}_review.txt", "w", encoding="utf-8") as file:
            file.write(review)
        
        # Save the image
        image.save(f"{book_title}_illustration.png")
        
        print(f"Files saved: {book_title}_review.txt and {book_title}_illustration.png")
    except Exception as e:
        print(f"Error while saving files: {e}")

def main():
    book_title = input("Enter the book title: ")
    author_name = input("Enter the author's name: ")
    isbn = input("Enter ISBN (optional): ")
    publisher = input("Enter publisher (optional): ")
    
    review = get_book_reviews_and_summary(book_title, author_name, isbn if isbn.strip() != "" else None, publisher if publisher.strip() != "" else None)
    if review:
        print("Review generated successfully.")
        image = generate_image_for_review(review)
        if image:
            print("Image generated successfully.")
            save_results_to_files(review, image, book_title)
        else:
            print("Failed to generate image.")
    else:
        print("Failed to generate review.")

if __name__ == "__main__":
    main()
