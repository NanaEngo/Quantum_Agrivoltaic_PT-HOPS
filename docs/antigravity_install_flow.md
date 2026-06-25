# Google Antigravity Installation Flow & Architecture Graph

This document provides a visual and step-by-step guide mapping the installation, initialization, authentication, and directory structure of the **Google Antigravity IDE** and **Antigravity 2.0 Agent Platform**.

---

## 1. Complete Installation Lifecycle

The flowchart below traces the path from raw system requirements to a fully verified, authenticated Antigravity IDE and Agent Environment.

```mermaid
graph TD
    %% Define Styles
    classDef req fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#bbf,stroke:#333,stroke-width:1px;
    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    classDef success fill:#9f9,stroke:#333,stroke-width:2px;
    
    %% Prerequisites Section
    subgraph Prerequisites ["1. System Prerequisites"]
        A[Google Chrome Browser]
        B[Personal Google/Gmail Account]
        C[OS: Linux / macOS / Windows]
    end

    %% Installation Methods Section
    subgraph InstallMethods ["2. Choose Installation Method"]
        D{"Which Interface?"}:::decision
        E["GUI Installer (antigravity.google/download)"]:::process
        F["CLI Script (Automated Shell)"]:::process
    end
    
    Prerequisites --> D

    %% Platform Branches
    subgraph GUIInstall ["3A. GUI Installation Flow"]
        E_Win["Windows: .exe Installer (User-Level AppData)"]:::process
        E_Mac["macOS: DMG Mount & Drag to Applications"]:::process
        E_Lin["Linux: .tar.gz Extract & Setup Launcher"]:::process
    end

    subgraph CLIInstall ["3B. CLI Installation Commands"]
        F_Unix["macOS/Linux Shell:<br><code>curl -fsSL https://antigravity.google/cli/install.sh | bash</code>"]:::process
        F_Win["Windows PowerShell:<br><code>irm https://antigravity.google/cli/install.ps1 | iex</code>"]:::process
    end

    E --> E_Win & E_Mac & E_Lin
    F --> F_Unix & F_Win

    %% Post-Install Authentication & Config
    subgraph InitSetup ["4. First Run & Authentication"]
        G[Launch Antigravity IDE]:::process
        H[Redirect to Chrome for Google OAuth2]:::process
        I{"Import Settings?"}:::decision
        J[Migrate VS Code / Cursor Configs]:::process
        K[Initialize Default Local Directories]:::process
    end

    E_Win & E_Mac & E_Lin --> G
    F_Unix & F_Win --> G
    G --> H
    H --> I
    I -- Yes --> J --> K
    I -- No --> K

    %% Complete Status
    subgraph Verification ["5. Verification & Success"]
        L[Verify CLI Path bindings: <code>antigravity --version</code>]:::process
        M["System Ready (Antigravity Agent Active)"]:::success
    end

    K --> L --> M
```

---

## 2. Directory Layout & Runtime Environment

Once installed, Antigravity structures its application data, workspace metadata, and agent logs within standard user-level directories:

```mermaid
graph TD
    classDef folder fill:#eef,stroke:#99f,stroke-width:2px;
    classDef file fill:#fff,stroke:#ccc,stroke-width:1px;

    UserHome["User Home (~/)"]:::folder
    GeminiDir["~/.gemini/"]:::folder
    AgDir["~/.gemini/antigravity-ide/"]:::folder
    
    BrainDir["brain/"]:::folder
    LogsDir["logs/"]:::folder
    ConfDir["config/"]:::folder
    
    Conversations["[conversation-id]/"]:::folder
    Transcripts["transcript.jsonl"]:::file
    Scratch["scratch/"]:::folder
    
    UserHome --> GeminiDir
    GeminiDir --> AgDir
    
    AgDir --> BrainDir
    AgDir --> LogsDir
    AgDir --> ConfDir
    
    BrainDir --> Conversations
    Conversations --> Transcripts
    Conversations --> Scratch
```

---

## 3. Platform Directory Matrix

| Operating System | App Installation Path | Local Config / AppData Directory |
| :--- | :--- | :--- |
| **Linux** | User bin directory / Custom path | `~/.gemini/antigravity-ide/` |
| **macOS** | `/Applications/Google Antigravity.app` | `~/Library/Application Support/Google/Antigravity/` |
| **Windows** | `%USERPROFILE%\AppData\Local\Programs\GoogleAntigravity\` | `%USERPROFILE%\AppData\Roaming\Google\Antigravity\` |

---

## 4. Post-Installation Verification Checklist

1. **Verify Binary Access**:
   ```bash
   antigravity --version
   ```
2. **Ensure Port Binding (MCP Servers & Local Agent Loop)**:
   Verify that local loopback connections on default agent ports are open.
3. **Verify Auth Credentials**:
   If the agent experiences connectivity issues, run `antigravity login` to trigger a re-authorization token flow via Chrome.

---

## 5. Model Context Protocol (MCP) & Python SDK Installation

For advanced development, you can write custom agents with the Python SDK and register external tools using MCP.

### A. Python SDK Setup
To install the official Google Antigravity Agentic SDK for custom agent engineering:
```bash
pip install google-antigravity
```

### B. MCP Server Registration
Antigravity integrates with external systems via the Model Context Protocol (MCP). To register a server (such as `comfyui-mcp-server` located in this workspace):

1. Edit the configuration settings file:
   - For workspace-specific settings: `blackbox_mcp_settings.json` in the project root.
   - For global settings: `~/.gemini/antigravity-ide/config/mcp.json`.
2. Add your server declaration:
```json
{
  "mcpServers": {
    "github.com/joenorton/comfyui-mcp-server": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:9000/mcp"
    }
  }
}
```

---

## 6. End-to-End Installation Flow with Extensions & SDK

Here is the updated full pipeline, showing the convergence of IDE, SDK, and MCP integrations:

```mermaid
graph TD
    classDef main fill:#bbf,stroke:#333,stroke-width:1px;
    classDef sdk fill:#f9f,stroke:#333,stroke-width:1px;
    classDef mcp fill:#ffb,stroke:#333,stroke-width:1px;
    
    A["Download IDE Installer or Script"]:::main --> B["Run IDE Installation"]:::main
    B --> C["OAuth Google Authentication"]:::main
    C --> D["IDE Initialized"]:::main
    
    D --> E["Option 1: Standard AI Coding"]:::main
    
    D --> F["Option 2: SDK Custom Agent Development"]:::sdk
    F --> F1["Install SDK: <code>pip install google-antigravity</code>"]:::sdk
    F1 --> F2["Design & Orchestrate Custom AGY Agents"]:::sdk
    
    D --> G["Option 3: Extend via Model Context Protocol (MCP)"]:::mcp
    G --> G1["Install MCP Server (e.g. comfyui-mcp-server)"]:::mcp
    G1 --> G2["Register in blackbox_mcp_settings.json"]:::mcp
    G2 --> G3["Expose Custom APIs / Nodes / Tools to Agent"]:::mcp
```

