# core/providers/llm/gemini_sdk.py
import os, json, uuid
from types import SimpleNamespace
from typing import Any, Dict, List

from google import generativeai as genai
from google.generativeai import types, GenerationConfig

from core.providers.llm.base import LLMProviderBase
from core.utils.util import check_model_key
from config.logger import setup_logging
from google.generativeai.types import GenerateContentResponse

log = setup_logging()
TAG = __name__


class LLMProvider(LLMProviderBase):
    def __init__(self, cfg: Dict[str, Any]):
        self.model_name = cfg.get("model_name", "gemini-2.0-flash")
        self.api_key = cfg["api_key"]
        proxy = cfg.get("https_proxy") or cfg.get("http_proxy")

        if not check_model_key("LLM", self.api_key):
            raise ValueError("无效的Gemini API Key，请检查是否配置正确")

        if proxy:
            os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = proxy
            log.bind(tag=TAG).info(f"Gemini 代理地址: {proxy}")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

        self.gen_cfg = GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_output_tokens=2048,
        )


    @staticmethod
    def _build_tools(funcs: List[Dict[str, Any]] | None):
        if not funcs:
            return None
        return [types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=f["function"]["name"],
                description=f["function"]["description"],
                parameters=f["function"]["parameters"],
            )
            for f in funcs
        ])]

    # Gemini文档提到，无需维护session-id，直接用dialogue拼接而成
    def response(self, session_id, dialogue):
        yield from self._generate(dialogue, None)

    def response_with_functions(self, session_id, dialogue, functions=None):
        yield from self._generate(dialogue, self._build_tools(functions))

    def _generate(self, dialogue, tools):
        role_map = {"assistant": "model", "user": "user"}
        contents: list = []
        # 拼接对话
        for m in dialogue:
            r = m["role"]

            if r == "assistant" and "tool_calls" in m:
                tc = m["tool_calls"][0]
                contents.append({
                    "role": "model",
                    "parts": [{"function_call": {
                        "name": tc["function"]["name"],
                        "args": json.loads(tc["function"]["arguments"]),
                    }}],
                })
                continue

            if r == "tool":
                contents.append({
                    "role": "model",
                    "parts": [{"text": str(m.get("content", ""))}],
                })
                continue

            contents.append({
                "role": role_map.get(r, "user"),
                "parts": [{"text": str(m.get("content", ""))}],
            })

        stream: GenerateContentResponse = self.model.generate_content(
            contents=contents,
            generation_config=self.gen_cfg,
            tools=tools,
            stream=True,
        )

        try:
            for chunk in stream:
                cand = chunk.candidates[0]
                for part in cand.content.parts:
                    # a) 函数调用-通常是最后一段话才是函数调用
                    if getattr(part, "function_call", None):
                        fc = part.function_call
                        yield None, [SimpleNamespace(
                            id=uuid.uuid4().hex,
                            type="function",
                            function=SimpleNamespace(
                                name=fc.name,
                                arguments=json.dumps(dict(fc.args),
                                                     ensure_ascii=False),
                            ),
                        )]
                        return
                    # b) 普通文本
                    if getattr(part, "text", None):
                        yield part.text if tools is None else (part.text, None)

        finally:
            if tools is not None:
                yield None, None  # function‑mode 结束，返回哑包

    # 关闭stream，预留后续打断对话功能的功能方法，官方文档推荐打断对话要关闭上一个流，可以有效减少配额计费和资源占用
    @staticmethod
    def _safe_finish_stream(stream: GenerateContentResponse):
        if hasattr(stream, "resolve"):
            stream.resolve()  # Gemini SDK version ≥ 0.5.0
        elif hasattr(stream, "close"):
            stream.close()  # Gemini SDK version < 0.5.0
        else:
            for _ in stream:  # 兜底耗尽
                pass
