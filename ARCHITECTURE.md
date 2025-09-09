# Kasm MCP Server Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Security Architecture](#security-architecture)
5. [Deployment Architecture](#deployment-architecture)

## System Overview

The Kasm MCP Server acts as a bridge between AI agents (like Cline) and Kasm Workspaces, providing secure, programmatic access to containerized desktop environments.

### High-Level Architecture

```mermaid
graph TB
    subgraph "AI Layer"
        A[AI Agent/Cline]
    end
    
    subgraph "MCP Layer"
        B[MCP Client]
        C[MCP Server]
        D[Security Layer]
        E[Tool Registry]
    end
    
    subgraph "Integration Layer"
        F[Kasm API Client]
        G[Authentication]
    end
    
    subgraph "Kasm Platform"
        H[Kasm API]
        I[Container Manager]
        J[Workspace Sessions]
    end
    
    A <-->|MCP Protocol| B
    B <-->|HTTP+SSE| C
    C --> D
    C --> E
    E --> F
    F --> G
    G <-->|REST API| H
    H --> I
    I --> J
```

## Component Architecture

### Detailed Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Kasm MCP Server                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │   MCP Server    │  │  Tool Registry   │  │ Security Layer   │   │
│  │                 │  │                  │  │                  │   │
│  │ - HTTP+SSE      │  │ - Command Tools  │  │ - Roots Valid.   │   │
│  │ - JSON-RPC      │  │ - Session Tools  │  │ - Path Check     │   │
│  │ - Async Handler │  │ - Admin Tools    │  │ - Cmd Filter     │   │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘   │
│           │                    │                      │             │
│           └────────────────────┴──────────────────────┘             │
│                                │                                    │
│  ┌─────────────────────────────┴────────────────────────────────┐  │
│  │                      Core Engine                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Request      │  │ Response     │  │ Error            │  │  │
│  │  │ Handler      │  │ Formatter    │  │ Handler          │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│  ┌─────────────────────────────┴────────────────────────────────┐  │
│  │                    Kasm API Client                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Auth Manager │  │ API Wrapper  │  │ Connection Pool  │  │  │
│  │  │ (SHA256)     │  │              │  │                  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

#### 1. MCP Server (`src/server.py`)
- **Purpose**: Main entry point for MCP protocol handling
- **Responsibilities**:
  - Protocol implementation
  - Request routing
  - Response formatting
  - Connection management

#### 2. Tool Registry (`src/tools/`)
- **Purpose**: Manages available tools and their execution
- **Components**:
  - `command.py`: Execute commands in containers
  - `session.py`: Manage Kasm sessions and file operations
  - `admin.py`: Administrative functions

#### 3. Security Layer (`src/security/`)
- **Purpose**: Enforces security boundaries
- **Components**:
  - `roots.py`: MCP Roots implementation
  - Path validation
  - Command filtering
  - Input sanitization

#### 4. Kasm API Client (`src/kasm_api/`)
- **Purpose**: Interfaces with Kasm Workspaces API
- **Features**:
  - SHA256 authentication
  - Connection pooling
  - Error handling
  - Request/response mapping

## Data Flow

### Tool Execution Flow

```mermaid
sequenceDiagram
    participant AI as AI Agent
    participant MC as MCP Client
    participant MS as MCP Server
    participant SL as Security Layer
    participant TL as Tool
    participant KC as Kasm Client
    participant KA as Kasm API

    AI->>MC: Natural language request
    MC->>MS: MCP tool call
    MS->>MS: Parse request
    MS->>SL: Validate request
    SL->>SL: Check security rules
    SL-->>MS: Validation result
    
    alt Validation passed
        MS->>TL: Execute tool
        TL->>KC: Prepare API call
        KC->>KC: Generate auth hash
        KC->>KA: API request
        KA-->>KC: API response
        KC-->>TL: Processed result
        TL-->>MS: Tool result
        MS-->>MC: MCP response
        MC-->>AI: Formatted result
    else Validation failed
        MS-->>MC: Security error
        MC-->>AI: Error message
    end
```

### Session Creation Flow

```mermaid
stateDiagram-v2
    [*] --> RequestReceived
    RequestReceived --> ValidateParams
    ValidateParams --> CheckPermissions
    CheckPermissions --> PrepareAPICall
    PrepareAPICall --> AuthenticateRequest
    AuthenticateRequest --> SendToKasm
    SendToKasm --> WaitForResponse
    WaitForResponse --> ProcessResponse
    ProcessResponse --> ReturnSessionInfo
    ReturnSessionInfo --> [*]
    
    ValidateParams --> [*]: Invalid params
    CheckPermissions --> [*]: Insufficient permissions
    SendToKasm --> [*]: API error
```

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    External Requests                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Layer 1: Transport Security                  │
│                                                              │
│  • HTTP+SSE with optional TLS                               │
│  • Connection authentication                                 │
│  • Rate limiting                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Layer 2: Protocol Validation                    │
│                                                              │
│  • MCP protocol compliance                                   │
│  • Schema validation                                         │
│  • Input sanitization                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Layer 3: Application Security                   │
│                                                              │
│  • MCP Roots enforcement                                     │
│  • Command filtering                                         │
│  • Path validation                                          │
│  • Blocked command list                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Layer 4: API Security                          │
│                                                              │
│  • SHA256 authentication                                     │
│  • API key management                                        │
│  • Request signing                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            Layer 5: Container Isolation                      │
│                                                              │
│  • Kasm container boundaries                                 │
│  • Resource isolation                                        │
│  • Network segmentation                                      │
└─────────────────────────────────────────────────────────────┘
```

### Trust Boundaries

```mermaid
graph TB
    subgraph "Untrusted Zone"
        A[External Network]
        B[AI Agent Requests]
    end
    
    subgraph "Semi-Trusted Zone"
        C[MCP Server]
        D[Input Validation]
        E[Security Filters]
    end
    
    subgraph "Trusted Zone"
        F[Kasm API Client]
        G[Authenticated Requests]
    end
    
    subgraph "Isolated Zone"
        H[Kasm Containers]
        I[User Workspaces]
    end
    
    A --> B
    B -->|Validate| C
    C --> D
    D --> E
    E -->|Sanitized| F
    F --> G
    G -->|Authorized| H
    H --> I
    
    style A fill:#ff6666
    style B fill:#ff6666
    style C fill:#ffff66
    style D fill:#ffff66
    style E fill:#ffff66
    style F fill:#66ff66
    style G fill:#66ff66
    style H fill:#6666ff
    style I fill:#6666ff
```

## Deployment Architecture

### Docker Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      Host System                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Docker Engine                        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────┐     │   │
│  │  │         kasm-mcp-server-v2:latest         │     │   │
│  │  ├───────────────────────────────────────────┤     │   │
│  │  │                                           │     │   │
│  │  │  • Python 3.11 Runtime                   │     │   │
│  │  │  • MCP Server Application                │     │   │
│  │  │  • Non-root user (mcp-user)             │     │   │
│  │  │  • Port 8080 exposed                     │     │   │
│  │  │                                           │     │   │
│  │  │  Volumes:                                │     │   │
│  │  │  - ./certs:/home/mcp-user/certs:ro      │     │   │
│  │  │                                           │     │   │
│  │  │  Environment:                            │     │   │
│  │  │  - KASM_API_URL                         │     │   │
│  │  │  - KASM_API_KEY                         │     │   │
│  │  │  - KASM_API_SECRET                      │     │   │
│  │  │  - ALLOWED_ROOTS                        │     │   │
│  │  └───────────────────────────────────────────┘     │   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────┐     │   │
│  │  │           mcp-network (bridge)            │     │   │
│  │  └───────────────────────────────────────────┘     │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    systemd                           │   │
│  │  • kasm-mcp-server-v2.service                      │   │
│  │  • Auto-restart on failure                         │   │
│  │  • Logging to journal                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Network Architecture

```mermaid
graph LR
    subgraph "Client Network"
        A[AI Agent]
    end
    
    subgraph "DMZ"
        B[Load Balancer<br/>Optional]
        C[Firewall Rules<br/>Port 8080]
    end
    
    subgraph "Application Network"
        D[MCP Server<br/>Container]
        E[Health Check<br/>Endpoint]
    end
    
    subgraph "Backend Network"
        F[Kasm API<br/>Endpoint]
        G[Kasm<br/>Workspaces]
    end
    
    A -->|HTTPS| B
    B --> C
    C --> D
    D --> E
    D -->|HTTPS| F
    F --> G
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
    style F fill:#99f,stroke:#333,stroke-width:2px
```

## Scalability Considerations

### Horizontal Scaling

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐    ┌────────▼──────┐    ┌───────▼──────┐
│ MCP Server 1 │    │ MCP Server 2  │    │ MCP Server N │
│              │    │               │    │              │
│ Container    │    │ Container     │    │ Container    │
└───────┬──────┘    └────────┬──────┘    └───────┬──────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Kasm API       │
                    │   (Shared)       │
                    └──────────────────┘
```

### Performance Optimization

1. **Connection Pooling**: Reuse Kasm API connections
2. **Async Operations**: Non-blocking I/O for all operations
3. **Caching**: Cache workspace lists and user information
4. **Rate Limiting**: Prevent API exhaustion
5. **Health Checks**: Automatic failover support

## Monitoring and Observability

### Metrics Collection Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Metrics                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request Metrics:           Security Metrics:               │
│  • Request count           • Blocked commands               │
│  • Response time           • Path violations                │
│  • Error rate              • Auth failures                  │
│  • Tool usage              • Rate limit hits                │
│                                                              │
│  System Metrics:           API Metrics:                     │
│  • CPU usage               • API call count                 │
│  • Memory usage            • API response time              │
│  • Connection count        • API error rate                 │
│  • Thread pool size        • Auth hash generation time      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Future Architecture Considerations

1. **Message Queue Integration**: For async operations
2. **Database Backend**: For audit logging and state management
3. **Multi-Region Support**: Geographic distribution
4. **WebSocket Support**: Real-time bidirectional communication
5. **Plugin Architecture**: Extensible tool system
