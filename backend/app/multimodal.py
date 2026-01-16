"""
Multimodal input processing: voice transcription and image analysis.
Uses On-Demand platform's audio and vision agents with user-provided or platform API keys.
"""

import base64
import logging
from typing import Optional, Tuple
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


async def transcribe_voice(
    audio_file_path: str,
    user_api_key: Optional[str] = None,
) -> str:
    """
    Transcribe audio to text using On-Demand audio agent.
    
    Args:
        audio_file_path: Path to the audio file (mp3, wav, m4a, etc.)
        user_api_key: Optional user's On-Demand API key (uses platform key if not provided)
        
    Returns:
        Transcribed text
    """
    try:
        api_key = user_api_key or settings.ON_DEMAND_API_KEY
        if not api_key:
            raise ValueError("No API key available for transcription")
        
        client = OnDemandClient(api_key=api_key)
        
        # Read audio file
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        # Use on-demand audio transcription
        transcript = await client.transcribe_audio(
            audio_file_path=audio_file_path,
            agent_ids=[settings.ON_DEMAND_AUDIO_AGENT],
        )
        
        logger.info(f"Transcribed audio: {len(transcript)} chars")
        return transcript
    
    except FileNotFoundError:
        logger.error(f"Audio file not found: {audio_file_path}")
        raise ValueError(f"Audio file not found: {audio_file_path}")
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise ValueError(f"Failed to transcribe audio: {str(e)}")


async def analyze_image(
    image_file_path: str,
    user_api_key: Optional[str] = None,
    context: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Analyze an image using On-Demand vision agent.
    
    Args:
        image_file_path: Path to the image file (jpg, png, gif, webp)
        user_api_key: Optional user's On-Demand API key (uses platform key if not provided)
        context: Optional context hint (e.g., "job offer", "investment chart")
        
    Returns:
        Tuple of (image_description, vision_summary_text)
    """
    try:
        api_key = user_api_key or settings.ON_DEMAND_API_KEY
        if not api_key:
            raise ValueError("No API key available for image analysis")
        
        client = OnDemandClient(api_key=api_key)
        
        # Read image file
        with open(image_file_path, "rb") as img_file:
            image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
        
        # Create analysis query
        query = f"""Analyze this image in the context of decision-making.
Provide a 2-3 sentence summary focusing on:
- Key facts, numbers, or insights
- Relevance to decision-making
- Actionable takeaways

{f'Context: {context}' if context else ''}

Image: {image_file_path}"""
        
        # Call on-demand vision agent
        summary = await client.analyze_image(
            image_file_path=image_file_path,
            query=query,
            agent_ids=[settings.ON_DEMAND_VISION_AGENT],
        )
        
        logger.info(f"Image analyzed: {len(summary)} chars summary")
        
        return image_file_path, summary
    
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_file_path}")
        raise ValueError(f"Image file not found: {image_file_path}")
    except Exception as e:
        logger.error(f"Image analysis error: {e}", exc_info=True)
        raise ValueError(f"Failed to analyze image: {str(e)}")