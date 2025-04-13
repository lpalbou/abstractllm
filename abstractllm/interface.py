"""
Abstract interface for LLM providers.
"""

from typing import Dict, Any, Optional, Union, Generator, AsyncGenerator, List
from abc import ABC, abstractmethod
from pathlib import Path

from abstractllm.utils.config import ConfigurationManager
from abstractllm.enums import ModelParameter, ModelCapability

class OutputHandler(ABC):
    """Abstract base class for output handlers."""
    
    @abstractmethod
    def handle(self, output: Union[str, Generator[str, None, None]]) -> None:
        """Handle output from the model.
        
        Args:
            output: Text output from the model (string or generator)
        """
        pass

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
        self.config_manager = ConfigurationManager(config or {})
        
        # Initialize output handlers
        self._output_handlers: List[OutputHandler] = []
    
    def add_output_handler(self, handler: OutputHandler) -> None:
        """Add an output handler.
        
        Args:
            handler: Output handler instance
        """
        self._output_handlers.append(handler)
    
    def remove_output_handler(self, handler: OutputHandler) -> None:
        """Remove an output handler.
        
        Args:
            handler: Output handler instance to remove
        """
        if handler in self._output_handlers:
            self._output_handlers.remove(handler)
    
    def clear_output_handlers(self) -> None:
        """Remove all output handlers."""
        self._output_handlers.clear()
    
    def _handle_output(self, output: Union[str, Generator[str, None, None]]) -> Union[str, Generator[str, None, None]]:
        """Process output through all handlers and return it.
        
        Args:
            output: Model output to process
            
        Returns:
            The original output (after processing by handlers)
        """
        # Process through all handlers
        for handler in self._output_handlers:
            try:
                handler.handle(output)
            except Exception as e:
                # Log error but continue with other handlers
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Output handler {handler.__class__.__name__} failed: {e}")
        
        # Return original output
        return output
    
    @abstractmethod
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None, 
                files: Optional[List[Union[str, Path]]] = None,
                stream: bool = False, 
                **kwargs) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: The input prompt
            system_prompt: Override the system prompt in the config
            files: Optional list of files to process (paths or URLs)
                  Supported types: images (for vision models), text, markdown, CSV, TSV
            stream: Whether to stream the response
            **kwargs: Additional parameters to override configuration
            
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
                          files: Optional[List[Union[str, Path]]] = None,
                          stream: bool = False, 
                          **kwargs) -> Union[str, AsyncGenerator[str, None]]:
        """
        Asynchronously generate a response using the LLM.
        
        Args:
            prompt: The input prompt
            system_prompt: Override the system prompt in the config
            files: Optional list of files to process (paths or URLs)
                  Supported types: images (for vision models), text, markdown, CSV, TSV
            stream: Whether to stream the response
            **kwargs: Additional parameters to override configuration
            
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