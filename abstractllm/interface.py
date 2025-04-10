"""
Abstract interface for LLM providers.
"""

from typing import Dict, Any, Optional, Union, Generator, AsyncGenerator
from abc import ABC, abstractmethod

from abstractllm.utils.config import ConfigurationManager
from abstractllm.enums import ModelParameter, ModelCapability

class AbstractLLMInterface(ABC):
    """
    Abstract interface for LLM providers.
    
    All LLM providers must implement this interface to ensure a consistent API.
    Each provider is responsible for managing its own configuration and defaults.
    """
    
    def __init__(self, config: Optional[Dict[Union[str, ModelParameter], Any]] = None):
        """
        Initialize the LLM provider.
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize config manager
        self.config_manager = ConfigurationManager(config)
    
    @abstractmethod
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None, 
                stream: bool = False, 
                **kwargs) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response to the prompt using the LLM.
        
        Args:
            prompt: The input prompt
            system_prompt: Override the system prompt in the config
            stream: Whether to stream the response (default: False)
            **kwargs: Additional parameters to override config
            
        Returns:
            If stream=False: The complete generated response as a string
            If stream=True: A generator yielding response chunks
            
        Raises:
            Exception: If the generation fails
        """
        pass
    
    @abstractmethod
    async def generate_async(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None, 
                          stream: bool = False, 
                          **kwargs) -> Union[str, AsyncGenerator[str, None]]:
        """
        Asynchronously generate a response to the prompt using the LLM.
        
        Args:
            prompt: The input prompt
            system_prompt: Override the system prompt in the config
            stream: Whether to stream the response (default: False)
            **kwargs: Additional parameters to override config
            
        Returns:
            If stream=False: The complete generated response as a string
            If stream=True: An async generator yielding response chunks
            
        Raises:
            Exception: If the generation fails
        """
        pass
        
    def get_capabilities(self) -> Dict[Union[str, ModelCapability], Any]:
        """
        Return capabilities of this LLM.
        
        Returns:
            Dictionary of capabilities
        """
        return {
            ModelCapability.STREAMING: False,
            ModelCapability.MAX_TOKENS: 2048,
            ModelCapability.SYSTEM_PROMPT: False,
            ModelCapability.ASYNC: False,
            ModelCapability.FUNCTION_CALLING: False,
            ModelCapability.VISION: False,
        }
        
    def set_config(self, **kwargs) -> None:
        """
        Update the configuration with individual parameters.
        
        Args:
            **kwargs: Configuration values to update
        """
        self.config_manager.update_config(kwargs)
        
    def update_config(self, config: Dict[Union[str, ModelParameter], Any]) -> None:
        """
        Update the configuration with a dictionary of parameters.
        
        Args:
            config: Dictionary of configuration values to update
        """
        self.config_manager.update_config(config)
        
    def get_config(self) -> Dict[Union[str, ModelParameter], Any]:
        """
        Get the current configuration.
        
        Returns:
            Current configuration as a dictionary
        """
        return self.config_manager.get_config()
        
    def get_param(self, param: Union[str, ModelParameter], default: Optional[Any] = None) -> Any:
        """
        Get a parameter value from configuration.
        
        Args:
            param: The parameter to retrieve
            default: Default value to return if the parameter is not found
            
        Returns:
            The value of the parameter or the default value if not found
        """
        return self.config_manager.get_param(param, default)
        
    def get_provider_params(self, kwargs: Dict[str, Any], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Get provider-specific parameters for generation.
        
        Args:
            kwargs: Additional parameters for generation
            system_prompt: Override the system prompt in the config
            
        Returns:
            Dictionary of provider-specific parameters
        """
        return self.config_manager.get_provider_params(kwargs, system_prompt) 