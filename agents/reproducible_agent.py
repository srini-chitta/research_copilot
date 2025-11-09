"""
Custom OpenAI Agent wrapper that supports temperature and seed for reproducibility.
"""

from moya.agents.openai_agent import OpenAIAgent, OpenAIAgentConfig
from utils.trace_logger import get_trace_logger


class ReproducibleOpenAIAgent(OpenAIAgent):
    """
    Extended OpenAIAgent that supports temperature and seed parameters for reproducible outputs.
    Overrides get_response() to inject temperature and seed into all API calls.
    """
    
    def __init__(self, config: OpenAIAgentConfig, temperature: float = 0.0, seed: int = 42):
        """
        Initialize the ReproducibleOpenAIAgent.
        
        :param config: Configuration for the agent
        :param temperature: Temperature for LLM sampling (0.0 for deterministic)
        :param seed: Random seed for reproducibility
        """
        super().__init__(config)
        self.temperature = temperature
        self.seed = seed
    
    def get_response(self, conversation):
        """
        Override get_response to inject temperature and seed into OpenAI API calls.
        This ensures reproducibility for both streaming and non-streaming modes.
        
        Args:
            conversation (list): Current chat messages.
        
        Returns:
            dict: Message from the assistant, which may include 'tool_calls'.
        """
        trace_logger = get_trace_logger()
        
        # Log the LLM request
        user_message = next((msg['content'] for msg in reversed(conversation) if msg['role'] == 'user'), '')
        trace_logger.log_llm_request(
            agent_name=self.agent_name,
            model=self.model_name,
            prompt=user_message,
            temperature=self.temperature,
            seed=self.seed
        )
        
        if self.is_streaming:
            # Streaming mode with temperature and seed
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=conversation,
                tools=self.get_tool_definitions() or None,
                tool_choice=self.tool_choice if self.tool_registry else None,
                temperature=self.temperature,
                seed=self.seed,
                stream=True
            )
            response_text = ""
            tool_calls = []
            current_tool_call = None
            
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta:
                    if delta.content is not None:
                        response_text += delta.content
                        
                    if delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            tool_call_index = tool_call_delta.index
                            
                            # Ensure we have enough slots in our tool_calls list
                            while len(tool_calls) <= tool_call_index:
                                tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                                
                            current_tool_call = tool_calls[tool_call_index]
                            
                            # Update tool call information from this chunk
                            if tool_call_delta.id:
                                current_tool_call["id"] = tool_call_delta.id
                                
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    current_tool_call["function"]["name"] = tool_call_delta.function.name
                                    
                                if tool_call_delta.function.arguments:
                                    current_tool_call["function"]["arguments"] = (
                                        current_tool_call["function"].get("arguments", "") + 
                                        tool_call_delta.function.arguments
                                    )
            
            result = {"content": response_text}
            if tool_calls:
                result["tool_calls"] = tool_calls
            
            # Log the LLM response (streaming)
            trace_logger.log_llm_response(
                agent_name=self.agent_name,
                response=response_text
            )
            
            # Log tool calls if any
            if tool_calls:
                for tc in tool_calls:
                    trace_logger.log_tool_call(
                        agent_name=self.agent_name,
                        tool_name=tc.get('function', {}).get('name', 'unknown'),
                        arguments=tc.get('function', {}).get('arguments', {})
                    )
            
            return result
        else:
            # Non-streaming mode with temperature and seed
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=conversation,
                tools=self.get_tool_definitions(),
                tool_choice=self.tool_choice if self.tool_registry else None,
                temperature=self.temperature,
                seed=self.seed
            )
            message = response.choices[0].message
            
            # Convert the response to a dict for uniform handling
            result = {"content": message.content or ""}
            
            if message.tool_calls:
                # Convert tool_calls to a list of dicts
                if isinstance(message.tool_calls, list):
                    if not isinstance(message.tool_calls[0], dict):
                        result["tool_calls"] = [tc.dict() for tc in message.tool_calls]
                    else:
                        result["tool_calls"] = message.tool_calls
            
            # Log the LLM response (non-streaming)
            tokens = None
            if hasattr(response, 'usage'):
                tokens = {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }
            
            system_fingerprint = getattr(response, 'system_fingerprint', None)
            
            trace_logger.log_llm_response(
                agent_name=self.agent_name,
                response=message.content or "",
                tokens=tokens,
                system_fingerprint=system_fingerprint
            )
            
            # Log tool calls if any
            if message.tool_calls:
                for tc in message.tool_calls:
                    tc_dict = tc.dict() if not isinstance(tc, dict) else tc
                    trace_logger.log_tool_call(
                        agent_name=self.agent_name,
                        tool_name=tc_dict.get('function', {}).get('name', 'unknown'),
                        arguments=tc_dict.get('function', {}).get('arguments', {})
                    )
                        
            return result
