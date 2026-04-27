import yaml
import os
from typing import List
from app.models.service import VirtualService, Rule, MatchCondition, ResponseTemplate

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load_services(self) -> List[VirtualService]:
        if not os.path.exists(self.config_path):
            return []

        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)

        services = []
        for svc_data in data.get('services', []):
            rules = []
            for rule_data in svc_data.get('rules', []):
                match_conditions = []
                for mc in rule_data.get('match', []):
                    match_conditions.append(MatchCondition(
                        field=mc.get('field'),
                        type=mc.get('type'),
                        value=mc.get('value'),
                        key=mc.get('key')
                    ))
                
                resp_data = rule_data.get('response', {})
                response = ResponseTemplate(
                    body=resp_data.get('body'),
                    headers=resp_data.get('headers', {}),
                    delay_ms=resp_data.get('delay_ms', 0)
                )
                
                rules.append(Rule(
                    name=rule_data.get('name'),
                    match=match_conditions,
                    response=response
                ))
            
            services.append(VirtualService(
                name=svc_data.get('name'),
                input_queue=svc_data.get('input_queue'),
                output_queue=svc_data.get('output_queue'),
                rules=rules,
                active=svc_data.get('active', True)
            ))
        
        return services
