import os, json, uuid
from types import SimpleNamespace
from typing import Any, Dict, List, Generator, Tuple, Optional
import re

import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part, Content

from core.providers.llm.base import LLMProviderBase
from config.logger import setup_logging

log = setup_logging()
TAG = __name__

from core.utils.emotion_manager import emotion_manager
# Generate dynamic emotion list from configuration
emotion_descriptions = emotion_manager.get_emotion_descriptions()
emotion_list = "\n".join([f"- {emotion}: {desc}" for emotion, desc in emotion_descriptions.items()])

emotional_prompt = f"""
    EMOTIONAL EXPRESSION

    As your character, you should express emotions contextually. Before each response, choose an appropriate emotion for your character to display. The "strange" emotions like elf and snowman are used for when the topic is centered around them.

    Available robot emotions:
    {emotion_list}
    - {emotion_manager.default_emotion}: Default/fallback emotion

    IMPORTANT: Start each response with [EMOTION:emotion_name] where emotion_name is one of the emotions listed above. For example: [EMOTION:neutral] or [EMOTION:bell] or [EMOTION:star]
"""

FUNCTION_CALLING_PROMPT = """
CRITICAL FUNCTION CALLING RULES:

When the user asks you to perform physical actions (shake, move, dance, etc.), you MUST:
1. Use the available function tools immediately - DO NOT write code or describe the action as code
2. Call the appropriate function and then respond naturally about what you're doing
3. NEVER output code like "print(default_api.function())" or "function()" - use actual function calls
4. After calling a function, provide a natural conversational response

Examples:
✅ CORRECT:
- User: "shake your body"
- You: [Call self_chassis_shake_body_start function] "I'm shaking my body for you!"

❌ WRONG:
- User: "shake your body" 
- You: "print(default_api.self_chassis_shake_body())" or "self_chassis_shake_body_start()"

Available physical actions require function calls:
- Shaking: use self_chassis_shake_body_start/stop functions
- Moving: use self_chassis_move_* functions  
- Any physical action: use the corresponding function tools

Remember: Execute functions silently, then speak naturally about the action.
"""

class LLMProvider(LLMProviderBase):
    def __init__(self, cfg: Dict[str, Any]):
        log.bind(tag=TAG).info(f"Initializing Gemini Vertex AI provider with config: {cfg}")
        try:
            self.model_name = cfg.get("model_name", "gemini-2.0-flash")

            # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not credentials_path or not os.path.exists(credentials_path):
                raise KeyError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or points to a non-existent file.")
        except KeyError as e:
            log.bind(tag=TAG).error(f"Configuration missing for Vertex AI. Required key not found: {e}. Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
            raise e

        vertexai.init()
        self.model = GenerativeModel(self.model_name)
        self.chats: Dict[str, Any] = {}

        self.gen_cfg = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

    @staticmethod
    def _build_tools(funcs: List[Dict[str, Any]] | None):
        if not funcs:
            return None
        return [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name=f["function"]["name"],
                        description=f["function"]["description"],
                        parameters=f["function"]["parameters"],
                    )
                    for f in funcs
                ]
            )
        ]

    def response(self, session_id: str, dialogue: List[Dict], **kwargs) -> Generator[str, None, None]:
        """Generate response without function calls - optimized for speed"""
        try:
            for content in self._generate(session_id, dialogue, None):
                if isinstance(content, str) and content.strip():
                    # Quick filter for obvious code patterns only
                    if not self._is_obvious_code(content):
                        yield content
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield f"I apologize, but I encountered an error. Please try again."

    def response_with_functions(self, session_id: str, dialogue: List[Dict], functions=None) -> Generator[Tuple[Optional[str], Optional[List]], None, None]:
        """Generate response with function calls - optimized for speed"""
        try:
            for result in self._generate(session_id, dialogue, self._build_tools(functions)):
                yield result
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield f"I encountered an error: {str(e)}", None

    def _generate(self, session_id: str, dialogue: List[Dict], tools):
        """Simplified generation logic - similar to OpenAI approach"""
        
        chat = self.chats.get(session_id)
        
        # Create chat session only if needed 
        if not chat:
            chat = self._create_chat_session(session_id, dialogue)

        # Get the latest message to send
        latest_message = dialogue[-1] if dialogue else None
        
        if not latest_message or not latest_message.get("content"):
            if tools is None:
                return
            else:
                yield None, None
                return

        try:
            stream = chat.send_message(
                content=latest_message["content"],
                generation_config=self.gen_cfg,
                tools=tools,
                stream=True,
            )
            
            # Simplified stream processing - similar to OpenAI
            yield from self._process_stream_fast(stream, tools)
            
        except Exception as e:
            log.bind(tag=TAG).error(f"Error calling Vertex AI: {e}")
            if tools is None:
                yield f"I'm having technical difficulties. Please try again."
            else:
                yield "Technical issues occurred.", None

    def _create_chat_session(self, session_id: str, dialogue: List[Dict]):
        """Simplified chat creation - more like OpenAI stateless approach"""
        role_map = {"assistant": "model", "user": "user"}
        history: list[Content] = []
        system_instruction = None

        # Handle system instruction
        if dialogue and dialogue[0].get("role") == "system":
            original_instruction = dialogue[0].get("content", "")
            
            # Simplified enhanced instruction
            system_instruction = f"""
{emotional_prompt}

{FUNCTION_CALLING_PROMPT}

{original_instruction}
"""
            dialogue = dialogue[1:]

        model = GenerativeModel(self.model_name, system_instruction=system_instruction)


        # Simplified history building - exclude last message
        for m in dialogue[:-1]:
            r = m["role"]
            
            try:
                if r == "assistant" and "tool_calls" in m:
                    tc = m["tool_calls"][0]
                    history.append(Content(role="model", parts=[Part.from_dict({
                        'function_call': {
                            'name': tc['function']['name'],
                            'args': json.loads(tc['function']['arguments'])
                        }
                    })]))
                    continue

                if r == "tool":
                    history.append(Content(role="function", parts=[Part.from_dict({
                        'function_response': {
                            'name': m.get('name', 'unknown'),
                            'response': {'content': str(m.get('content', ''))}
                        }
                    })]))
                    continue

                mapped_role = role_map.get(r)
                if mapped_role:
                    content_text = str(m.get("content", "")).strip()
                    if content_text:
                        history.append(Content(role=mapped_role, parts=[Part.from_text(content_text)]))
                            
            except Exception as e:
                log.bind(tag=TAG).debug(f"Error processing dialogue message: {e}")
                continue

        chat = model.start_chat(history=history)
        self.chats[session_id] = chat
        return chat

    def _process_stream_fast(self, stream, tools) -> Generator:
        """Fast stream processing - similar to OpenAI approach"""
        function_calls_found = []
        
        try:
            for chunk in stream:
                if not chunk.candidates:
                    continue
                
                candidate = chunk.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    continue
                
                for part in candidate.content.parts:
                    # Handle function calls
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        function_call = SimpleNamespace(
                            id=uuid.uuid4().hex,
                            type="function",
                            function=SimpleNamespace(
                                name=fc.name,
                                arguments=json.dumps(dict(fc.args), ensure_ascii=False),
                            ),
                        )
                        function_calls_found.append(function_call)
                        
                    # Handle text content
                    elif hasattr(part, 'text') and part.text:
                        text_content = part.text.strip()
                        if text_content:
                            # Fast filtering - only check for obvious code patterns
                            if tools is not None and self._is_obvious_code(text_content):
                                # Try quick extraction
                                extracted_function = self._quick_extract_function(text_content)
                                if extracted_function:
                                    function_call = SimpleNamespace(
                                        id=uuid.uuid4().hex,
                                        type="function",
                                        function=SimpleNamespace(
                                            name=extracted_function,
                                            arguments="{}",
                                        ),
                                    )
                                    function_calls_found.append(function_call)
                                continue
                            
                            # Yield immediately - like OpenAI
                            if tools is None:
                                yield text_content
                            else:
                                yield text_content, None

            # Return function calls if any were found
            if function_calls_found and tools is not None:
                yield None, function_calls_found
                
        except Exception as e:
            log.bind(tag=TAG).error(f"Error processing stream: {e}")
            if tools is None:
                yield f"Processing error."
            else:
                yield "Processing error.", None
        finally:
            if tools is not None:
                yield None, None

    def _is_obvious_code(self, text: str) -> bool:
        """Fast check for obvious code patterns only"""
        if not text or len(text.strip()) == 0:
            return False
            
        text_lower = text.lower().strip()
        
        # Only check the most obvious code patterns for speed
        obvious_patterns = [
            'print(',
            'default_api.',
            'self_chassis_',
            '()',
        ]
        
        for pattern in obvious_patterns:
            if pattern in text_lower:
                return True
        
        # Quick check for very short return-like values
        if len(text.strip()) < 6 and text_lower in ['none', 'true', 'false']:
            return True
        
        return False

    def _quick_extract_function(self, text: str) -> Optional[str]:
        """Quick function extraction - simplified"""
        if not text:
            return None
            
        # Quick regex for common patterns
        if 'self_chassis_' in text.lower():
            match = re.search(r'(self_chassis_\w+)', text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        if 'shake' in text.lower():
            return 'self_chassis_shake_body_start'
        
        return None

    def cleanup_session(self, session_id: str):
        """Clean up session"""
        if session_id in self.chats:
            del self.chats[session_id]