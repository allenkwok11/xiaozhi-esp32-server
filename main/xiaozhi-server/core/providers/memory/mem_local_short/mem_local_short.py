from ..base import MemoryProviderBase, logger
import time
import json
import os
import yaml
from config.config_loader import get_project_dir
from config.manage_api_client import save_mem_local_short


short_term_memory_prompt = """
# 时空记忆编织者

## 核心使命
构建可生长的动态记忆网络，在有限空间内保留关键信息的同时，智能维护信息演变轨迹
根据对话记录，总结user的重要信息，以便在未来的对话中提供更个性化的服务

## 记忆法则
### 1. 三维度记忆评估（每次更新必执行）
| 维度       | 评估标准                  | 权重分 |
|------------|---------------------------|--------|
| 时效性     | 信息新鲜度（按对话轮次） | 40%    |
| 情感强度   | 含💖标记/重复提及次数     | 35%    |
| 关联密度   | 与其他信息的连接数量      | 25%    |

### 2. 动态更新机制
**名字变更处理示例：**
原始记忆："曾用名": ["张三"], "现用名": "张三丰"
触发条件：当检测到「我叫X」「称呼我Y」等命名信号时
操作流程：
1. 将旧名移入"曾用名"列表
2. 记录命名时间轴："2024-02-15 14:32:启用张三丰"
3. 在记忆立方追加：「从张三到张三丰的身份蜕变」

### 3. 空间优化策略
- **信息压缩术**：用符号体系提升密度
  - ✅"张三丰[北/软工/🐱]"
  - ❌"北京软件工程师，养猫"
- **淘汰预警**：当总字数≥900时触发
  1. 删除权重分<60且3轮未提及的信息
  2. 合并相似条目（保留时间戳最近的）

## 记忆结构
输出格式必须为可解析的json字符串，不需要解释、注释和说明，保存记忆时仅从对话提取信息，不要混入示例内容
```json
{
  "时空档案": {
    "身份图谱": {
      "现用名": "",
      "特征标记": [] 
    },
    "记忆立方": [
      {
        "事件": "入职新公司",
        "时间戳": "2024-03-20",
        "情感值": 0.9,
        "关联项": ["下午茶"],
        "保鲜期": 30 
      }
    ]
  },
  "关系网络": {
    "高频话题": {"职场": 12},
    "暗线联系": [""]
  },
  "待响应": {
    "紧急事项": ["需立即处理的任务"], 
    "潜在关怀": ["可主动提供的帮助"]
  },
  "高光语录": [
    "最打动人心的瞬间，强烈的情感表达，user的原话"
  ]
}
```
"""

short_term_memory_prompt_only_content = """
你是一个经验丰富的记忆总结者，擅长将对话内容进行总结摘要，遵循以下规则：
1、总结user的重要信息，以便在未来的对话中提供更个性化的服务
2、不要重复总结，不要遗忘之前记忆，除非原来的记忆超过了1800字内，否则不要遗忘、不要压缩用户的历史记忆
3、用户操控的设备音量、播放音乐、天气、退出、不想对话等和用户本身无关的内容，这些信息不需要加入到总结中
4、不要把设备操控的成果结果和失败结果加入到总结中，也不要把用户的一些废话加入到总结中
5、不要为了总结而总结，如果用户的聊天没有意义，请返回原来的历史记录也是可以的
6、只需要返回总结摘要，严格控制在1800字内
7、不要包含代码、xml，不需要解释、注释和说明，保存记忆时仅从对话提取信息，不要混入示例内容
"""


def extract_json_data(json_code):
    start = json_code.find("```json")
    # 从start开始找到下一个```结束
    end = json_code.find("```", start + 1)
    # print("start:", start, "end:", end)
    if start == -1 or end == -1:
        try:
            jsonData = json.loads(json_code)
            return json_code
        except Exception as e:
            print("Error:", e)
        return ""
    jsonData = json_code[start + 7 : end]
    return jsonData


TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory):
        super().__init__(config)
        self.short_memory = ""
        self.long_memory = {"entities": [], "relations": []}  # Enhanced with long-term memory storage
        self.save_to_file = True
        self.memory_path = get_project_dir() + "data/.memory.yaml"
        self.load_memory(summary_memory)

    def init_memory(
        self, role_id, llm, summary_memory=None, save_to_file=True, **kwargs
    ):
        super().init_memory(role_id, llm, **kwargs)
        self.save_to_file = save_to_file
        self.load_memory(summary_memory)

    def load_memory(self, summary_memory):
        # Return directly after getting summary memory from API
        if summary_memory or not self.save_to_file:
            self.short_memory = summary_memory
            return

        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        if self.role_id in all_memory:
            mem = all_memory[self.role_id]
            # Compatible with old format and new format
            if isinstance(mem, str):
                self.short_memory = mem
            else:
                self.short_memory = mem.get("short_term", "")
                self.long_memory = mem.get("long_term", {"entities": [], "relations": []})

    def save_memory_to_file(self):
        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        # Save both short-term and long-term memory
        all_memory[self.role_id] = {
            "short_term": self.short_memory,
            "long_term": self.long_memory
        }
        with open(self.memory_path, "w", encoding="utf-8") as f:
            yaml.dump(all_memory, f, allow_unicode=True)

    def extract_observations_from_text(self, text):
        """Extract entities and relations from text"""
        lines = text.strip().split("\n")
        entities = []
        relations = []
        now = time.strftime("%Y-%m-%d")

        for line in lines:
            # English and Chinese name extraction
            if ("my name is" in line.lower() or "i am" in line.lower() or 
                "我叫" in line or "我的名字" in line or "我是" in line):
                name = ""
                if "my name is" in line.lower():
                    name = line.lower().split("my name is")[-1].strip().replace(".", "")
                elif "i am" in line.lower():
                    name = line.lower().split("i am")[-1].strip().replace(".", "")

                # Only add if name is not empty and has meaningful content
                if name and len(name.strip()) > 1:
                    # Clean up the name - remove common prefixes
                    name = name.replace("user:", "").replace("用户:", "").strip()
                    # Remove articles and common words
                    name = name.replace("the ", "").replace("a ", "").replace("an ", "").strip()
                    if name and len(name.strip()) > 1:
                        entities.append({"name": name, "entityType": "person", "observations": [f"named on {now}"], "score": 80, "last_updated": now})
            elif ("like" in line.lower() or "喜欢" in line) and ("user:" in line.lower() or "用户:" in line):
                # Extract what the user likes
                liked_item = ""
                if "like" in line.lower():
                    # Extract content after "like"
                    parts = line.lower().split("like")
                    if len(parts) > 1:
                        liked_item = parts[-1].strip().replace(".", "").replace("ing", "")
                        # Remove "User:" prefix if present
                        liked_item = liked_item.replace("user:", "").strip()
                        # Remove common articles
                        liked_item = liked_item.replace("to ", "").replace("the ", "").replace("a ", "").replace("an ", "").strip()

                if liked_item and len(liked_item.strip()) > 1:
                    entities.append({"name": liked_item, "entityType": "interest", "observations": [f"user likes {liked_item}"], "score": 75, "last_updated": now})
                    relations.append({"from": "user", "to": liked_item, "relationType": "likes"})
            elif "live in" in line.lower() or "住在" in line or "居住" in line:
                location = ""
                if "live in" in line.lower():
                    location = line.lower().split("live in")[-1].strip().replace(".", "")
                elif "住在" in line:
                    location = line.split("住在")[-1].strip().replace("。", "")
                elif "居住" in line:
                    location = line.split("居住")[-1].strip().replace("在", "").replace("。", "")
                
                if location and len(location.strip()) > 1:
                    # Clean up location - remove common prefixes
                    location = location.replace("user:", "").replace("用户:", "").strip()
                    location = location.replace("the ", "").replace("a ", "").replace("in ", "").strip()
                    if location and len(location.strip()) > 1:
                        entities.append({"name": location, "entityType": "location", "observations": [], "score": 60, "last_updated": now})
                        relations.append({"from": "user", "to": location, "relationType": "lives_in"})
            elif "work" in line.lower() or "工作" in line or "职业" in line:
                job = ""
                if "work" in line.lower():
                    job = line.lower().split("work")[-1].strip().replace(".", "")
                elif "工作" in line:
                    job = line.split("工作")[-1].strip().replace("是", "").replace("。", "")
                elif "职业" in line:
                    job = line.split("职业")[-1].strip().replace("是", "").replace("。", "")
                
                if job and len(job.strip()) > 1:
                    # Clean up job title - remove common prefixes
                    job = job.replace("user:", "").replace("用户:", "").strip()
                    job = job.replace("as a ", "").replace("as an ", "").replace("a ", "").replace("an ", "").strip()
                    if job and len(job.strip()) > 1:
                        entities.append({"name": job, "entityType": "job", "observations": [], "score": 70, "last_updated": now})
                        relations.append({"from": "user", "to": job, "relationType": "works_as"})
        return {"entities": entities, "relations": relations}

    def trim_long_memory(self, max_entities=100):
        """Clean up stale long-term memories"""
        today = time.strftime("%Y-%m-%d")
        def is_stale(entity):
            try:
                last = time.strptime(entity.get("last_updated", "1970-01-01"), "%Y-%m-%d")
                age = (time.mktime(time.strptime(today, "%Y-%m-%d")) - time.mktime(last)) / 86400
                return entity.get("score", 50) < 60 and age > 60
            except:
                return False
        self.long_memory["entities"] = [e for e in self.long_memory["entities"] if not is_stale(e)]

    def delete_memory_by_semantic(self, text: str):
        """Delete memory based on semantic content"""
        deleted = []
        if "forget" in text.lower() or "delete" in text.lower() or "remove" in text.lower():
            for e in list(self.long_memory["entities"]):
                if e["name"].lower() in text.lower():
                    self.long_memory["entities"].remove(e)
                    deleted.append(f"Entity {e['name']} deleted")
                else:
                    matched_obs = [obs for obs in e.get("observations", []) if any(key.lower() in text.lower() for key in obs.split())]
                    if matched_obs:
                        for obs in matched_obs:
                            e["observations"].remove(obs)
                        e["score"] -= 10
                        e["last_updated"] = time.strftime("%Y-%m-%d")
                        deleted.append(f"Entity {e['name']} observations deleted: {matched_obs}")
            
            # Save changes to file if any deletions were made
            if deleted and self.save_to_file:
                self.save_memory_to_file()
        
        return deleted

    def query_long_memory(self, keyword: str):
        """Query long-term memory"""
        matches = []
        keyword_lower = keyword.lower()
        for e in self.long_memory["entities"]:
            if keyword_lower in e["name"].lower() or any(keyword_lower in obs.lower() for obs in e.get("observations", [])):
                matches.append(e)
        for r in self.long_memory["relations"]:
            if keyword_lower in r["from"].lower() or keyword_lower in r["to"].lower() or keyword_lower in r["relationType"].lower():
                matches.append(r)
        return matches

    async def save_memory(self, msgs):
        # Print model information being used
        model_info = getattr(self.llm, "model_name", str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).debug(f"Using memory saving model: {model_info}")
        if self.llm is None:
            logger.bind(tag=TAG).error("LLM is not set for memory provider")
            return None

        if len(msgs) < 2:
            return None

        msgStr = ""
        for msg in msgs:
            if msg.role == "user":
                msgStr += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                msgStr += f"Assistant: {msg.content}\n"
        if self.short_memory and len(self.short_memory) > 0:
            msgStr += "历史记忆：\n"
            msgStr += self.short_memory

        # Current time
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msgStr += f"当前时间：{time_str}"

        if self.save_to_file:
            result = self.llm.response_no_stream(
                short_term_memory_prompt,
                msgStr,
                max_tokens=2000,
                temperature=0.2,
            )
            json_str = extract_json_data(result)
            try:
                json.loads(json_str)  # Check if JSON format is correct
                self.short_memory = json_str
                
                # Extract long-term memory
                graph_data = self.extract_observations_from_text(msgStr)
                if graph_data["entities"] or graph_data["relations"]:
                    existing_entity_names = {e["name"] for e in self.long_memory["entities"]}
                    for entity in graph_data["entities"]:
                        if entity["name"] not in existing_entity_names:
                            self.long_memory["entities"].append(entity)

                    for rel in graph_data["relations"]:
                        if rel not in self.long_memory["relations"]:
                            self.long_memory["relations"].append(rel)
                
                self.trim_long_memory()
                self.save_memory_to_file()
            except Exception as e:
                print("Error:", e)
        else:
            result = self.llm.response_no_stream(
                short_term_memory_prompt_only_content,
                msgStr,
                max_tokens=2000,
                temperature=0.2,
            )
            save_mem_local_short(self.role_id, result)
        logger.bind(tag=TAG).info(f"Save memory successful - Role: {self.role_id}")

        return self.short_memory

    async def query_memory(self, query: str) -> str:
        return self.short_memory
