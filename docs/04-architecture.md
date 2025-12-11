[← Previous: Use Case](03-use-case.md) | [Next: Data Collection →](05-data-collection.md)

---

# Architecture Overview

## Clean Architecture (Hexagonal / Ports & Adapters)

```mermaid
graph TB
    subgraph Infrastructure["🌐 Infrastructure Layer"]
        Web["NiceGUI Web Interface"]
        Config["Configuration & DI"]
    end

    subgraph Adapters["🔌 Adapters Layer"]
        Gateway["GitHub Gateway"]
        Storage["Pickle Storage"]
    end

    subgraph UseCases["💼 Use Cases Layer"]
        UC1["Get Repo Info"]
        UC2["Cache Management"]
        Ports["Port Interfaces"]
    end

    subgraph Domain["🏛️ Domain Layer"]
        Entities["Repository Entity"]
        DTO["Data Transfer Objects"]
    end

    Web --> UC1
    Web --> UC2
    Config --> Gateway
    Config --> Storage
    UC1 --> Ports
    UC2 --> Ports
    Gateway -.implements.-> Ports
    Storage -.implements.-> Ports
    UC1 --> Entities
    Gateway --> Entities
    Storage --> Entities
```

## Key Benefits
✅ **Testability** - Easy to mock dependencies  
✅ **Maintainability** - Clear separation of concerns  
✅ **Flexibility** - Swap implementations without breaking logic  
✅ **Dependency Inversion** - Core logic isolated from frameworks  

---

[↑ Back to Top](#architecture-overview)