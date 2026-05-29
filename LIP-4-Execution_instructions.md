## **HDFC Mutual Fund Facts-Only FAQ Assistant** 

## **Execution & Implementation Guide (Groq + Llama 3.3 70B)** 

## **Project Objective** 

Build a Retrieval-Augmented Generation (RAG) based FAQ assistant that answers factual questions about selected HDFC Mutual Fund schemes using only approved public sources. 

The system must: 

- Use only official HDFC Mutual Fund, AMFI, and SEBI resources. 

- Provide factual answers only. 

- Include source attribution with every response. 

- Refuse investment advice and recommendations. 

- Persist embeddings locally for fast subsequent startups. 

- Use Groq-hosted Llama 3.3 70B as the inference model. 

- 

## **Scope** 

## **Supported Funds** 

- HDFC Top 100 Fund 

- HDFC Flexi Cap Fund 

- HDFC ELSS Tax Saver Fund 

- HDFC Balanced Advantage Fund 

## **Approved Source Categories** 

## **Scheme Information** 

- Official Scheme Pages 

- Monthly Factsheets 

- Scheme Information Documents (SID) 

- Key Information Memorandum (KIM) 

## **Regulatory Sources** 

- SEBI Mutual Fund FAQs 

- AMFI Educational Resources 

## **Investor Services** 

- Account Statements 

1 

- Capital Gains Statements 

- Tax Documents 

- Forms & Downloads 

## **Fund Information** 

- Expense Ratios 

- Exit Load Structure 

- SIP Information 

- Riskometer Details 

## **Technology Stack** 

## **Frontend** 

- Streamlit 

## **LLM** 

- Groq API • Llama 3.3 70B Versatile 

## **Framework** 

- LangChain 

## **Embeddings** 

- all-MiniLM-L6-v2 

## **Vector Store** 

- ChromaDB 

## **Data Sources** 

- Official Web Pages 

- Official PDFs 

## **Project Structure** 

```
hdfc-mf-faq/
│
├── app.py
```

- `├── rag_assistant.py` 

2 

```
├── source_list.py
├── requirements.txt
├── README.md
├── sample_qa.md
├── source_list.csv
├── .env
├── .gitignore
│
└── chroma_db/
```

## **Phase 1 — Environment Setup** 

## **Create Project** 

```
mkdirhdfc-mf-faq
cdhdfc-mf-faq
```

## **Create Files** 

```
app.py
rag_assistant.py
source_list.py
requirements.txt
README.md
sample_qa.md
.env
.gitignore
```

## **requirements.txt** 

```
streamlit
langchain
langchain-community
langchain-groq
chromadb
sentence-transformers
pypdf
python-dotenv
beautifulsoup4
```

## **Environment Variables** 

Create `.env` 

3 

```
GROQ_API_KEY=gsk_your_groq_api_key
```

## **Install Dependencies** 

```
pipinstall-rrequirements.txt
```

## **Phase 2 — Source Registry** 

Create `source_list.py` . 

Maintain a single source registry: 

```
SOURCE_LIST=[
(url,"web"),
(url,"pdf")
]
```

All retrieval operations must originate from this registry. 

No additional sources should be introduced. 

## **Phase 3 — Document Ingestion** 

Implement: 

```
load_and_split_documents()
```

## **Loading Strategy** 

## **Web Pages** 

Use: 

```
WebBaseLoader
```

## **PDFs** 

Use: 

4 

```
PyPDFLoader
```

## **Metadata** 

Attach source URLs: 

```
document.metadata["source"]
```

## **Chunking Configuration** 

```
RecursiveCharacterTextSplitter(
chunk_size=1000,
chunk_overlap=200
)
```

## **Error Handling** 

Requirements: 

- Skip failed URLs 

- Log errors 

- Continue processing 

Indexing should never stop because of a single broken source. 

## **Phase 4 — Embeddings & Vector Store** 

## **Embedding Model** 

```
all-MiniLM-L6-v2
```

Use: 

```
HuggingFaceEmbeddings
```

## **Chroma Persistence** 

Persist vector store to: 

5 

```
./chroma_db
```

## **Required Functions** 

```
create_vectorstore(chunks)
```

```
get_retriever()
```

## **Behavior** 

If Chroma exists: 

- Load existing DB 

Otherwise: 

- Process sources 

- Generate embeddings 

- Create Chroma DB 

- Persist to disk 

## **Phase 5 — Facts-Only Prompt Design** 

Create: 

```
FACTS_ONLY_PROMPT
```

## **Mandatory Rules** 

1. Use only retrieved context. 

2. Never hallucinate information. 

3. Never answer beyond source material. 

4. Maximum response length: 3 sentences. 

5. Every answer must include exactly one source URL. 

6. Never provide: 

7. Investment advice 

8. Recommendations 

9. Opinions 

10. Predictions 

11. Never calculate future returns. 

12. Reference official factsheets when projections are requested. 

6 

13. Include source refresh date. 

14. If information is unavailable: 

```
I couldn't find that information in the approved sources.
```

## **Standard Advice Refusal** 

```
I can only provide factual information from approved sources and cannot offer
investment advice.
```

## **Phase 6 — Groq QA Chain** 

## **Environment Setup** 

```
fromdotenvimportload_dotenv
importos
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")
```

## **Imports** 

```
fromlangchain_groqimportChatGroq
fromlangchain.chainsimportRetrievalQA
```

## **Build Chain** 

Implement: 

```
build_qa_chain()
```

## **Model Configuration** 

```
llm=ChatGroq(
model_name="llama-3.3-70b-versatile",
temperature=0
```

```
)
```

7 

## **Retrieval QA** 

`qa_chain = RetrievalQA.from_chain_type( llm=llm, chain_type="stuff", retriever=retriever, chain_type_kwargs={ "prompt": FACTS_ONLY_PROMPT } )` 

Return: 

`qa_chain` 

## **Phase 7 — Streamlit Interface** 

## **Application Title** 

`HDFC MF Facts Assistant` 

## **Welcome Message** 

`Welcome! Ask any factual question about HDFC Mutual Fund schemes.` 

## **Example Questions** 

Provide buttons for: 

- Expense ratio of HDFC Top 100 Fund direct plan? 

- What is the lock-in period for HDFC ELSS Tax Saver? 

- How to download capital gains statement? 

## **Warning Banner** 

⚠️ `Facts-only. No investment advice.` 

## **User Input** 

Use: 

8 

```
st.text_input()
```

## **Query Execution** 

```
result=qa({"query":question})
```

Display: 

```
st.markdown(result["result"])
```

## **Phase 8 — Testing** 

Run: 

```
streamlitrunapp.py
```

## **Validation Checklist** 

## **Retrieval Accuracy** 

Question: 

```
What is the lock-in period for HDFC ELSS Tax Saver?
```

Expected: 

- Accurate answer 

- Correct source URL 

## **Investor Services** 

Question: 

```
How do I download my capital gains statement?
```

Expected: 

- Correct process 

- Official source citation 

9 

## **Advice Refusal** 

Question: 

```
Should I invest in ELSS?
```

Expected: 

- Refusal 

- No recommendation 

## **Missing Information** 

Question: 

```
What return will this fund generate in five years?
```

Expected: 

- Refusal 

- Factsheet reference 

## **Phase 9 — Packaging** 

Generate: 

## **README.md** 

Include: 

- Setup 

- Architecture 

- Usage 

- Limitations 

## **sample_qa.md** 

Include: 

- 5–10 representative Q&A examples 

## **source_list.csv** 

Export complete source registry. 

10 

## **Footer Disclaimer** 

```
This assistant provides factual information from approved public sources only
and does not provide investment advice.
```

## **Final Deliverables** 

- app.py 

- rag_assistant.py 

- source_list.py 

- requirements.txt 

- .env (gitignored) 

- README.md 

- sample_qa.md 

- source_list.csv 

## **Acceptance Criteria** 

The implementation is complete when: 

- All sources load successfully 

- Documents are indexed correctly 

- ChromaDB persistence works 

- Groq integration functions properly 

- Source citations appear in every response 

- Advice questions are refused 

- Streamlit UI is operational 

- Documentation is complete 

## **Run Commands** 

```
pipinstall-rrequirements.txt
```

```
streamlitrunapp.py
```

11 

## **Notes for Cursor / AI Coding Agents** 

Implementation Rules: 

- Follow phases sequentially. 

- Do not introduce additional sources. 

- Restrict answers to retrieved context. 

- Prioritize factual correctness. 

- Fail safely when information is unavailable. 

- Use Groq + Llama 3.3 70B exclusively. 

- Do not require OpenAI APIs. 

- Persist vector embeddings locally. 

12 

