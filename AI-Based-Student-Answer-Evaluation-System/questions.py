"""
Predefined question bank for the AI-Based Student Answer Evaluation System.
Each question includes subject metadata, reference answers, required keywords,
synonym sets, and pedagogical example sentences to guide student improvement.
"""

QUESTIONS = [
    {
        "id": "q1",
        "subject": "Object-Oriented Programming",
        "title": "Core Principles of OOP",
        "question": "Explain the four core principles of Object-Oriented Programming (OOP) and briefly describe their significance in software design.",
        "max_marks": 10,
        "reference_answer": (
            "The four core principles of Object-Oriented Programming are Encapsulation, Abstraction, "
            "Inheritance, and Polymorphism. Encapsulation binds together data and functions into a single unit "
            "(class) and restricts direct access to internal state, promoting data hiding and security. "
            "Abstraction hides complex implementation details and exposes only the essential features to the user, "
            "typically via interfaces and abstract classes. Inheritance enables a child class to inherit properties "
            "and behaviors from a parent class, facilitating code reusability and hierarchical organization. "
            "Polymorphism allows objects to take multiple forms and respond differently to the same method call, "
            "achieved through method overloading (compile-time) and method overriding (runtime)."
        ),
        "keywords": [
            {
                "term": "encapsulation",
                "synonyms": ["encapsulate", "encapsulating", "data hiding", "bundles data"],
                "example": "Encapsulation bundles fields and methods into a single class, protecting private data with public getters and setters."
            },
            {
                "term": "abstraction",
                "synonyms": ["abstract", "abstracting", "essential features", "hides complexity"],
                "example": "Abstraction hides low-level implementation details behind clean interfaces and abstract base classes."
            },
            {
                "term": "inheritance",
                "synonyms": ["inherit", "inheriting", "subclass", "derived class", "parent class", "super class"],
                "example": "Inheritance allows a subclass to inherit attributes and methods from a superclass, maximizing code reuse."
            },
            {
                "term": "polymorphism",
                "synonyms": ["polymorphic", "overriding", "overloading", "multiple forms"],
                "example": "Polymorphism enables methods like 'draw()' to behave differently across different child classes such as Circle and Square."
            },
            {
                "term": "code reusability",
                "synonyms": ["reusable", "reusability", "reuse code"],
                "example": "Applying inheritance directly enhances code reusability, reducing duplicate logic across the codebase."
            },
            {
                "term": "data hiding",
                "synonyms": ["access specifiers", "private variables", "information hiding"],
                "example": "Data hiding prevents external unauthorized tampering by keeping class attributes private."
            }
        ],
        "sample_answers": {
            "good": (
                "The four fundamental principles of OOP are Encapsulation, Abstraction, Inheritance, and Polymorphism. "
                "Encapsulation involves bundling data and related methods into a class and achieving data hiding through private access modifiers. "
                "Abstraction hides background complexities and shows only essential interface details to clients. "
                "Inheritance provides code reusability by allowing child classes to inherit attributes and behaviors from parent classes. "
                "Polymorphism allows objects of different types to be treated uniformly and support method overloading and overriding."
            ),
            "partial": (
                "OOP has inheritance and polymorphism. Inheritance means one class gets methods from another class to reuse code. "
                "Polymorphism means having multiple forms, like method overriding. It makes code easier to write and maintain."
            ),
            "weak": (
                "OOP is object oriented programming. It uses objects and classes. You can write programs faster using functions."
            )
        }
    },
    {
        "id": "q2",
        "subject": "Database Management Systems",
        "title": "Database Normalization",
        "question": "What is Database Normalization? Describe the primary goals and the differences between 1NF, 2NF, and 3NF.",
        "max_marks": 10,
        "reference_answer": (
            "Database Normalization is the systematic process of organizing data in a relational database to minimize "
            "data redundancy and prevent insertion, update, and deletion anomalies. In First Normal Form (1NF), each table cell "
            "must contain only atomic (indivisible) values, and each record must have a unique primary key with no repeating groups. "
            "In Second Normal Form (2NF), the table must first satisfy 1NF and eliminate partial dependencies, meaning every "
            "non-key attribute must be fully functionally dependent on the entire primary key. In Third Normal Form (3NF), "
            "the table must meet 2NF requirements and eliminate transitive dependencies, meaning non-prime attributes must "
            "not depend on other non-prime attributes."
        ),
        "keywords": [
            {
                "term": "redundancy",
                "synonyms": ["duplicate data", "data redundancy", "minimizing redundancy"],
                "example": "Normalization decomposes bloated tables to systematically eliminate duplicate data and redundant storage."
            },
            {
                "term": "anomalies",
                "synonyms": ["insertion anomaly", "update anomaly", "deletion anomaly"],
                "example": "Without normalization, tables suffer from update anomalies where modifying one record requires updating multiple rows."
            },
            {
                "term": "atomic",
                "synonyms": ["atomicity", "indivisible", "single-valued"],
                "example": "First Normal Form requires all columns to hold atomic values rather than comma-separated lists."
            },
            {
                "term": "partial dependency",
                "synonyms": ["partial functional dependency", "fully functional dependent"],
                "example": "Second Normal Form resolves partial dependencies by ensuring non-key columns depend on the entire composite primary key."
            },
            {
                "term": "transitive dependency",
                "synonyms": ["transitive", "transitively dependent"],
                "example": "Third Normal Form removes transitive dependencies where column A determines B, and B determines non-key column C."
            },
            {
                "term": "primary key",
                "synonyms": ["candidate key", "unique key", "composite key"],
                "example": "Every normalized table requires a well-defined primary key to uniquely identify each row."
            }
        ],
        "sample_answers": {
            "good": (
                "Database normalization is the process of structuring relational tables to reduce data redundancy and eliminate anomalies "
                "(insertion, update, and deletion). 1NF requires all attributes to be atomic and rows unique with a primary key. "
                "2NF requires meeting 1NF and removing partial dependencies, ensuring non-key attributes depend on the full primary key. "
                "3NF requires meeting 2NF and eliminating transitive dependencies, ensuring non-prime attributes do not depend on other non-prime attributes."
            ),
            "partial": (
                "Normalization is used in databases to avoid redundancy and keep data clean. 1NF means tables have atomic values. "
                "2NF removes partial dependency. 3NF removes transitive dependency between columns."
            ),
            "weak": (
                "Normalization is making a database normal so it runs faster and stores data in SQL tables."
            )
        }
    },
    {
        "id": "q3",
        "subject": "Operating Systems",
        "title": "Processes vs Threads and Context Switching",
        "question": "Differentiate between a process and a thread, and explain the concept and overhead of context switching.",
        "max_marks": 10,
        "reference_answer": (
            "A process is an independent executing program with its own dedicated memory address space, including its own code, "
            "data, heap, and open file descriptors. A thread is a lightweight unit of execution within a process; multiple threads "
            "belonging to the same process share the same virtual address space, heap, and code segment, while maintaining their "
            "own private registers, program counter, and stack. Context switching is the mechanism where the operating system "
            "CPU scheduler saves the state (execution context) of a currently running process or thread and restores the state of "
            "another so that multiple tasks can share the CPU. Process context switching has higher overhead because it requires "
            "invalidating CPU caches and switching Memory Management Unit (MMU) page tables, whereas thread switching within the "
            "same process is much faster as memory mappings remain shared."
        ),
        "keywords": [
            {
                "term": "address space",
                "synonyms": ["memory space", "virtual memory", "shared memory"],
                "example": "Processes possess isolated virtual address spaces, while threads of a single process share common memory."
            },
            {
                "term": "lightweight",
                "synonyms": ["lightweight process", "lwp", "light-weight"],
                "example": "Threads are referred to as lightweight execution units due to lower resource consumption during creation."
            },
            {
                "term": "context switching",
                "synonyms": ["context switch", "state saving", "scheduling switch"],
                "example": "Context switching allows the OS to freeze a thread's state, store registers, and swap another thread onto the CPU."
            },
            {
                "term": "overhead",
                "synonyms": ["cpu overhead", "cost", "latency", "cache flush"],
                "example": "Switching between heavy processes incurs cache invalidation overhead and requires updating TLB page table pointers."
            },
            {
                "term": "registers",
                "synonyms": ["cpu registers", "program counter", "pc", "stack pointer"],
                "example": "Each thread retains its own program counter and CPU registers to resume independent execution accurately."
            },
            {
                "term": "stack",
                "synonyms": ["call stack", "thread stack", "local stack"],
                "example": "While threads share the global heap, each thread maintains an isolated call stack for local function frames."
            }
        ],
        "sample_answers": {
            "good": (
                "A process is a program in execution that has its own isolated memory address space and resources. In contrast, "
                "a thread is a lightweight unit of execution inside a process, sharing the heap and memory address space with peer threads, "
                "while keeping its own stack and registers. Context switching is the OS mechanism of saving the state of the active task "
                "and restoring another task. Process context switching has high overhead due to flushing TLB and MMU page tables, while thread "
                "switching has lower overhead because memory mappings are preserved."
            ),
            "partial": (
                "A process is a running program and a thread is a smaller part of a process. Threads share memory, but processes do not. "
                "Context switching is when the CPU switches from one task to another, which takes time and creates overhead."
            ),
            "weak": (
                "A process is when you open an app. A thread is when you run things at the same time. The CPU does context switching."
            )
        }
    },
    {
        "id": "q4",
        "subject": "Machine Learning & AI",
        "title": "Overfitting vs Underfitting",
        "question": "Explain the difference between overfitting and underfitting in Machine Learning models, and outline three techniques to combat overfitting.",
        "max_marks": 10,
        "reference_answer": (
            "In Machine Learning, underfitting occurs when a model is overly simplistic and cannot capture the underlying patterns "
            "or trend in the training data, leading to high bias and poor performance on both training and test datasets. Overfitting "
            "occurs when a model is overly complex and memorizes the training data, including noise and random fluctuations, leading "
            "to high variance, near-perfect training accuracy, but very poor generalization on unseen test data. To combat overfitting, "
            "practitioners employ: 1) Regularization techniques such as L1 (Lasso) and L2 (Ridge) which penalize large model weights; "
            "2) Cross-validation (e.g., k-fold) and early stopping to halt training before the model over-learns noise; and "
            "3) Data augmentation or dropout (in deep neural networks) to inject variance and discourage co-adaptation of neurons."
        ),
        "keywords": [
            {
                "term": "high bias",
                "synonyms": ["bias", "underfitting bias", "excessive bias"],
                "example": "Underfitting is characterized by high bias where the model assumes an overly simple hypothesis for the data."
            },
            {
                "term": "high variance",
                "synonyms": ["variance", "overfitting variance", "excessive variance"],
                "example": "Overfitting produces high variance, meaning slight shifts in the input lead to wildly divergent predictions."
            },
            {
                "term": "generalization",
                "synonyms": ["generalize", "unseen data", "test set performance"],
                "example": "A properly trained model achieves strong generalization, performing accurately on new, unseen test samples."
            },
            {
                "term": "regularization",
                "synonyms": ["l1", "l2", "ridge", "lasso", "weight decay"],
                "example": "L2 regularization adds a penalty proportional to weight squares, shrinking weights to prevent overfitting."
            },
            {
                "term": "cross-validation",
                "synonyms": ["k-fold", "validation set", "k-fold cross-validation"],
                "example": "Using k-fold cross-validation ensures the model is evaluated on multiple independent validation splits."
            },
            {
                "term": "early stopping",
                "synonyms": ["dropout", "data augmentation", "pruning"],
                "example": "Early stopping monitors validation loss and halts training as soon as test loss begins to rise."
            }
        ],
        "sample_answers": {
            "good": (
                "Underfitting happens when a model is too simple to capture the underlying structure of the data, exhibiting high bias and "
                "poor accuracy on both training and test sets. Overfitting occurs when a model is excessively complex, fitting noise in the "
                "training set and suffering from high variance with poor generalization on unseen data. Three ways to prevent overfitting are: "
                "1) Regularization (L1/L2 penalties on weights), 2) Cross-validation and early stopping, and 3) Data augmentation or dropout in neural networks."
            ),
            "partial": (
                "Overfitting is when a model learns training data too well and fails on test data because of high variance. "
                "Underfitting is when the model is too basic with high bias. You can use regularization and cross-validation to solve it."
            ),
            "weak": (
                "Overfitting is fitting too much and underfitting is not fitting enough. You can fix it with more data."
            )
        }
    },
    {
        "id": "q5",
        "subject": "Computer Networks",
        "title": "TCP vs UDP Protocols",
        "question": "Compare TCP and UDP protocols, highlighting their differences in reliability, connection establishment, header size, and typical use cases.",
        "max_marks": 10,
        "reference_answer": (
            "Transmission Control Protocol (TCP) is a connection-oriented, reliable transport protocol that guarantees ordered, "
            "error-free delivery of packets through mechanisms like the three-way handshake (SYN, SYN-ACK, ACK), sequence numbers, "
            "acknowledgments (ACKs), and flow and congestion control. It features a larger header size (20 to 60 bytes) and higher latency. "
            "In contrast, User Datagram Protocol (UDP) is a connectionless, best-effort protocol that does not establish a formal connection "
            "and does not guarantee packet arrival, ordering, or duplicate protection. UDP features a lightweight fixed header (8 bytes) "
            "and minimal latency. Consequently, TCP is ideal for applications requiring data integrity such as HTTP/HTTPS web browsing, "
            "email (SMTP), and file transfers (FTP), whereas UDP is preferred for real-time applications where low latency is critical and "
            "minor packet loss is tolerable, such as video streaming, online gaming, VoIP, and DNS lookups."
        ),
        "keywords": [
            {
                "term": "connection-oriented",
                "synonyms": ["three-way handshake", "syn ack", "handshake"],
                "example": "TCP is connection-oriented, demanding a 3-way handshake before transmitting application payload."
            },
            {
                "term": "connectionless",
                "synonyms": ["best effort", "no handshake"],
                "example": "UDP operates connectionless, sending individual datagrams directly without waiting for a connection setup."
            },
            {
                "term": "acknowledgments",
                "synonyms": ["ack", "acks", "retransmission", "error checking", "reliable delivery"],
                "example": "TCP uses sequence numbers and acknowledgments to trigger retransmission if packets are lost in transit."
            },
            {
                "term": "header size",
                "synonyms": ["header overhead", "20 bytes", "8 bytes"],
                "example": "TCP carries a minimum 20-byte header overhead compared to UDP's lightweight 8-byte fixed header."
            },
            {
                "term": "flow and congestion control",
                "synonyms": ["congestion control", "flow control", "sliding window"],
                "example": "TCP dynamically throttles transmission rates using congestion control algorithms to avoid network collapse."
            },
            {
                "term": "latency",
                "synonyms": ["real-time", "streaming", "low latency", "packet loss"],
                "example": "UDP achieves minimal latency, making it the preferred choice for real-time VoIP and multiplayer gaming."
            }
        ],
        "sample_answers": {
            "good": (
                "TCP is a connection-oriented protocol that ensures reliable, ordered packet delivery using a three-way handshake, "
                "acknowledgments, sequence numbers, and flow and congestion control. It has a larger header size (at least 20 bytes). "
                "UDP is a connectionless protocol providing fast, best-effort delivery without guarantees or retransmission, with a compact "
                "8-byte header size. TCP is used where reliability is essential like web (HTTP) and file transfer (FTP), while UDP is used for "
                "low latency real-time needs like VoIP, video streaming, and online gaming."
            ),
            "partial": (
                "TCP is reliable and uses handshakes and acknowledgments, making it good for web browsing. "
                "UDP is faster and connectionless with smaller header size, used for gaming and live streaming."
            ),
            "weak": (
                "TCP and UDP are internet protocols. TCP is slower and UDP is faster."
            )
        }
    }
]


def get_all_questions():
    """Return list of questions for the UI dropdown."""
    return [
        {
            "id": q["id"],
            "subject": q["subject"],
            "title": q["title"],
            "question": q["question"],
            "max_marks": q["max_marks"],
            "reference_answer": q["reference_answer"],
            "keywords": [k["term"] for k in q["keywords"]],
            "sample_answers": q.get("sample_answers", {})
        }
        for q in QUESTIONS
    ]


def get_question_by_id(qid: str):
    """Retrieve full question object by ID."""
    for q in QUESTIONS:
        if q["id"] == qid:
            return q
    return None
