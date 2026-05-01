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
        
        if "ping" in prompt_lower or "health" in prompt_lower:
            config["rules"].append({
                "rule_name": "HealthCheck",
                "condition": "message_type == 'PING'",
                "action": "respond_with: 'PONG'"
            })

        if "approval" in prompt_lower or "limit" in prompt_lower:
            config["rules"].append({
                "rule_name": "HighValueApproval",
                "condition": "amount > 5000",
                "action": "respond_with: '{\"status\": \"PENDING_APPROVAL\", \"notice\": \"Amount exceeds auto-limit\"}'"
            })

        if not config["rules"]:
            # Context-aware fallback
            topic = prompt.split()[-1].capitalize() if prompt.split() else "Generic"
            config["rules"].append({
                "rule_name": f"{topic}Handler",
                "condition": "True",
                "action": f"respond_with: 'Generated response for {prompt}'"
            })

        return config
