# 增强跨API视觉路由器

[![English](https://img.shields.io/badge/Language-English-blue)](README.md) [![中文](https://img.shields.io/badge/语言-中文-red)](README_CN.md) ![Version](https://img.shields.io/badge/version-1.0.0-blue) ![OpenWebUI](https://img.shields.io/badge/OpenWebUI-%3E%3D0.5.0-green)

📦 **[插件官方链接](https://openwebui.com/f/kilon/enhanced_vision_router)**

一个强大的OpenWebUI视觉增强插件，为非视觉模型提供跨API的视觉处理能力，解决不同API之间切换模型的兼容性问题。

## 快速安装

1. 将`enhanced_vision_router.py`复制到OpenWebUI函数添加界面或前往[插件官方链接](https://openwebui.com/f/kilon/enhanced_vision_router)快速导入
2. 在配置中添加需要增强的非视觉模型ID列表
3. 选择你偏好的视觉模型（默认为`deepseek.vision`）

## 工作原理

插件会拦截发送到非视觉模型的请求并：
- **检测并提取**用户消息中的图像
- 使用配置的**视觉模型生成详细描述**
- 将图像**替换为文本描述**，使非视觉模型能"看见"图像
- 处理**跨API调用的格式兼容性**，避免类型错误

## 实际使用示例

### 跨API模型切换

无缝在不同API提供商的模型之间切换：

```
用户：[发送一张图片] 这是什么?
AI (DeepSeek.Chat)：这是一张城市夜景照片，展示了...

用户：切换到Mixtral模型继续分析这张图片
AI (Ollama.Mixtral)：从图片中可以看出，这是一座现代化城市的夜景...
```

### 特殊图像类型处理

插件会根据图像类型优化描述：

```
用户：[发送一张包含文本的截图]
AI：这是一张截图，上面的文本内容为"..."。截图显示了一个网页界面，包含...

用户：[发送一张图表]
AI：这是一张柱状图，展示了2020-2023年间的销售数据。图中显示销售额在2022年达到峰值，为...
```

## 配置选项

插件提供丰富的配置选项：

```python
# 主要配置选项
non_vision_model_ids = ["deepseek.chat", "ollama.mixtral", "anthropic.claude-3-haiku"]  # 需要视觉能力的非视觉模型
vision_model_id = "deepseek.vision"  # 主视觉模型
fallback_vision_model_id = "google.gemini-2.0-flash"  # 备用视觉模型
debug_mode = True  # 启用调试模式
status_updates = True  # 显示处理状态
```

### 自定义提示词和模板

```python
# 自定义图像描述提示词
image_description_prompt = """你是一个专业的图像分析描述专家。
你的任务：提供图像的详细描述，以便没有视觉的人也能理解和使用它们。
...
"""

# 自定义图像上下文模板
image_context_template = "以下是用户消息中附带的图像描述。请将其视为您可以看到的图像。仅在与用户提示相关时才考虑此图像。\n\n图像描述: {description}"
```

## 功能特点

<details>
<summary>点击展开功能列表</summary>

- **跨API兼容性**：解决不同API提供商之间切换模型的类型错误问题
- **智能图像处理**：自动提取和处理用户消息中的图像
- **多级缓存机制**：缓存图像描述，提高性能并减少API调用
- **错误恢复机制**：主模型失败时自动切换到备用视觉模型
- **详细状态反馈**：提供实时处理状态和进度报告
- **图像格式多样性**：支持base64编码和图像URL两种方式
- **会话状态追踪**：保持会话上下文，确保跨API调用的一致性
- **类型安全处理**：统一处理不同API的消息格式差异
- **可扩展提供商映射**：易于添加新的API提供商支持
</details>

## 配置详情

<details>
<summary>点击展开配置详情</summary>

### 全局设置
- `non_vision_model_ids`: 需要视觉能力的非视觉模型ID列表
- `vision_model_id`: 用于处理图像的主视觉模型
- `fallback_vision_model_id`: 备用视觉模型，当主模型失败时使用
- `providers_map`: API提供商映射，用于识别不同模型所属的API
- `image_description_prompt`: 发送给视觉模型的图像描述提示
- `image_context_template`: 替换图像的文本模板
- `debug_mode`: 调试模式开关，开启后会记录更多日志
- `status_updates`: 是否启用状态更新消息
- `max_retry_count`: 视觉模型处理失败时的最大重试次数
- `max_cache_size`: 图像描述缓存的最大条目数
</details>

## 高级用法

<details>
<summary>点击展开高级用法</summary>

### API提供商映射

为新的API提供商添加支持：

```python
providers_map = {
    "deepseek": "deepseek",
    "google": "google",
    "anthropic": "anthropic",
    "openai": "openai",
    "mixtral": "ollama",
    "llama": "ollama",
    "qwen": "qwen",
    "新提供商": "新提供商API类型"
}
```

### 图像缓存管理

控制缓存行为：

```python
max_cache_size = 500  # 最大缓存条目数
```

较大的缓存可以减少API调用，但会占用更多内存。

### 调试模式

启用详细日志记录：

```python
debug_mode = True  # 启用调试模式
```

启用后，插件会输出详细的处理日志，对故障排查非常有用。
</details>

## 错误排查

<details>
<summary>点击展开常见问题解决方案</summary>

### 类型错误问题

如果遇到 `TypeError: expected string or bytes-like object, got 'list'` 错误：

1. 确保已配置正确的 `providers_map` 映射关系
2. 检查非视觉模型是否正确添加到配置列表中

### 图像处理失败

如果图像处理失败：

1. 确认视觉模型API是否可用
2. 尝试使用备用视觉模型 `fallback_vision_model_id`
3. 检查图像格式是否受支持

### 处理缓慢

如果图像处理速度较慢：

1. 增加缓存大小以减少重复处理
2. 检查网络连接和API响应时间
3. 考虑使用响应更快的视觉模型

### 跨会话一致性

如果需要跨会话保持图像描述：

1. 考虑实现持久化缓存存储
2. 在用户级别维护图像描述缓存
</details>

## 架构设计

<details>
<summary>点击展开架构详情</summary>

此插件遵循Clean Architecture和领域驱动设计原则：

- **核心领域**：图像处理和消息重构的核心逻辑
- **应用层**：协调领域对象，处理请求和响应
- **基础设施层**：与OpenWebUI API交互，处理外部依赖
- **接口层**：接收和返回消息，处理格式转换

插件的消息流程：

1. 请求拦截：检查目标模型是否需要视觉增强
2. 图像提取：从用户消息中提取所有图像
3. 缓存检查：检查图像是否已有描述缓存
4. 视觉处理：对未缓存的图像调用视觉模型生成描述
5. 消息重构：将图像替换为文本描述
6. 格式调整：确保消息格式适用于目标API
7. 返回增强的请求：将处理后的请求传递给目标模型
</details>

## 贡献指南

<details>
<summary>点击展开贡献指南</summary>

欢迎贡献！请随时提交Pull Request。

1. Fork仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

### 开发注意事项

- 确保保持API兼容性
- 添加新功能时包含相应的文档
- 遵循Clean Architecture原则
- 编写清晰的提交信息
</details>

## 许可证

本项目采用BSD-3-Clause许可证 - 详情请参阅LICENSE文件。

## 作者

- **kilon** - [Email](mailto:a15607467772@163.com)

---

为OpenWebUI社区用❤️构建
