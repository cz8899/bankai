flowchart TD
    %% Visual Groupings
    subgraph UI["📱 Frontend Layer"]
        A[Streamlit UI<br>ECS Fargate + ALB]:::ui
        V[Admin Dashboard]:::ui
    end
    subgraph Security["🛡️ Security & Compliance Layer"]
        PB[IAM Roles &<br>Permission Boundaries]:::security
        WL[Custom WAF* Scanner]:::security
    end
    subgraph Ingest["📥 Ingestion Pipeline"]
        C[S3 Bucket] --> D[Ingestion Lambda]
        D --> E[Textract/OCR*]
        E --> F[chunker.py]
    end
    subgraph Retrieval["🔍 Retrieval & Ranking"]
        J[RetrievalCoordinator]
        L[BedrockRanker]
    end
    subgraph LLM["🧠 LLM Execution"]
        T1[LLM Invocation Service]
        T2[Bedrock API]
    end
    subgraph Core["🧠 Core Engine"]
        QR[HybridRAGRouter]
        IP[IntentionPlanner<br>→ ConversationPlanner]
        M[ConversationPlanner]
        N[FallbackRouter]
        O[FeedbackLoopController]
        P[PolicyStore]
        Q[Redis<br>Cache & Session]
        R[CloudWatch Logs]
        A_LOGGER[AnalyticsLogger]
    end
    %% Core Flow
    A -->|POST /query| QR
    QR -->|Check Cache| Q
    QR --> IP
    IP --> M
    %% Data Flow
    F -->|Write Content| G[JSONL Chunks]
    F -->|Store Embeddings| H[ChromaDB<br>Vector Store]
    F -->|Write Metadata| I[DynamoDB<br>Metadata & Logs]
    %% Retrieval Path
    M --> J
    J -->|Vector Search| H
    J -->|Keyword Search| K[OpenSearch]
    QR -->|Update Context| Q
    QR --> L
    QR --> N
    QR --> O
    QR --> P
    %% Execution
    N --> T1
    M --> T1
    L --> T1
    O --> T1
    T1 -->|Cache Results| Q
    T1 --> T2
    %% Optional Components
    ext[Partner API Gateway]:::service -.->|Optional OCR*/fallback| E
    ext --> QR
    %% Security Links
    PB -.->|Govern| D & T2 & H & QR
    WL -->|Findings| R
    WL -->|Metrics| K
    %% Feedback & Admin
    A -->|Feedback| U[streamlit_feedback.py]
    U --> I
    U -->|Improve Ranking| L
    V -->|List Jobs| I
    V -->|Retry| D
    V --> WL
    %% Click Annotations
    click WL "https://aws.amazon.com/waf/" "Web Application Firewall"
    click T2 "https://aws.amazon.com/bedrock/" "LLM = Large Language Model"
    click E "https://aws.amazon.com/textract/" "OCR = Optical Character Recognition"
    click H "https://docs.trychroma.com/" "ChromaDB Documentation"
    click PB "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html" "IAM Best Practices"
    %% Styling
    classDef ui fill:#4CAF50,stroke:#388E3C,color:white;
    classDef security fill:#F44336,stroke:#D32F2F,color:white;
    classDef ingest fill:#9C27B0,stroke:#7B1FA2,color:white;
    classDef retrieval fill:#2196F3,stroke:#1976D2,color:white;
    classDef llm fill:#FF9800,stroke:#F57C00,color:white;
    classDef service fill:#FF5722,stroke:#E64A19;
    classDef note fill:#fff,stroke:#ddd;
    %% Annotations
    note1["*Abbreviations:<br>LLM: Large Language Model<br>WAF: Web Application Firewall<br>OCR: Optical Character Recognition"]:::note
    note2["Dashed arrows indicate<br>optional components/flows"]:::note
    class A,V ui
    class PB,WL security
    class C,D,E,F ingest
    class J,L retrieval
    class T1,T2 llm
    class ext service
    class note1,note2 note
<img width="740" height="1637" alt="image" src="https://github.com/user-attachments/assets/53f7467a-60c9-4625-8da9-4fc7360be26e" />

