CRCopilot 是一个基于 LLM 大语言模型且完全免费的 Code Review 系统。

基于 Docker 部署。

### 配置 python 环境
```shell
conda create --name crcopilot python=3.10
conda activate crcopilot
```

### 安装依赖
```shell
pip install -r requirements.txt
```

## 使用 Docker 启动必要服务
包括：

向量数据库 Qdrant http://localhost:6333

Git服务 Gitea http://localhost:3000

关系型数据库 MySQL
```shell
docker-compose up -d
```

### git服务
http://localhost:3000/
![WebUI](docs/images/gitea.png)


### WebUI
![WebUI](docs/images/web-demo.gif)
可以通过以下命令启动基于 Gradio 的网页版 demo：
```shell
python web_demo.py
```

### 命令行
![api_cli_access](docs/images/api_cli_access.png)

运行仓库中 [api_cli_access.py](api_cli_access.py)：

```shell
# 启动本地大模型服务
python api_cli.py
# 命令行交互
python api_cli_access.py
```

程序会在命令行中进行交互式的对话，在命令行中输入指示并回车即可生成回复


### API 部署
首先需要安装额外的依赖 `pip install fastapi uvicorn`，然后运行仓库中的 [api.py](api.py)：
```shell
python api.py
```
默认部署在本地的 8000 端口，通过 POST 方法进行调用
```shell
curl -X POST "http://127.0.0.1:8000" \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "你好", "history": []}'
```
得到的返回值为
```shell
{
  "response":"你好👋！我是人工智能助手 ChatGLM2-6B，很高兴见到你，欢迎问我任何问题。",
  "history":[["你好","你好👋！我是人工智能助手 ChatGLM2-6B，很高兴见到你，欢迎问我任何问题。"]],
  "status":200,
  "time":"2023-03-23 21:38:40"
}
```


### 知识库
| 内容 | 数据源 |
| ------------- | ------------- |
| React 官方文档 | [https://react.dev/learn](https://github.com/reactjs/react.dev/tree/main/src/content/learn)  |
| Zustand 官方文档  | [https://docs.pmnd.rs/zustand/](https://github.com/pmndrs/zustand/tree/main/docs)  |

