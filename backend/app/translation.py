# """
# Language detection and translation to English.
# Uses OpenAI API with user-provided API keys.
# """

# import logging
# from openai import OpenAI

# logger = logging.getLogger(__name__)


# def get_user_client(user_api_key: str) -> OpenAI:
#     """Create an OpenAI client using the user's provided API key."""
#     if not user_api_key or not user_api_key.strip():
#         raise ValueError("User API key is required")
#     return OpenAI(api_key=user_api_key)


# async def detect_language(text: str, user_api_key: str) -> str:
#     """
#     Detect the language of the given text using OpenAI.
    
#     Args:
#         text: Input text
#         user_api_key: User's OpenAI API key
        
#     Returns:
#         Language code (e.g., 'en', 'hi', 'es') or 'en' if already English
#     """
#     try:
#         if not text or len(text.strip()) < 5:
#             return "en"
        
#         client = get_user_client(user_api_key)
        
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "Identify the language of the given text. Respond with ONLY the ISO 639-1 language code (e.g., 'en', 'hi', 'es', 'fr').",
#                 }
#             ],
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"Identify the language: {text[:100]}",
#                 }
#             ],
#             max_tokens=10,
#         )
        
#         lang_code = response.choices[0].message.content.strip().lower()
        
#         # Ensure it's a valid code
#         if len(lang_code) != 2:
#             logger.warning(f"Unexpected language code: {lang_code}, defaulting to 'en'")
#             return "en"
        
#         logger.info(f"Detected language: {lang_code}")
#         return lang_code
    
#     except Exception as e:
#         logger.error(f"Language detection error: {e}, defaulting to 'en'")
#         return "en"


# async def translate_to_english(text: str, user_api_key: str) -> str:
#     """
#     Translate text to English if it's not already in English.
    
#     Args:
#         text: Input text in any language
#         user_api_key: User's OpenAI API key
        
#     Returns:
#         English translation or original text if already in English
#     """
#     try:
#         if not text or len(text.strip()) < 5:
#             return text
        
#         # Detect language first
#         lang_code = await detect_language(text, user_api_key)
        
#         if lang_code == "en":
#             logger.info("Text already in English, skipping translation")
#             return text
        
#         client = get_user_client(user_api_key)
        
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": f"Translate the following text from {lang_code} to English. Preserve the meaning and tone. Return ONLY the translation, no additional text.",
#                 },
#                 {
#                     "role": "user",
#                     "content": text,
#                 },
#             ],
#             max_tokens=2000,
#         )
        
#         translated = response.choices[0].message.content.strip()
#         logger.info(f"Translated from {lang_code} to English: {len(translated)} chars")
        
#         return translated
    
#     except Exception as e:
#         logger.error(f"Translation error: {e}, returning original text")
#         return text

#gemini

"""
Language detection and translation to English.
Uses OpenAI API with user-provided API keys.
"""

import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)

def get_user_client(user_api_key: str) -> OpenAI:
    """Create an OpenAI client using the user's provided API key."""
    if not user_api_key or not user_api_key.strip():
        raise ValueError("User API key is required")
    return OpenAI(api_key=user_api_key)

async def detect_language(text: str, user_api_key: str) -> str:
    """
    Detect the language of the given text using OpenAI.
    
    Returns:
        Language code (e.g., 'en', 'hi', 'es') or 'en' if already English
    """
    try:
        if not text or len(text.strip()) < 5:
            return "en"
        
        client = get_user_client(user_api_key)
        
        # FIXED: Merged the two messages lists into one
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Identify the language of the given text. Respond with ONLY the ISO 639-1 language code (e.g., 'en', 'hi', 'es', 'fr').",
                },
                {
                    "role": "user",
                    "content": f"Identify the language: {text[:100]}",
                }
            ],
            max_tokens=10,
        )
        
        lang_code = response.choices[0].message.content.strip().lower()
        
        # Ensure it's a valid code (basic ISO check)
        if len(lang_code) > 3: # Some codes are 3 letters, but mostly 2
            lang_code = lang_code[:2]
            
        logger.info(f"Detected language: {lang_code}")
        return lang_code
    
    except Exception as e:
        logger.error(f"Language detection error: {e}, defaulting to 'en'")
        return "en"

async def translate_to_english(text: str, user_api_key: str) -> str:
    """
    Translate text to English if it's not already in English.
    """
    try:
        if not text or len(text.strip()) < 5:
            return text
        
        # Detect language first
        lang_code = await detect_language(text, user_api_key)
        
        if lang_code == "en":
            logger.info("Text already in English, skipping translation")
            return text
        
        client = get_user_client(user_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text from ISO code {lang_code} to English. Preserve the meaning and tone. Return ONLY the translation, no additional text.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            max_tokens=2000,
        )
        
        translated = response.choices[0].message.content.strip()
        logger.info(f"Translated from {lang_code} to English: {len(translated)} chars")
        
        return translated
    
    except Exception as e:
        logger.error(f"Translation error: {e}, returning original text")
        return text