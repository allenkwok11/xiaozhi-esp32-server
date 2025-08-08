import os
import json
import uuid
from types import SimpleNamespace
from typing import Any, Dict, List, Generator, Tuple, Optional

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
    """
    Stateless Vertex AI Gemini provider optimized for MCP:
    - Rebuilds system instruction, full dialogue, and tools every request
    - Uses generate_content(stream=True) instead of persistent chats
    - Streams text chunks directly; passes through function_call parts
    - Handles GeneratorExit correctly (no yields after close)
    """

    def __init__(self, cfg: Dict[str, Any]):
        log.bind(tag=TAG).info(f"Initializing Gemini Vertex AI provider with config: {cfg}")
        try:
            self.model_name = cfg.get("model_name", "gemini-2.0-flash")

            # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not credentials_path or not os.path.exists(credentials_path):
                raise KeyError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or points to a non-existent file.")
        except KeyError as e:
            log.bind(tag=TAG).error(
                f"Configuration missing for Vertex AI. Required key not found: {e}. "
                f"Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )
            raise e

        vertexai.init()
        self.gen_cfg = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

    @staticmethod
    def _build_tools(funcs: Optional[List[Dict[str, Any]]]):
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
        """
        Generate a response without function calling. Streams plain text chunks.
        session_id is ignored to keep the provider stateless per MCP turn.
        """
        try:
            for content in self._generate_stateless(dialogue, tools=None):
                if isinstance(content, str) and content.strip():
                    yield content
        except GeneratorExit:
            # Consumer closed the generator; stop cleanly
            raise
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield "I apologize, but I encountered an error. Please try again."

    def response_with_functions(
        self,
        session_id: str,
        dialogue: List[Dict],
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[Tuple[Optional[str], Optional[List]], None, None]:
        """
        Generate response with function calls.
        Yields (text_chunk, None) for text tokens,
        then (None, [function_calls]) if any were emitted,
        and finally (None, None) to signal completion.
        """
        try:
            tools = self._build_tools(functions)
            termination_sent = False
            for result in self._generate_stateless(dialogue, tools=tools):
                if isinstance(result, tuple):
                    yield result
                elif isinstance(result, str):
                    yield result, None
            # Normal completion: ensure a final termination signal
            yield None, None
            termination_sent = True
        except GeneratorExit:
            # Upstream closed; do not yield anything during close
            raise
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            try:
                yield f"I encountered an error: {str(e)}", None
                yield None, None
            except GeneratorExit:
                # If the consumer closed while we were reporting error, just stop
                raise

    def _generate_stateless(self, dialogue: List[Dict], tools):
        """
        Stateless generation:
        - Rebuilds system instruction on every call
        - Maps the entire dialogue into Vertex 'contents'
        - Calls model.generate_content with streaming
        """
        if not dialogue:
            if tools is None:
                return
            else:
                # No content; still indicate completion for tool flows
                yield None, None
                return

        # Extract system instruction if present
        system_instruction = None
        working_dialogue = dialogue
        if working_dialogue and working_dialogue[0].get("role") == "system":
            original_instruction = working_dialogue[0].get("content", "")
            system_instruction = f"""{emotional_prompt}

{FUNCTION_CALLING_PROMPT}

{original_instruction}"""
            working_dialogue = working_dialogue[1:]

        # No content to send
        if not working_dialogue:
            if tools is None:
                return
            else:
                yield None, None
                return

        # Build contents from the full dialogue provided by MCP
        try:
            contents: List[Content] = self._map_dialogue_to_contents(working_dialogue)
        except GeneratorExit:
            raise
        except Exception as e:
            log.bind(tag=TAG).error(f"Failed to map dialogue to contents: {e}")
            if tools is None:
                yield "I'm having technical difficulties. Please try again."
            else:
                yield "Technical issues occurred.", None
                yield None, None
            return

        model = GenerativeModel(self.model_name, system_instruction=system_instruction)

        stream = None
        try:
            stream = model.generate_content(
                contents=contents,
                generation_config=self.gen_cfg,
                tools=tools,
                stream=True,
            )
            yield from self._process_stream(stream, tools)
        except GeneratorExit:
            # Consumer closed; ensure stream is closed, then re-raise
            self._cancel_stream(stream)
            raise
        except Exception as e:
            log.bind(tag=TAG).error(f"Error calling Vertex AI: {e}")
            if tools is None:
                yield "I'm having technical difficulties. Please try again."
            else:
                yield "Technical issues occurred.", None
                yield None, None
        finally:
            # Best-effort cleanup; DO NOT yield here
            self._cancel_stream(stream)

    def _cancel_stream(self, stream):
        """Attempt to close/cancel the Vertex stream safely."""
        if stream is None:
            return
        try:
            # Some SDKs expose close(); others may have cancel()
            if hasattr(stream, "close") and callable(getattr(stream, "close")):
                stream.close()
            elif hasattr(stream, "cancel") and callable(getattr(stream, "cancel")):
                stream.cancel()
        except Exception:
            pass

    def _map_dialogue_to_contents(self, dialogue: List[Dict]) -> List[Content]:
        """
        Map MCP-style dialogue to VertexAI Content list.
        Supports:
        - role=user|assistant text messages
        - assistant tool_calls (function_call)
        - tool/function responses (role='tool')
        """
        role_map = {"assistant": "model", "user": "user"}
        contents: List[Content] = []

        for m in dialogue:
            r = m.get("role")
            # Assistant function call(s)
            if r == "assistant" and "tool_calls" in m and m["tool_calls"]:
                for tc in m["tool_calls"]:
                    try:
                        args = tc["function"].get("arguments")
                        if isinstance(args, str):
                            args_dict = json.loads(args) if args.strip() else {}
                        elif isinstance(args, dict):
                            args_dict = args
                        else:
                            args_dict = {}
                        contents.append(Content(
                            role="model",
                            parts=[Part.from_dict({
                                "function_call": {
                                    "name": tc["function"]["name"],
                                    "args": args_dict
                                }
                            })]
                        ))
                    except Exception as e:
                        log.bind(tag=TAG).debug(f"Error mapping assistant tool_call: {e}")
                continue

            # Tool/function response
            if r == "tool":
                try:
                    contents.append(Content(
                        role="function",
                        parts=[Part.from_dict({
                            "function_response": {
                                "name": m.get("name", "unknown"),
                                "response": {"content": str(m.get("content", ""))}
                            }
                        })]
                    ))
                except Exception as e:
                    log.bind(tag=TAG).debug(f"Error mapping tool response: {e}")
                continue

            # Regular user/assistant text
            mapped_role = role_map.get(r)
            if mapped_role:
                text = str(m.get("content", "")).strip()
                if text:
                    contents.append(Content(role=mapped_role, parts=[Part.from_text(text)]))

        return contents

    def _process_stream(self, stream, tools) -> Generator:
        """
        Process Vertex streaming responses.
        - Emits text chunks as str (tools is None) or (text, None) if tools are used
        - Collects function calls and emits them once at the end as (None, [calls])
        - Emits a final (None, None) only on normal completion when tools are used
        """
        function_calls_found = []
        normal_completion = False

        try:
            for chunk in stream:
                if not getattr(chunk, "candidates", None):
                    continue
                candidate = chunk.candidates[0]
                if not getattr(candidate, "content", None) or not candidate.content.parts:
                    continue

                for part in candidate.content.parts:
                    fc = getattr(part, "function_call", None)
                    if fc:
                        try:
                            args = dict(getattr(fc, "args", {}) or {})
                        except Exception:
                            args = {}
                        function_calls_found.append(SimpleNamespace(
                            id=uuid.uuid4().hex,
                            type="function",
                            function=SimpleNamespace(
                                name=getattr(fc, "name", ""),
                                arguments=json.dumps(args, ensure_ascii=False),
                            ),
                        ))
                        continue

                    text = getattr(part, "text", None)
                    if text:
                        text_content = text.strip()
                        if not text_content:
                            continue
                        if tools is None:
                            yield text_content
                        else:
                            yield text_content, None

            # Normal end of stream
            normal_completion = True

            if tools is not None and function_calls_found:
                yield None, function_calls_found

            if tools is not None:
                yield None, None

        except GeneratorExit:
            # Consumer closed; do not yield, just stop
            raise
        except Exception as e:
            log.bind(tag=TAG).error(f"Error processing stream: {e}")
            if tools is None:
                try:
                    yield "Processing error."
                except GeneratorExit:
                    raise
            else:
                try:
                    yield "Processing error.", None
                    yield None, None
                except GeneratorExit:
                    raise
        finally:
            # No yields here; just cleanup if needed (handled upstream)
            pass

    def cleanup_session(self, session_id: str):
        """
        Stateless provider: nothing to clean up.
        Kept for interface compatibility.
        """
        return