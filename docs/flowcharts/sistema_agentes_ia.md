graph TD
    A[create_agent] --> B{provider?}
    B -->|gemini| C[GeminiAgent]
    B -->|openai| D[OpenAIAgent]
    C --> E[generate_response]
    D --> E
    E --> F[retry_on_failure]
    F --> G[rate_limited]
    G --> H[cached]
    H --> I{Cache hit?}
    I -->|Yes| J[Return cached]
    I -->|No| K[Call API]
    J --> L[Response ready]
    K --> L