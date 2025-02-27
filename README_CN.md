# 增强记忆管理器

[![English](https://img.shields.io/badge/Language-English-blue)](README.md) [![中文](https://img.shields.io/badge/语言-中文-red)](README_CN.md) ![Version](https://img.shields.io/badge/version-2.0.0-blue) ![OpenWebUI](https://img.shields.io/badge/OpenWebUI-%3E%3D0.5.0-green)

📦 **[插件官方链接](https://openwebui.com/f/kilon/enhanced_auto_memory_manager)**

一个强大的OpenWebUI记忆管理插件，通过自动记忆和显式记忆功能增强对话上下文。

## 快速安装

1. 将`enhanced_memory_filter.py`复制到OpenWebUI函数添加界面或前往[插件官方链接](https://openwebui.com/f/kilon/enhanced_auto_memory_manager)快速导入
2. 在配置文件里填写好支持OpenAI的API密钥和API URL以及模型（亲测DeepSeek，Siliconflow，OpenAI，火山引擎可用）

## 工作原理

插件会监控你与AI的对话并：
- **自动提取**重要信息，无需用户操作
- 当你使用"记住这个"等短语时**识别显式记忆请求**
- 在未来对话中需要时**检索相关记忆**

## 实际使用示例

### 自动记忆
正常聊天即可 - 插件在后台默默工作：

```
用户：我住在北京，是一名软件工程师。
AI：了解了！我会记住你是一位居住在北京的软件工程师。
```

插件会自动存储这些信息以供将来参考。

### 显式记忆
当你想确保某事被记住时，使用触发词：

```
用户：记住我喜欢所有应用都使用深色模式。
AI：我已记录下你喜欢所有应用使用深色模式。

用户：别忘了我女儿的生日是5月15日。
AI：我已记下你女儿的生日是5月15日。
```

这些记忆会被赋予更高优先级，在未来对话中更容易被回忆起来。

## 配置选项

插件开箱即用，但你可以通过编辑`enhanced_memory_filter.py`进行自定义：

```python
# 全局设置示例（查找Valves类）
api_url = "https://api.deepseek.com/v1"  # 使用DeepSeek而非OpenAI
model = "deepseek-chat"  # 使用DeepSeek的模型
explicit_memory_keywords = ["记住", "别忘了", "牢记", "记得", "remember", "don't forget", "note that"]
```
或在配置里填写显示触发关键词

### 环境变量

插件也支持通过环境变量进行配置：
```bash
# 在启动OpenWebUI前设置在环境中
export DEEPSEEK_API_KEY="你的API密钥"
export DEEPSEEK_API_URL="https://api.deepseek.com/v1" 
```

## 功能特点

<details>
<summary>点击展开功能列表</summary>

- **自动记忆提取**：智能从对话中提取并存储重要信息
- **显式记忆识别**：通过关键词如"记住"、"别忘了"等识别显式记忆请求
- **优先级记忆存储**：基于重要性为记忆分配不同优先级
- **用户级配置**：允许按用户自定义记忆功能
- **上下文感知处理**：理解时间引用和上下文信息
- **高级记忆检索**：在对话中高效检索相关记忆
- **清晰架构设计**：基于Clean Architecture和领域驱动设计原则构建
</details>

## 配置详情

<details>
<summary>点击展开配置详情</summary>

### 全局设置
- `api_url`: OpenAI/DeepSeek API URL
- `api_key`: API密钥
- `model`: 用于记忆处理的模型
- `related_memories_n`: 检索相关记忆的数量
- `enabled`: 启用/禁用记忆过滤器
- `explicit_memory_keywords`: 触发显式记忆处理的关键词
- `explicit_memory_priority`: 显式记忆请求的优先级
- `show_memory_confirmation`: 是否显示记忆确认信息

### 用户设置
- `show_status`: 显示记忆处理状态
- `enable_auto_memory`: 启用自动记忆功能
- `enable_explicit_memory`: 启用显式记忆功能
</details>

## 架构设计

<details>
<summary>点击展开架构详情</summary>

此插件遵循Clean Architecture和领域驱动设计原则设计：

- **核心领域逻辑**：记忆操作和过滤逻辑与外部关注点隔离
- **应用层**：领域对象的协调和事务管理
- **基础设施层**：领域接口和外部服务的实现
- **接口层**：API接口和事件处理
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
</details>

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 作者

- **kilon** - [GitHub](https://github.com/kilolonion) - a15607467772@163.com

---

为OpenWebUI社区用❤️构建 