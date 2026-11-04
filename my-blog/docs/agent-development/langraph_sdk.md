---
title: 网页端调用 LangGraph 服务
date: '2026-09-24'
description: 使用 LangGraph JavaScript SDK 连接本地 Agent 服务，从依赖安装到 Vite 页面调试。
tags:
- LangGraph
- JavaScript
---

# 网页端调用 LangGraph 服务

mkdir langgraph-html-demo && cd langgraph-html-demo  
npm init -y  
npm install @langchain/langgraph-sdk @langchain/core  
npm install -D vite  

1. 启动langgraph服务  
   uv run langgraph dev  
2. 启动服务  
   npx vite


