import logging
from typing import Dict, List, Optional, Type
from friday.providers.base.provider import Provider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    def __init__(self):
        # Maps category -> {provider_name -> ProviderInstance}
        self._providers: Dict[str, Dict[str, Provider]] = {}
        # Fallback preference list: category -> list of provider names in order of preference
        self._fallbacks: Dict[str, List[str]] = {}

    def register(self, provider: Provider) -> None:
        category = provider.metadata.category.lower()
        name = provider.metadata.name.lower()
        
        if category not in self._providers:
            self._providers[category] = {}
        
        self._providers[category][name] = provider
        logger.info(f"Registered provider: {category}/{name}")

    def get_provider(self, category: str, name: str) -> Optional[Provider]:
        category = category.lower()
        name = name.lower()
        return self._providers.get(category, {}).get(name)

    def list_providers(self, category: str) -> List[Provider]:
        return list(self._providers.get(category.lower(), {}).values())

    def set_fallbacks(self, category: str, fallback_names: List[str]) -> None:
        self._fallbacks[category.lower()] = [n.lower() for n in fallback_names]

    def get_fallback_chain(self, category: str, primary_name: str) -> List[Provider]:
        category = category.lower()
        primary_name = primary_name.lower()
        
        chain = []
        # Add primary
        primary = self.get_provider(category, primary_name)
        if primary:
            chain.append(primary)
            
        # Add other registered providers in the configured fallback list
        fallback_list = self._fallbacks.get(category, [])
        for name in fallback_list:
            if name != primary_name:
                prov = self.get_provider(category, name)
                if prov and prov not in chain:
                    chain.append(prov)
                    
        # Add any remaining registered providers in the category as ultimate fallbacks
        for name, prov in self._providers.get(category, {}).items():
            if prov not in chain:
                chain.append(prov)
                
        return chain
