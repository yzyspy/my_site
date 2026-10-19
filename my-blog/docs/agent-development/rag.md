
### RAG
## 项目介绍
把知识库中的文档转换为向量表示，保存到向量数据库，当用户输入查询时，大模型根据知识库的内容进行问答

```golang
package main

import (
	"context"
	"fmt"
	"log"
	"trpc.group/trpc-go/trpc-agent-go/agent/llmagent"
	"trpc.group/trpc-go/trpc-agent-go/knowledge"
	openaiembedder "trpc.group/trpc-go/trpc-agent-go/knowledge/embedder/openai"
	//ollamaembedder "trpc.group/trpc-go/trpc-agent-go/knowledge/embedder/ollama"
	"trpc.group/trpc-go/trpc-agent-go/knowledge/source"
	dirsource "trpc.group/trpc-go/trpc-agent-go/knowledge/source/dir"
	filesource "trpc.group/trpc-go/trpc-agent-go/knowledge/source/file"
	knowledgetool "trpc.group/trpc-go/trpc-agent-go/knowledge/tool"
	vectorinmemory "trpc.group/trpc-go/trpc-agent-go/knowledge/vectorstore/inmemory"
	"trpc.group/trpc-go/trpc-agent-go/model"
	"trpc.group/trpc-go/trpc-agent-go/model/openai"
	"trpc.group/trpc-go/trpc-agent-go/runner"
	"trpc.group/trpc-go/trpc-agent-go/session/inmemory"
	"trpc.group/trpc-go/trpc-agent-go/tool"
	// 如需支持 PDF 文件，需手动引入 PDF reader（独立 go.mod，避免引入不必要的第三方依赖）
	_ "trpc.group/trpc-go/trpc-agent-go/knowledge/document/reader/pdf"
)

func main() {

	// 创建模型
	ctx := context.Background()

	//embedder := ollamaembedder.New(
	//	ollamaembedder.WithModel("nomic-embed-text"),
	//)
	
	embedder := openaiembedder.New(
		openaiembedder.WithModel("text-embedding-v4"),
		openaiembedder.WithAPIKey(""),
		openaiembedder.WithBaseURL("https://dashscope.aliyuncs.com/compatible-mode/v1"),
	)
	// 2. 创建内存向量存储
	vectorStore := vectorinmemory.New()

	// 3. 创建知识源，能自动检测文件的格式
	sources := []source.Source{
		filesource.New([]string{"./dir/hetong.pdf"}),
		dirsource.New([]string{"./dir"}),
	}

	// 4. 创建 Knowledge
	kb := knowledge.New(
		knowledge.WithEmbedder(embedder),
		knowledge.WithVectorStore(vectorStore),
		knowledge.WithSources(sources),
	)

	// 5. 加载文档
	if err := kb.Load(ctx); err != nil {
		log.Fatalf("Failed to load knowledge base: %v", err)
	}

	// 6. 创建搜索工具
	searchTool := knowledgetool.NewKnowledgeSearchTool(
		kb,
		knowledgetool.WithToolName("knowledge_search"),
		knowledgetool.WithToolDescription("Search for relevant information in the knowledge base."),
	)

	// 7. 创建 Agent 并添加工具
	modelInstance := openai.New(
		"deepseek-v4-pro",
		//openai.WithAPIKey(os.Getenv("AI_DEEPSEEK_API_KEY")),
		openai.WithAPIKey(""),
		openai.WithBaseURL("https://api.deepseek.com/v1"),
	)
	genConfig := model.GenerationConfig{
		Stream: true,
	}
	llmAgent := llmagent.New("assistant",
		llmagent.WithModel(modelInstance),
		llmagent.WithTools([]tool.Tool{searchTool}),
		llmagent.WithGenerationConfig(genConfig),
	)

	// 8. 创建 Runner 并执行
	sessionService := inmemory.NewSessionService()
	appRunner := runner.NewRunner("knowledge-chat", llmAgent, runner.WithSessionService(sessionService))

	//message := model.NewUserMessage("轻症有哪些是可以赔偿的")
	message := model.NewUserMessage("每年缴费多少钱")
	eventChan, err := appRunner.Run(ctx, "user123", "session456", message)
	if err != nil {
		log.Fatalf("Failed to run agent: %v", err)
	}
	for evt := range eventChan {
		if evt.Response == nil || len(evt.Response.Choices) == 0 {
			continue
		}
		if content := evt.Response.Choices[0].Message.Content; content != "" {
			fmt.Println(content)
		}
	}
}

```


go.mod
```
module webrtc-test

go 1.25.0

require (
	github.com/cloudwego/eino v0.9.3
	github.com/cloudwego/eino-ext/components/model/deepseek v0.1.6
	github.com/google/wire v0.7.0
	trpc.group/trpc-go/trpc-agent-go v1.10.0
	trpc.group/trpc-go/trpc-agent-go/knowledge/document/reader/pdf v1.10.0
	trpc.group/trpc-go/trpc-agent-go/knowledge/embedder/ollama v1.10.0
)

require (
	github.com/bahlo/generic-list-go v0.2.0 // indirect
	github.com/bmatcuk/doublestar/v4 v4.10.0 // indirect
	github.com/bufbuild/protocompile v0.14.1 // indirect
	github.com/buger/jsonparser v1.1.1 // indirect
	github.com/bytedance/gopkg v0.1.3 // indirect
	github.com/bytedance/sonic v1.15.0 // indirect
	github.com/bytedance/sonic/loader v0.5.0 // indirect
	github.com/cenkalti/backoff/v4 v4.3.0 // indirect
	github.com/cespare/xxhash/v2 v2.3.0 // indirect
	github.com/clipperhouse/uax29/v2 v2.2.0 // indirect
	github.com/cloudwego/base64x v0.1.6 // indirect
	github.com/cohesion-org/deepseek-go v1.3.4 // indirect
	github.com/creack/pty v1.1.24 // indirect
	github.com/dustin/go-humanize v1.0.1 // indirect
	github.com/eino-contrib/jsonschema v1.0.3 // indirect
	github.com/go-logr/logr v1.4.3 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/google/uuid v1.6.0 // indirect
	github.com/goph/emperror v0.17.2 // indirect
	github.com/grpc-ecosystem/grpc-gateway/v2 v2.22.0 // indirect
	github.com/hhrutter/lzw v1.0.0 // indirect
	github.com/hhrutter/pkcs7 v0.2.0 // indirect
	github.com/hhrutter/tiff v1.0.2 // indirect
	github.com/joho/godotenv v1.5.1 // indirect
	github.com/json-iterator/go v1.1.12 // indirect
	github.com/klauspost/cpuid/v2 v2.2.9 // indirect
	github.com/ledongthuc/pdf v0.0.0-20250511090121-5959a4027728 // indirect
	github.com/mailru/easyjson v0.9.0 // indirect
	github.com/mattn/go-runewidth v0.0.19 // indirect
	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/nikolalohinski/gonja v1.5.3 // indirect
	github.com/ollama/ollama v0.16.3 // indirect
	github.com/openai/openai-go v1.12.0 // indirect
	github.com/panjf2000/ants/v2 v2.10.0 // indirect
	github.com/pdfcpu/pdfcpu v0.11.1 // indirect
	github.com/pelletier/go-toml/v2 v2.2.2 // indirect
	github.com/pkg/errors v0.9.1 // indirect
	github.com/sirupsen/logrus v1.9.3 // indirect
	github.com/slongfield/pyfmt v0.0.0-20220222012616-ea85ff4c361f // indirect
	github.com/tidwall/gjson v1.14.4 // indirect
	github.com/tidwall/match v1.1.1 // indirect
	github.com/tidwall/pretty v1.2.1 // indirect
	github.com/tidwall/sjson v1.2.5 // indirect
	github.com/twitchyliquid64/golang-asm v0.15.1 // indirect
	github.com/wk8/go-ordered-map/v2 v2.1.8 // indirect
	github.com/yargevad/filepathx v1.0.0 // indirect
	github.com/yuin/goldmark v1.4.13 // indirect
	go.opentelemetry.io/auto/sdk v1.2.1 // indirect
	go.opentelemetry.io/otel v1.43.0 // indirect
	go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.29.0 // indirect
	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.29.0 // indirect
	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp v1.29.0 // indirect
	go.opentelemetry.io/otel/metric v1.43.0 // indirect
	go.opentelemetry.io/otel/sdk v1.43.0 // indirect
	go.opentelemetry.io/otel/trace v1.43.0 // indirect
	go.opentelemetry.io/proto/otlp v1.3.1 // indirect
	go.uber.org/multierr v1.10.0 // indirect
	go.uber.org/zap v1.27.0 // indirect
	golang.org/x/arch v0.11.0 // indirect
	golang.org/x/crypto v0.51.0 // indirect
	golang.org/x/exp v0.0.0-20250218142911-aa4b98e5adaa // indirect
	golang.org/x/image v0.32.0 // indirect
	golang.org/x/net v0.55.0 // indirect
	golang.org/x/sync v0.20.0 // indirect
	golang.org/x/sys v0.45.0 // indirect
	golang.org/x/text v0.37.0 // indirect
	google.golang.org/genproto/googleapis/api v0.0.0-20260720211330-0afa2a65878a // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20260720211330-0afa2a65878a // indirect
	google.golang.org/grpc v1.82.1 // indirect
	google.golang.org/protobuf v1.36.11 // indirect
	gopkg.in/yaml.v2 v2.4.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
	trpc.group/trpc-go/trpc-a2a-go v0.2.5 // indirect
)

```