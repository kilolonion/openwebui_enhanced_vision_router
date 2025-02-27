# Enhanced Cross-API Vision Router

[![English](https://img.shields.io/badge/Language-English-blue)](README.md) [![中文](https://img.shields.io/badge/语言-中文-red)](README_CN.md) ![Version](https://img.shields.io/badge/version-1.0.0-blue) ![OpenWebUI](https://img.shields.io/badge/OpenWebUI-%3E%3D0.5.0-green)

📦 **[Official Plugin Link](https://openwebui.com/f/kilon/enhanced_vision_router)**

A powerful OpenWebUI vision enhancement plugin that provides cross-API visual processing capabilities for non-vision models, solving compatibility issues when switching between models from different APIs.

## Quick Installation

1. Copy `enhanced_vision_router.py` to the OpenWebUI function addition interface or visit the [Official Plugin Link](https://openwebui.com/f/kilon/enhanced_vision_router) for quick import
2. Add the list of non-vision model IDs that need enhancement in the configuration
3. Choose your preferred vision model (default is `deepseek.vision`)

## How It Works

The plugin intercepts requests sent to non-vision models and:
- **Detects and extracts** images from user messages
- Uses the configured **vision model to generate detailed descriptions**
- **Replaces images with text descriptions**, allowing non-vision models to "see" images
- Handles **cross-API call format compatibility** to avoid type errors

## Real-World Usage Examples

### Cross-API Model Switching

Seamlessly switch between models from different API providers:

```
User: [Sends an image] What is this?
AI (DeepSeek.Chat): This is a city night scene photo, showing...

User: Switch to Mixtral model and continue analyzing this image
AI (Ollama.Mixtral): From the image, I can see that this is a modern city skyline at night...
```

### Special Image Type Processing

The plugin optimizes descriptions based on image type:

```
User: [Sends a screenshot containing text]
AI: This is a screenshot with the text content "...". The screenshot shows a web interface, containing...

User: [Sends a chart]
AI: This is a bar chart showing sales data from 2020-2023. The chart indicates that sales peaked in 2022, at...
```

## Configuration Options

The plugin offers rich configuration options:

```python
# Main configuration options
non_vision_model_ids = ["deepseek.chat", "ollama.mixtral", "anthropic.claude-3-haiku"]  # Non-vision models that need vision capabilities
vision_model_id = "deepseek.vision"  # Primary vision model
fallback_vision_model_id = "google.gemini-2.0-flash"  # Backup vision model
debug_mode = True  # Enable debug mode
status_updates = True  # Show processing status
```

### Custom Prompts and Templates

```python
# Custom image description prompt
image_description_prompt = """You are a professional image analysis description expert.
Your task: Provide detailed descriptions of images so that people without vision can understand and use them.
...
"""

# Custom image context template
image_context_template = "Below is a description of the image attached to the user's message. Please consider this as an image you can see. Only consider this image when relevant to the user's prompt.\n\nImage description: {description}"
```

## Features

<details>
<summary>Click to expand feature list</summary>

- **Cross-API Compatibility**: Resolves type errors when switching between models from different API providers
- **Intelligent Image Processing**: Automatically extracts and processes images from user messages
- **Multi-level Caching Mechanism**: Caches image descriptions to improve performance and reduce API calls
- **Error Recovery Mechanism**: Automatically switches to a backup vision model when the primary model fails
- **Detailed Status Feedback**: Provides real-time processing status and progress reports
- **Image Format Diversity**: Supports both base64 encoding and image URL methods
- **Session State Tracking**: Maintains session context to ensure consistency across API calls
- **Type-Safe Processing**: Uniformly handles message format differences between different APIs
- **Extensible Provider Mapping**: Easy to add support for new API providers
</details>

## Configuration Details

<details>
<summary>Click to expand configuration details</summary>

### Global Settings
- `non_vision_model_ids`: List of non-vision model IDs that need vision capabilities
- `vision_model_id`: Primary vision model used for processing images
- `fallback_vision_model_id`: Backup vision model, used when the primary model fails
- `providers_map`: API provider mapping, used to identify which API different models belong to
- `image_description_prompt`: Image description prompt sent to the vision model
- `image_context_template`: Text template for replacing images
- `debug_mode`: Debug mode switch, enables more logging when turned on
- `status_updates`: Whether to enable status update messages
- `max_retry_count`: Maximum retry count when vision model processing fails
- `max_cache_size`: Maximum number of entries for the image description cache
</details>

## Advanced Usage

<details>
<summary>Click to expand advanced usage</summary>

### API Provider Mapping

Add support for new API providers:

```python
providers_map = {
    "deepseek": "deepseek",
    "google": "google",
    "anthropic": "anthropic",
    "openai": "openai",
    "mixtral": "ollama",
    "llama": "ollama",
    "qwen": "qwen",
    "new_provider": "new_provider_api_type"
}
```

### Image Cache Management

Control caching behavior:

```python
max_cache_size = 500  # Maximum cache entries
```

A larger cache can reduce API calls but will consume more memory.

### Debug Mode

Enable detailed logging:

```python
debug_mode = True  # Enable debug mode
```

When enabled, the plugin outputs detailed processing logs, which is very useful for troubleshooting.
</details>

## Troubleshooting

<details>
<summary>Click to expand solutions for common issues</summary>

### Type Error Issues

If you encounter a `TypeError: expected string or bytes-like object, got 'list'` error:

1. Ensure you have configured the correct `providers_map` mapping relationships
2. Check that the non-vision model is correctly added to the configuration list

### Image Processing Failure

If image processing fails:

1. Confirm whether the vision model API is available
2. Try using the backup vision model `fallback_vision_model_id`
3. Check if the image format is supported

### Slow Processing

If image processing is slow:

1. Increase the cache size to reduce repeated processing
2. Check network connections and API response times
3. Consider using a vision model with faster response times

### Cross-Session Consistency

If you need to maintain image descriptions across sessions:

1. Consider implementing a persistent cache storage
2. Maintain image description caches at the user level
</details>

## Architecture Design

<details>
<summary>Click to expand architecture details</summary>

This plugin follows Clean Architecture and Domain-Driven Design principles:

- **Core Domain**: Core logic for image processing and message reconstruction
- **Application Layer**: Coordinates domain objects, handles requests and responses
- **Infrastructure Layer**: Interacts with OpenWebUI API, handles external dependencies
- **Interface Layer**: Receives and returns messages, handles format conversion

Plugin message flow:

1. Request Interception: Checks if the target model needs vision enhancement
2. Image Extraction: Extracts all images from user messages
3. Cache Check: Checks if the image already has a description cache
4. Vision Processing: Calls the vision model to generate descriptions for uncached images
5. Message Reconstruction: Replaces images with text descriptions
6. Format Adjustment: Ensures message format is applicable to the target API
7. Return Enhanced Request: Passes the processed request to the target model
</details>

## Contribution Guidelines

<details>
<summary>Click to expand contribution guidelines</summary>

Contributions are welcome! Feel free to submit Pull Requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Notes

- Ensure API compatibility is maintained
- Include corresponding documentation when adding new features
- Follow Clean Architecture principles
- Write clear commit messages
</details>


## Author

- **kilon** - [Email](mailto:a15607467772@163.com)

---

Built with ❤️ for the OpenWebUI community
