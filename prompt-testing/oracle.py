import google.generativeai
generation_config = google.generativeai.GenerationConfig(temperature=0.0, top_p=0.5, max_output_tokens=1024)

from time import sleep

# Put your API keys here.
api_keys = []

import google.generativeai as genai
genai.configure(api_key=api_keys[1])
model = genai.GenerativeModel('gemini-1.5-flash')

def oracle(article_text, prompt):
    # sleep(0.1)
    negative = ["無。", "无。"]
    while True:
        try:
            response = model.generate_content(
                contents = prompt.replace("<the_transcription>", article_text),
                generation_config = generation_config,
                safety_settings = [ {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}, ]
            )

            return response.text.strip(" \n") not in negative

        except Exception as e:
            if str(e)[:17] == "Invalid operation":
                print(article_text[:10])
                return False

            print(f"Error: {e}")
            sleep(5)

def oracle_return_text(article_text, prompt):
    negative = ["無。", "无。"]
    while True:
        try:
            response = model.generate_content(
                contents = prompt.replace("<the_transcription>", article_text),
                generation_config = generation_config,
                safety_settings = [ {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}, ]
            )

            return response.text

        except Exception as e:
            if str(e)[:17] == "Invalid operation":
                print(article_text[:10])
                return "無。"

            print(f"Error: {e}")
            sleep(5)

