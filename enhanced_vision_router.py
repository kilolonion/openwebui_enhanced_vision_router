"""
title: Enhanced Cross-API Vision Router
author: kilon
email: a15607467772@163.com
date: 2024-05-11
version: 1.0.0
license: BSD-3-Clause
description: 提供增强的跨API视觉路由能力，解决不同API之间切换模型的兼容性问题，同时保留原Pseudo-Vision Router的所有功能。
"""

from pydantic import BaseModel, Field, validator
from typing import Callable, Awaitable, Any, Optional, List, Dict, Union
import hashlib
import json
import copy
import re
import logging
import time
import traceback

from open_webui.models.users import Users
from open_webui.utils.chat import generate_chat_completion
from fastapi import Request

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrossAPIVisionRouter")

class Filter:
    class Valves(BaseModel):
        non_vision_model_ids: List[str] = Field(
            default_factory=list,
            description="需要视觉能力的非视觉模型ID列表",
        )
        vision_model_id: str = Field(
            default="deepseek.vision", 
            description="用于处理图像的视觉模型标识符",
        )
        fallback_vision_model_id: str = Field(
            default="google.gemini-2.0-flash",
            description="备用视觉模型，当主视觉模型失败时使用",
        )
        providers_map: Dict[str, str] = Field(
            default_factory=lambda: {
                "deepseek": "deepseek",
                "google": "google",
                "anthropic": "anthropic",
                "openai": "openai",
                "mixtral": "ollama",
                "llama": "ollama",
                "qwen": "qwen"
            },
            description="API提供商映射，用于识别不同模型所属的API提供商",
        )
        image_description_prompt: str = Field(
            default=(
                """你是一个专业的图像分析描述专家。

你的任务：提供图像的详细描述，以便没有视觉的人也能理解和使用它们。

- 描述要全面准确，不限字数
- 根据图像内容调整描述风格：
  - 文本类图像（如书页）：
    - 准确转录文本内容
    - 添加视觉描述（如"这是一页看起来很旧的书")
  - 艺术类图像（如绘画）：
    - 提供创意或解释性描述
- 包含图像中的任何可见文本
- 描述图像中的人物（如适用）
- 适当使用Markdown和LaTeX格式
- 使用与图像内容相同的语言进行描述（如适用），否则使用中文
- 只提供描述，不要添加额外评论
- 请使结构清晰，便于阅读和理解
"""
            ),
            description="发送给视觉模型的图像描述提示",
        )
        image_context_template: str = Field(
            default="以下是用户消息中附带的图像描述。请将其视为您可以看到的图像。仅在与用户提示相关时才考虑此图像。\n\n图像描述: {description}",
            description="图像上下文模板，用于替换图像",
        )
        debug_mode: bool = Field(
            default=False, 
            description="调试模式开关，开启后会记录更多日志"
        )
        status_updates: bool = Field(
            default=True, 
            description="是否启用状态更新消息"
        )
        max_retry_count: int = Field(
            default=2,
            description="视觉模型处理失败时的最大重试次数"
        )
        max_cache_size: int = Field(
            default=500,
            description="图像描述缓存的最大条目数"
        )
        
        @validator('providers_map')
        def ensure_lowercase_keys(cls, v):
            """确保提供商映射的键是小写的"""
            return {k.lower(): v for k, v in v.items()}

    def __init__(self):
        self.valves = self.Valves()
        # 图像描述缓存
        self.image_description_cache: Dict[str, str] = {}
        # API状态缓存
        self.api_health_cache: Dict[str, Dict[str, Any]] = {}
        # 处理中的会话记录
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def get_api_provider(self, model_id: str) -> str:
        """
        根据模型ID识别API提供商
        """
        if not model_id:
            return "unknown"
            
        model_id_lower = model_id.lower()
        
        # 直接匹配完整提供商名称
        for provider, mapped_provider in self.valves.providers_map.items():
            if model_id_lower.startswith(provider):
                return mapped_provider
                
        # 部分匹配
        for provider, mapped_provider in self.valves.providers_map.items():
            if provider in model_id_lower:
                return mapped_provider
                
        return "unknown"

    def get_image_key(self, image_info: Dict[str, Any]) -> Optional[str]:
        """
        为图像生成唯一键值
        """
        try:
            if image_info.get("type") == "image_url":
                url = image_info.get("image_url")
                return str(url) if url else None
            elif image_info.get("type") == "image":
                image_data = image_info.get("image")
                if image_data is None:
                    return None

                # 处理不同的图像数据类型
                if isinstance(image_data, bytes):
                    data = image_data
                elif isinstance(image_data, str):
                    # 对于base64字符串
                    data = image_data.encode("utf-8")
                elif hasattr(image_data, "read"):
                    data = image_data.read()
                    if hasattr(image_data, "seek"):
                        image_data.seek(0)  # 重置文件指针
                else:
                    data = str(image_data).encode("utf-8")

                return hashlib.sha256(data).hexdigest()
            return None
        except Exception as e:
            logger.error(f"生成图像键时出错: {e}")
            if self.valves.debug_mode:
                logger.error(traceback.format_exc())
            return None

    def extract_images_from_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从消息中提取所有图像
        """
        images_found = []
        
        for idx_message, message in enumerate(messages):
            if message.get("role") != "user":
                continue
                
            content = message.get("content", "")
            
            # 处理列表类型的内容
            if isinstance(content, list):
                for idx_part, part in enumerate(content):
                    if part.get("type") == "image":
                        images_found.append({
                            "message_index": idx_message,
                            "content_index": idx_part,
                            "type": "image",
                            "image": part.get("image"),
                            "format": "base64"
                        })
                    elif part.get("type") == "image_url":
                        images_found.append({
                            "message_index": idx_message,
                            "content_index": idx_part,
                            "type": "image_url",
                            "image_url": part.get("image_url"),
                            "format": "url"
                        })
            
            # 处理独立图像数组
            if message.get("images"):
                for idx_img, img in enumerate(message.get("images", [])):
                    images_found.append({
                        "message_index": idx_message,
                        "image_index": idx_img,
                        "type": "image",
                        "image": img,
                        "format": "base64"
                    })
                    
        return images_found

    def is_content_list(self, content: Any) -> bool:
        """
        检查内容是否为列表类型，用于统一处理不同API的消息格式
        """
        return isinstance(content, list)

    def normalize_message_content(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化消息内容，确保内容始终为列表格式
        """
        content = message.get("content", "")
        
        # 复制消息，避免修改原始消息
        normalized_message = copy.deepcopy(message)
        
        # 字符串转换为列表格式
        if isinstance(content, str):
            normalized_message["content"] = [{"type": "text", "text": content}]
        elif not isinstance(content, list):
            # 其他非列表类型也转换为列表
            normalized_message["content"] = [{"type": "text", "text": str(content)}]
            
        return normalized_message

    def denormalize_message_content(self, message: Dict[str, Any], original_type: str) -> Dict[str, Any]:
        """
        将消息内容从标准化的列表格式恢复为原始格式
        """
        content = message.get("content", [])
        
        # 复制消息，避免修改原始消息
        denormalized_message = copy.deepcopy(message)
        
        # 如果原始类型是字符串，且当前是列表格式，则转回字符串
        if original_type == "string" and isinstance(content, list):
            text_parts = []
            for part in content:
                if part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            denormalized_message["content"] = " ".join(text_parts)
            
        return denormalized_message

    async def process_images_with_vision_model(
        self,
        images: List[Dict[str, Any]],
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[Dict[str, Any]],
        __request__: Optional[Request],
    ) -> Dict[str, str]:
        """
        使用视觉模型处理图像
        """
        results = {}
        cached_images = 0
        processed_images = 0
        
        # 检查缓存中已有的图像
        for image_info in images:
            image_key = self.get_image_key(image_info)
            if not image_key:
                continue
                
            if image_key in self.image_description_cache:
                results[image_key] = self.image_description_cache[image_key]
                cached_images += 1
            else:
                processed_images += 1
                
        # 发送初始状态消息
        if self.valves.status_updates and images:
            status_message = f"找到 {len(images)} 张图片"
            if cached_images > 0:
                status_message += f"（其中 {cached_images} 张从缓存加载）"
            if processed_images > 0:
                status_message += f", 正在使用 {self.valves.vision_model_id} 处理 {processed_images} 张新图片"
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": status_message,
                    "done": False
                }
            })
        
        # 处理未缓存的图像
        image_count = 0
        for image_info in images:
            image_key = self.get_image_key(image_info)
            if not image_key or image_key in results:
                continue
                
            image_count += 1
            
            # 尝试使用主视觉模型
            description = await self._process_single_image(
                image_info, 
                self.valves.vision_model_id,
                __event_emitter__,
                __user__,
                __request__,
                image_count,
                processed_images
            )
            
            # 如果主模型失败，尝试使用备用模型
            if not description and self.valves.vision_model_id != self.valves.fallback_vision_model_id:
                if self.valves.status_updates:
                    await __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": f"主视觉模型处理失败，尝试备用模型 {self.valves.fallback_vision_model_id}",
                            "done": False
                        }
                    })
                    
                description = await self._process_single_image(
                    image_info,
                    self.valves.fallback_vision_model_id,
                    __event_emitter__,
                    __user__,
                    __request__,
                    image_count,
                    processed_images
                )
            
            # 存储结果，即使是失败的结果也存储，避免重复尝试失败的图像
            if description:
                results[image_key] = description
                self.image_description_cache[image_key] = description
                
                # 如果缓存过大，移除最早的条目
                if len(self.image_description_cache) > self.valves.max_cache_size:
                    # 简单的LRU实现 - 删除第一个键
                    oldest_key = next(iter(self.image_description_cache))
                    self.image_description_cache.pop(oldest_key)
            else:
                # 使用默认描述
                default_desc = "图像处理失败，无法生成描述。"
                results[image_key] = default_desc
                
        # 发送最终状态消息
        if self.valves.status_updates and images:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": f"图像处理完成: 替换了 {len(images)} 张图片 ({cached_images} 张来自缓存)",
                    "done": True
                }
            })
            
        return results

    async def _process_single_image(
        self,
        image_info: Dict[str, Any],
        vision_model_id: str,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[Dict[str, Any]],
        __request__: Optional[Request],
        image_count: int,
        total_images: int
    ) -> Optional[str]:
        """
        处理单个图像
        """
        retry_count = 0
        max_retries = self.valves.max_retry_count
        
        while retry_count <= max_retries:
            try:
                # 准备图像部分
                if image_info.get("type") == "image_url" and image_info.get("image_url"):
                    image_part = {
                        "type": "image_url",
                        "image_url": image_info.get("image_url")
                    }
                elif image_info.get("type") == "image" and image_info.get("image"):
                    image_part = {
                        "type": "image",
                        "image": image_info.get("image")
                    }
                else:
                    if self.valves.debug_mode:
                        logger.warning(f"跳过无效图像数据: {image_info.get('type')}")
                    return None
                
                # 构建消息
                messages_to_vision_model = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.valves.image_description_prompt
                            },
                            image_part
                        ]
                    }
                ]
                
                # 准备请求
                payload = {
                    "model": vision_model_id,
                    "messages": messages_to_vision_model,
                    "stream": False
                }
                
                # 获取用户对象
                user_obj = Users.get_user_by_id(__user__["id"]) if __user__ and "id" in __user__ else None
                
                # 发送状态更新
                if self.valves.status_updates:
                    await __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": f"正在处理图像 {image_count}/{total_images}...",
                            "done": False
                        }
                    })
                
                # 调用API
                start_time = time.time()
                response = await generate_chat_completion(
                    request=__request__,
                    form_data=payload,
                    user=user_obj
                )
                elapsed_time = time.time() - start_time
                
                # 提取结果
                content = response["choices"][0]["message"]["content"]
                
                if content:
                    word_count = len(content.split())
                    
                    # 发送状态更新
                    if self.valves.status_updates:
                        await __event_emitter__({
                            "type": "status",
                            "data": {
                                "description": f"图像 {image_count} 处理完成: {word_count} 个描述词 ({elapsed_time:.2f}秒)",
                                "done": False
                            }
                        })
                    
                    return content
                else:
                    retry_count += 1
                    if retry_count <= max_retries:
                        # 发送重试状态
                        if self.valves.status_updates:
                            await __event_emitter__({
                                "type": "status",
                                "data": {
                                    "description": f"图像 {image_count} 处理未返回内容，重试 {retry_count}/{max_retries}",
                                    "done": False
                                }
                            })
                    else:
                        # 发送失败状态
                        if self.valves.status_updates:
                            await __event_emitter__({
                                "type": "status",
                                "data": {
                                    "description": f"图像 {image_count} 处理失败，无法生成描述",
                                    "done": False
                                }
                            })
                        return None
                        
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                if self.valves.debug_mode:
                    logger.error(f"处理图像 {image_count} 时出错: {error_msg}")
                    logger.error(traceback.format_exc())
                
                if retry_count <= max_retries:
                    # 发送重试状态
                    if self.valves.status_updates:
                        await __event_emitter__({
                            "type": "status",
                            "data": {
                                "description": f"图像 {image_count} 处理错误: {error_msg[:50]}..., 重试 {retry_count}/{max_retries}",
                                "done": False
                            }
                        })
                else:
                    # 发送失败状态
                    if self.valves.status_updates:
                        await __event_emitter__({
                            "type": "status",
                            "data": {
                                "description": f"图像 {image_count} 处理失败: {error_msg[:50]}...",
                                "done": False
                            }
                        })
                    return None
                    
        return None

    def reconstruct_messages(
        self, 
        messages: List[Dict[str, Any]], 
        image_descriptions: Dict[str, str],
        images_found: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        重构消息，将图像替换为描述文本
        """
        # 按消息索引分组图像
        images_by_message = {}
        for img in images_found:
            msg_idx = img["message_index"]
            if msg_idx not in images_by_message:
                images_by_message[msg_idx] = []
            images_by_message[msg_idx].append(img)
        
        # 复制消息列表，避免修改原始数据
        reconstructed_messages = copy.deepcopy(messages)
        
        # 处理每条消息
        for msg_idx, message in enumerate(reconstructed_messages):
            if msg_idx not in images_by_message or message.get("role") != "user":
                continue
            
            # 提取该消息中的所有图像
            imgs = sorted(images_by_message[msg_idx], 
                          key=lambda x: x.get("content_index", x.get("image_index", 0)))
            
            # 标准化消息内容为列表格式
            normalized_message = self.normalize_message_content(message)
            content_list = normalized_message.get("content", [])
            
            # 创建新的内容列表
            new_content = []
            
            # 添加图像描述
            for img_idx, img in enumerate(imgs):
                image_key = self.get_image_key(img)
                if not image_key or image_key not in image_descriptions:
                    continue
                
                description = image_descriptions[image_key]
                
                # 使用模板格式化描述
                context_text = self.valves.image_context_template.format(
                    description=description
                )
                
                # 添加到新内容
                new_content.append({"type": "text", "text": context_text})
            
            # 添加原始文本内容（过滤掉图像）
            for part in content_list:
                if part.get("type") in ["text", "code"]:
                    new_content.append(part)
            
            # 更新消息内容
            message["content"] = new_content
            
            # 删除独立图像数组
            if "images" in message:
                message.pop("images")
        
        return reconstructed_messages

    def get_content_format(self, messages: List[Dict[str, Any]]) -> Dict[int, str]:
        """
        检测每条消息的内容格式类型
        """
        format_map = {}
        
        for idx, message in enumerate(messages):
            content = message.get("content")
            if isinstance(content, str):
                format_map[idx] = "string"
            elif isinstance(content, list):
                format_map[idx] = "list"
            else:
                format_map[idx] = "other"
                
        return format_map

    async def inlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __request__: Optional[Request] = None,
    ) -> dict:
        """
        主入口函数，处理请求
        """
        try:
            # 检查是否需要处理
            if not __model__ or "id" not in __model__ or __model__["id"] not in self.valves.non_vision_model_ids:
                return body
            
            # 复制请求体，避免修改原始数据
            processed_body = copy.deepcopy(body)
            messages = processed_body.get("messages", [])
            
            # 生成会话ID
            session_id = hashlib.md5(json.dumps(processed_body).encode()).hexdigest()
            
            # 记录内容格式
            content_formats = self.get_content_format(messages)
            
            # 提取图像
            images_found = self.extract_images_from_messages(messages)
            
            if not images_found:
                return body  # 没有图像，无需处理
            
            # 处理图像
            image_descriptions = await self.process_images_with_vision_model(
                images_found,
                __event_emitter__,
                __user__,
                __request__
            )
            
            # 重构消息
            reconstructed_messages = self.reconstruct_messages(messages, image_descriptions, images_found)
            processed_body["messages"] = reconstructed_messages
            
            # 存储会话信息
            self.active_sessions[session_id] = {
                "model_id": __model__["id"],
                "api_provider": self.get_api_provider(__model__["id"]),
                "content_formats": content_formats,
                "timestamp": time.time()
            }
            
            return processed_body
            
        except Exception as e:
            error_msg = f"视觉路由器处理错误: {str(e)}"
            logger.error(error_msg)
            
            if self.valves.debug_mode:
                logger.error(traceback.format_exc())
                
            if self.valves.status_updates:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": error_msg,
                        "done": True
                    }
                })
                
            # 出错时返回原始请求
            return body