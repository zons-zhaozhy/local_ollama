# 本地大模型 API 服务

本项目旨在为本地运行的 Ollama 大模型提供一个简洁而强大的 Web API 服务。它结合了 FastAPI 的高性能后端和简洁的前端界面，为用户提供了一个易于使用的大模型交互平台。

## 架构概览

1. **后端服务**：使用 Python 的 FastAPI 框架，提供高性能的异步 API 服务。
2. **大模型接口**：通过 Ollama 的 HTTP API 与本地运行的大语言模型进行交互。
3. **前端界面**：使用原生 HTML、CSS 和 JavaScript 构建的简洁用户界面，支持实时交互。

## 主要组件

### 1. FastAPI 后端

- 提供 RESTful API endpoints，处理前端请求。
- 实现与 Ollama 的异步通信，支持流式响应。
- 使用 CORS 中间件，确保跨域请求的安全处理。
- 集成日志系统，便于调试和监控。

### 2. Ollama 接口

- 封装 Ollama HTTP API 的调用，支持多种模型。
- 处理不同模型的参数配置和响应格式。
- 支持流式输出，提高响应速度和用户体验。

### 3. 前端界面

- 提供直观的用户界面，支持模型选择和问题输入。
- 实现动态加载可用模型列表。
- 使用 Fetch API 处理异步请求和流式响应。
- 响应式设计，适配不同设备屏幕。

## API 端点

- `/generate`: POST 请求，发送提示并获取模型响应。
- `/tags`: GET 请求，获取可用模型列表。

## 技术栈

- **后端**：Python 3.8+, FastAPI, Uvicorn, Requests
- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **大模型**：Ollama (支持多种开源大语言模型)

## 部署步骤

1. 安装依赖：
   ```
   pip install fastapi uvicorn requests
   ```

2. 确保 Ollama 服务已在本地运行。

3. 启动 FastAPI 服务：
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. 访问前端界面：打开浏览器，访问 `http://localhost:8000/static/index.html`。

5. API 文档：访问 `http://localhost:8000/docs` 查看交互式 API 文档。

## 新特性：Whisper 语音识别

本项目现已集成 OpenAI 的 Whisper 模型用于语音识别。Whisper 是一个强大的多语言语音识别模型，特别适合中文等多种语言的识别任务。

### Whisper 集成说明

1. **安装依赖**：
   在安装其他依赖的同时，请确保安装 Whisper：
   ```bash
   pip install openai-whisper
   ```

2. **使用方法**：
   语音识别功能的使用方法与之前相同。在前端界面中，点击"按住说话"按钮进行录音，录音结束后会自动发送到服务器进行识别。

3. **性能考虑**：
   - Whisper 模型会在服务器启动时加载，这可能会略微增加启动时间。
   - 首次语音识别请求可能会稍慢，因为模型需要预热。
   - 后续请求将会更快，因为模型已经加载到内存中。

4. **注意事项**：
   - Whisper 模型需要一定的计算资源。确保您的服务器有足够的 CPU 或 GPU 能力。
   - 默认使用 "base" 模型，可以在 `main.py` 中修改为其他模型大小（如 "tiny", "small", "medium", "large"）以平衡性能和准确性。

## 启动和运行

### 服务端启动

1. 确保您已安装所有必要的依赖：
   ```
   pip install fastapi uvicorn requests
   ```

2. 确保 Ollama 服务已在本地运行，端口为 11444。

3. 在项目根目录下，使用以下命令启动 FastAPI 服务：
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

### 客户端访问

1. **Web 界面访问**：
   - 打开您的网络浏览器
   - 访问 `http://10.22.11.110:8000/static/index.html`
   - 您应该能看到模型问答系统的用户界面

2. **API 直接访问**：
   - 使用 API 测试工具（如 Postman）或 curl 命令
   - 示例 curl 命令：
     ```
     curl -X POST "http://10.22.11.110:8000/generate" \
          -H "Content-Type: application/json" \
          -d '{"baseUrl":"http://10.22.11.110:11444/api/", "model":"llama2", "prompt":"Hello, how are you?"}'
     ```

3. **API 文档**：
   - 访问 `http://10.22.11.110:8000/docs` 查看交互式 API 文档
   - 在这里您可以直接测试 API 端点

4. **远程访问**：
   - 确保客户端设备与服务器在同一网络中
   - 使用服务器的 IP 地址（10.22.11.110）来访问系统
   - 例如：`http://10.22.11.110:8000/static/index.html`

### 注意事项

- 本服务使用 HTTPS 与客户端通信，但允许与 Ollama 服务器使用 HTTP 通信。
- 确保您的防火墙设置允许访问 443 端口（HTTPS）。
- Ollama 服务应该在本地网络中运行，通常使用 HTTP 协议。
- 在生产环境中，建议将 Ollama 服务置于安全的内部网络中。

## 配置说明

- **CORS 设置**：默认允许所有来源的请求。在生产环境中，建议限制允许的来源。
- **日志级别**：可在 `main.py` 中调整日志级别，默认为 INFO。
- **模型参数**：可以通过修改前端界面或后端代码来调整模型参数。

## 性能优化

- 使用异步请求处理大量并发连接。
- 实现流式响应，减少首次响应时间。
- 前端使用防抖技术，避免频繁请求。

## 安全考虑

- 实现请求速率限制，防止 API 滥用。
- 考虑添加身份验证机制，特别是在公开部署时。
- 定期更新依赖包，修复潜在的安全漏洞。

## 故障排除

- 检查 Ollama 服务是否正常运行。
- 验证 Base URL 设置是否正确。
- 查看服务器日志以获取详细错误信息。

## 未来改进

- 实现用户认证和授权系统。
- 添加更高级的请求队列管理机制。
- 集成监控和分析工具，提供详细的 API 使用统计。
- 支持更多自定义模型参数和高级配置选项。

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 联系方式

如有任何问题或建议，请通过 [项目 Issues](https://github.com/yourusername/your-repo-name/issues) 与我们联系。

## HTTPS 配置（使用自签名证书）

本项目使用自签名证书来启用 HTTPS。请按照以下步骤配置：

1. 安装必要的依赖：
   ```bash
   pip install cryptography
   ```

2. 运行证书生成脚本：
   ```bash
   python generate_cert.py
   ```

3. 确保 `cert.pem` 和 `key.pem` 文件与 `main.py` 在同一目录下。

4. 使用以下命令启动服务器：
   ```bash
   python main.py
   ```

5. 通过 https://localhost 或 https://your-ip-address 访问系统

注意：由于使用自签名证书，浏览器可能会显示安全警告。在开发环境中，您可以选择继续访问网站。在生产环境中，请使用受信任的 SSL 证书。

## 启动和运行

... (保留原有的启动说明，但更新访问 URL 为 HTTPS)
