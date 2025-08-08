# git_spider
一个基于github的智能搜索工具

```
## 搜索
python ./tools/Search_Repo.py -q "agentic" -o ./src/maual_update/Agentic.md
python ./tools/Search_Repo.py -q "mcp" -o ./src/maual_update/MCP.md
python ./tools/Search_Repo.py -q "rag" -o ./src/maual_update/RAG.md
python ./tools/Search_Repo.py -q "awesome rag" -o ./src/maual_update/awesome_rag.md
python ./tools/Search_Repo.py -q "awesome llm" -o ./src/maual_update/awesome_llm.md


## 更新
python ./tools/Search_Repo.py --update -o ./src/maual_update/awesome_llm.md
python ./tools/Search_Repo.py --update -o ./src/maual_update/Agentic.md
python ./tools/Search_Repo.py --update -o ./src/maual_update/MCP.md
python ./tools/Search_Repo.py --update -o ./src/maual_update/RAG.md
```