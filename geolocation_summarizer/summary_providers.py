#!/usr/bin/env python3
"""
Summary Providers

This module provides different LLM providers for hierarchical grid summarization.
Supports OpenAI GPT and Google Gemini models.
"""

import json
import asyncio
import aiohttp
from typing import Dict, List
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SummaryProvider(ABC):
    """Abstract base class for summary providers"""
    
    @abstractmethod
    async def summarize_batch(self, cell_descriptions: List[str], level: int, kernel_size: int) -> Dict[str, str]:
        """Summarize a batch of cells"""
        pass

class OpenAISummaryProvider(SummaryProvider):
    """OpenAI GPT summary provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
    async def summarize_batch(self, cell_descriptions: List[str], level: int, kernel_size: int) -> Dict[str, str]:
        """Summarize cells using OpenAI GPT"""
        if not self.api_key:
            # Mock response for testing
            return self._get_mock_response(len(cell_descriptions))
        
        prompt = f"""
Analyze the following location cells and provide concise summaries for each cell's character/context, keep the summaries at max 5 words.

Level: {level} (Kernel size: {kernel_size}x{kernel_size})

Cells to analyze:
{chr(10).join(cell_descriptions)}

Return your response as a JSON object:
{{
    "summaries": {{
        "1": "Brief summary for cell 1",
        "2": "Brief summary for cell 2",
        ...
    }}
}}

Each summary should be at max 5 words describing the area's character based on the combined tags.
"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a location analysis expert. Provide concise, accurate summaries of area characteristics based on user-generated tags."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    return self._parse_response(response_text, len(cell_descriptions))
                else:
                    raise Exception(f"OpenAI API call failed with status {response.status}")
    
    def _parse_response(self, response_text: str, num_cells: int) -> Dict[str, str]:
        """Parse the JSON response from OpenAI"""
        try:
            result_data = json.loads(response_text)
            summaries = result_data.get("summaries", {})
            
            # Convert to our format
            result = {}
            for i in range(num_cells):
                cell_key = str(i + 1)  # OpenAI uses 1-based indexing
                result[str(i)] = summaries.get(cell_key, "No summary available")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {str(i): "Error parsing response" for i in range(num_cells)}
    
    def _get_mock_response(self, num_cells: int) -> Dict[str, str]:
        """Get mock response for testing"""
        mock_summaries = [
            "Urban area with mixed social characteristics and community dynamics",
            "Diverse neighborhood showing varied demographic patterns",
            "Mixed-use zone with different community groups",
            "Urban area with contrasting social interactions",
            "Diverse neighborhood with varied social dynamics",
            "Mixed community area with different social patterns",
            "Urban zone with diverse social characteristics",
            "Community area with mixed social dynamics",
            "Diverse area with varied social patterns",
            "Mixed neighborhood with different social interactions",
            "Urban zone with diverse community characteristics",
            "Community zone with mixed social dynamics",
            "Diverse neighborhood with varied social interactions",
            "Mixed-use area with different community patterns",
            "Urban area with diverse social characteristics"
        ]
        
        result = {}
        for i in range(num_cells):
            result[str(i)] = mock_summaries[i % len(mock_summaries)]
        
        return result

class GeminiSummaryProvider(SummaryProvider):
    """Google Gemini summary provider"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        
    async def summarize_batch(self, cell_descriptions: List[str], level: int, kernel_size: int) -> Dict[str, str]:
        """Summarize cells using Google Gemini"""
        if not self.api_key:
            # Mock response for testing
            return self._get_mock_response(len(cell_descriptions))
        
        try:
            from google import genai
            
            # Initialize Gemini client
            client = genai.Client(api_key=self.api_key)
            
            prompt = f"""
Analyze the following location cells and provide concise summaries for each cell's character/context, keep the summaries in at max 5 words.

Level: {level} (Kernel size: {kernel_size}x{kernel_size})

Cells to analyze:
{chr(10).join(cell_descriptions)}

Return your response as a JSON object:
{{
    "summaries": {{
        "1": "Brief summary for cell 1",
        "2": "Brief summary for cell 2",
        ...
    }}
}}

Each summary should be at max 5 words describing the area's character based on the combined tags.
"""
            
            print(f"📤 Sending to Gemini:")
            print(f"   Model: {self.model}")
            print(f"   Prompt: {prompt}")
            print(f"   Cell descriptions: {len(cell_descriptions)} cells")
            
            # Generate content using Gemini
            response = client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            response_text = response.text
            return self._parse_response(response_text, len(cell_descriptions))
            
        except ImportError:
            print("Google Gemini library not installed. Install with: pip install google-generativeai")
            return self._get_mock_response(len(cell_descriptions))
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            return self._get_mock_response(len(cell_descriptions))
    
    def _parse_response(self, response_text: str, num_cells: int) -> Dict[str, str]:
        """Parse the JSON response from Gemini"""
        try:
            # Handle markdown code blocks that Gemini sometimes returns
            if response_text.startswith("```json"):
                # Extract JSON from markdown code block
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
            elif response_text.startswith("```"):
                # Handle other code blocks
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.strip().startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)
            
            result_data = json.loads(response_text)
            summaries = result_data.get("summaries", {})
            
            # Convert to our format
            result = {}
            for i in range(num_cells):
                cell_key = str(i + 1)  # Gemini uses 1-based indexing
                result[str(i)] = summaries.get(cell_key, "No summary available")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {str(i): "Error parsing response" for i in range(num_cells)}
    
    def _get_mock_response(self, num_cells: int) -> Dict[str, str]:
        """Get mock response for testing"""
        mock_summaries = [
            "Urban area with mixed social characteristics and community dynamics",
            "Diverse neighborhood showing varied demographic patterns",
            "Mixed-use zone with different community groups",
            "Urban area with contrasting social interactions",
            "Diverse neighborhood with varied social dynamics",
            "Mixed community area with different social patterns",
            "Urban zone with diverse social characteristics",
            "Community area with mixed social dynamics",
            "Diverse area with varied social patterns",
            "Mixed neighborhood with different social interactions",
            "Urban zone with diverse community characteristics",
            "Community zone with mixed social dynamics",
            "Diverse neighborhood with varied social interactions",
            "Mixed-use area with different community patterns",
            "Urban area with diverse social characteristics"
        ]
        
        result = {}
        for i in range(num_cells):
            result[str(i)] = mock_summaries[i % len(mock_summaries)]
        
        return result

class SummaryProviderFactory:
    """Factory for creating summary providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> SummaryProvider:
        """Create a summary provider based on type"""
        if provider_type.lower() == "openai":
            return OpenAISummaryProvider(**kwargs)
        elif provider_type.lower() == "gemini":
            return GeminiSummaryProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available provider types"""
        return ["openai", "gemini"]

# Example usage
if __name__ == "__main__":
    async def test_providers():
        """Test both providers"""
        cell_descriptions = [
            "Cell 1 (lat: 28.574, lon: 77.232): only sexy ppl here",
            "Cell 2 (lat: 28.754, lon: 77.122): zone of jee fails",
            "Cell 3 (lat: 28.564, lon: 77.242): The Cool Guys territory"
        ]
        
        # Test OpenAI
        print("Testing OpenAI provider...")
        openai_provider = SummaryProviderFactory.create_provider("openai")
        openai_result = await openai_provider.summarize_batch(cell_descriptions, 0, 1)
        print(f"OpenAI result: {openai_result}")
        
        # Test Gemini
        print("\nTesting Gemini provider...")
        gemini_provider = SummaryProviderFactory.create_provider("gemini")
        gemini_result = await gemini_provider.summarize_batch(cell_descriptions, 0, 1)
        print(f"Gemini result: {gemini_result}")
    
    asyncio.run(test_providers())
