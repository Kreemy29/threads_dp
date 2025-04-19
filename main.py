# main.py

import os
import random
import requests
from config import URL_DEEPSEEK, HEADERS, OUTPUT_FILE_PATH
from data import load_captions
from generator import generate_baity_prompt, generate_opinion_prompt, generate_event_prompt

def main():
    captions_baity, captions_opinion = load_captions()

    if not captions_baity or not captions_opinion:
        print("❌ Could not load captions. Please check your CSV/TXT files.")
        return

    # Ensure the output directory exists
    output_dir = os.path.dirname(OUTPUT_FILE_PATH)
    os.makedirs(output_dir, exist_ok=True)

    used_baity = set()
    used_opinion = set()
    used_events = set()

    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
        print("\nGenerating a mix of 'baity', 'opinion', and 'event' captions:\n")

        for _ in range(30):
            style_choice = random.choice(["baity", "opinion", "event"])
            location = random.choice(["New York", "California", "Texas", "Florida", "Illinois"])

            if style_choice == "baity":
                base_prompt = random.choice(captions_baity)
                while base_prompt in used_baity:
                    base_prompt = random.choice(captions_baity)
                used_baity.add(base_prompt)

                dynamic_prompt = generate_baity_prompt(location)
                system_content = (
                    "You are a creative assistant generating fresh, flirty, and inviting social media captions. "
                    "Keep the tone cheeky and engaging, but avoid using hashtags or tags. "
                    "Mention only one news or weather item if relevant—do not add extra topics."
                )
                user_message = f"{base_prompt}\n\n{dynamic_prompt}"

            elif style_choice == "opinion":
                base_prompt = random.choice(captions_opinion)
                while base_prompt in used_opinion:
                    base_prompt = random.choice(captions_opinion)
                used_opinion.add(base_prompt)

                dynamic_prompt = generate_opinion_prompt(base_prompt, location)
                system_content = (
                    "You are a creative assistant generating real, relatable, and location-based social media captions. "
                    "Reference only the single local news headline. Do not add extra or unrelated topics. "
                    "Keep it concise and avoid hashtags or tags."
                )
                user_message = dynamic_prompt

            else:
                base_prompt = random.choice(captions_opinion)
                while base_prompt in used_events:
                    base_prompt = random.choice(captions_opinion)
                used_events.add(base_prompt)

                dynamic_prompt = generate_event_prompt(base_prompt)
                system_content = (
                    "You are a creative assistant generating real, relatable, and location-based social media captions "
                    "focusing on a single local concert or festival event. Do not add unrelated topics. "
                    "Keep it concise and avoid hashtags or tags."
                )
                user_message = dynamic_prompt

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_message}
                ],
                "stream": False,
                "n": 1
            }

            response = requests.post(URL_DEEPSEEK, json=payload, headers=HEADERS)
            if response.status_code == 200:
                generated_text = response.json().get("choices", [])[0]['message']['content']
                print(f"[{style_choice.upper()}] Generated Caption: {generated_text}")
                output_file.write(f"{generated_text}\n")
            else:
                print(f"DeepSeek API Error {response.status_code}: {response.text}")

    print(f"\n✅ All generated captions are saved to: {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    main()
