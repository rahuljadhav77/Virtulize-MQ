import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    async def generate_config(prompt: str) -> Dict[str, Any]:
        """
        Simulates an LLM generating a VirtualServiceConfig from a prompt.
        In a real enterprise app, this would call OpenAI/Gemini/Anthropic.
        """
        logger.info(f"AI generating config for prompt: {prompt}")
        
        # Heuristic simulation for demo purposes
        prompt_lower = prompt.lower()
        
        service_name = "AI_Generated_Service"
        if "bank" in prompt_lower or "payment" in prompt_lower:
            service_name = "PaymentGateway_Mock"
        elif "order" in prompt_lower:
            service_name = "OrderSystem_Mock"

        # Default structure
        config = {
            "service_name": service_name,
            "service_type": "ibm_mq",
            "input_queue": "AI.IN.QUEUE",
            "output_queue": "AI.OUT.QUEUE",
            "rules": []
        }

        # Simulated intelligent rule generation
        if "low balance" in prompt_lower or "balance" in prompt_lower:
            config["rules"].append({
                "rule_name": "LowBalanceAlert",
                "condition": "amount < 100",
                "action": "respond_with: '{\"status\": \"REJECTED\", \"reason\": \"LOW_BALANCE\"}'"
            })
        
        if "ping" in prompt_lower:
            config["rules"].append({
                "rule_name": "HealthCheck",
                "condition": "message_type == 'PING'",
                "action": "respond_with: 'PONG'"
            })

        if not config["rules"]:
            # Generic fallback
            config["rules"].append({
                "rule_name": "GenericResponse",
                "condition": "True",
                "action": f"respond_with: 'AI generated response for: {prompt}'"
            })

        return config
