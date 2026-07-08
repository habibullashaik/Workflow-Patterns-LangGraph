# 🧠 Workflow Patterns in LangGraph

> A hands-on, production-style exploration of the four core orchestration patterns that power modern Agentic AI systems — Sequential, Router, Parallel, and Supervisor — built from scratch with LangGraph.

---

## 📖 Introduction

Every impressive AI agent you've seen — a coding assistant that plans and executes, a research bot that gathers and synthesizes, a customer support system that routes and resolves — is not "one big prompt." It is a **workflow**: a graph of smaller, specialized steps connected by explicit control flow.

LLMs are powerful reasoning engines, but reasoning alone doesn't make a reliable system. What makes an agent *production-grade* is the **structure around the model** — how state is passed, how decisions are made about what runs next, how work is parallelized, and how a process knows when it's actually done.

This is why **workflow patterns** are the real foundation of Agentic AI. Frameworks like LangGraph don't make agents "smarter" — they make agent *behavior predictable, debuggable, and composable*. Once you understand these four patterns, you can look at almost any production agent system and recognize which combination of them is running under the hood.

---

## 🎯 Why This Project?

Most tutorials show *one* agent doing *one* thing. That's a good first step, but it hides the real engineering problem: **how do you connect multiple agents together in a way that's reliable and scalable?**

I built this project to answer that question for myself, hands-on, by implementing the same three core agents — **Research**, **Writer**, and **Reviewer** — inside four different orchestration architectures. Reusing the same agents across all four patterns makes the comparison honest: the only thing that changes is the *shape of the graph*, not the underlying capability. That contrast is what makes the differences between Sequential, Router, Parallel, and Supervisor workflows click.

This repo is both:
- A **working reference implementation** of each pattern, and
- A **teaching resource** for anyone trying to understand how real agentic systems are architected.

---

## 🏗️ Architecture Overview

### 1️⃣ Sequential Workflow

**Purpose:** Execute a fixed pipeline of agents in a strict, predetermined order. No branching, no decisions — just a linear chain where each agent's output becomes the next agent's input.

**Architecture Diagram:**
```
┌─────────┐      ┌────────┐      ┌──────────┐
│ Research │ ───▶ │ Writer │ ───▶ │ Reviewer │ ───▶ END
└─────────┘      └────────┘      └──────────┘
```

**Flow:**
`START → research → writer → reviewer → END`

**Advantages:**
- Simple to reason about and debug — the execution path is always the same
- Predictable latency (sum of each step)
- Easiest pattern to test and monitor

**Limitations:**
- No adaptability — every input goes through every step, even if unnecessary
- Cannot skip or reorder steps based on context
- Wastes compute/time when a step isn't needed for a given input

**Real-World Use Cases:**
- Document generation pipelines (draft → edit → proofread)
- ETL-style content pipelines
- Any process where the steps are always required, in the same order

**When NOT to Use It:**
- When different inputs require different handling (use **Router** instead)
- When steps are independent and could run concurrently (use **Parallel** instead)
- When the number of steps or their order isn't known in advance (use **Supervisor** instead)

---

### 2️⃣ Router Workflow

**Purpose:** Look at an incoming request and dynamically decide **which single agent** should handle it. Only one path is taken per run.

**Architecture Diagram:**
```
                    ┌────────────┐
                    │   Router   │
                    └─────┬──────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐  ┌────────┐  ┌──────────┐
        │ Research │  │ Writer │  │ Reviewer │
        └──────────┘  └────────┘  └──────────┘
              │            │            │
              └────────────┴────────────┘
                          ▼
                         END
```

**Flow:**
`START → router → (research | writer | reviewer) → END`

The router uses a **conditional edge**, typically backed by an LLM classification call or rule-based logic, to pick exactly one destination node.

**Advantages:**
- Efficient — only does the work that's actually needed
- Easy to extend with new "workers" without touching existing ones
- Natural fit for intent classification / request triage

**Limitations:**
- Only one agent runs per request — no combining of capabilities in a single pass
- Routing quality is only as good as the classifier (LLM or rules) making the decision
- Misrouting can silently produce a wrong or incomplete result

**Real-World Use Cases:**
- Customer support ticket triage (billing vs. technical vs. general)
- Multi-tool assistants that pick the right tool/agent for a query
- Intent-based chatbots

**When NOT to Use It:**
- When a task genuinely needs multiple agents to collaborate on the same request (use **Sequential** or **Supervisor**)
- When you need to fan out identical work across many sub-tasks (use **Parallel**)

---

### 3️⃣ Parallel Workflow

**Purpose:** Break one large task into independent sub-tasks, execute them **simultaneously**, and merge the results before continuing.

**Architecture Diagram:**
```
                    ┌───────────┐
                    │  Splitter │
                    └─────┬─────┘
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │Research 1│    │Research 2│    │Research 3│   (parallel)
     └────┬─────┘    └────┬─────┘    └────┬─────┘
          └────────────────┼────────────────┘
                            ▼
                     ┌────────────┐
                     │   Writer   │  (merged state)
                     └─────┬──────┘
                            ▼
                     ┌────────────┐
                     │  Reviewer  │
                     └─────┬──────┘
                            ▼
                           END
```

**Flow:**
`START → splitter → Send(researcher × N) → writer → reviewer → END`

**Concepts Covered:**
- **`Send` API** — dynamically fan out a variable number of parallel branches at runtime
- **Reducers** — merge results from parallel branches back into shared state (e.g., `Annotated[list, add]`)
- **Parallel State** — each branch operates on its own slice of state before being combined
- **Task Decomposition** — splitting one big job into independent units of work
- **Merge State (Fan-in)** — ensuring downstream nodes run once, with *all* results, not once per branch

**Advantages:**
- Dramatically reduces wall-clock time for independent sub-tasks
- Scales naturally with the number of sub-tasks (`Send` handles this without pre-defining N)
- Encourages clean separation of independent units of work

**Limitations:**
- Requires careful reducer design — get this wrong and downstream nodes fire multiple times instead of once
- Debugging concurrent branches is harder than a linear chain
- Rate limits / cost can spike since multiple LLM calls fire at once

**Real-World Use Cases:**
- Multi-source research (searching 5 sources at once, then synthesizing)
- Batch summarization of many documents
- Parallel tool calls (e.g., checking weather, calendar, and email simultaneously)

**When NOT to Use It:**
- When sub-tasks depend on each other's output (use **Sequential**)
- When the task can't be meaningfully decomposed into independent units
- When cost/rate-limit constraints make concurrent calls impractical

---

### 4️⃣ Supervisor Workflow

**Purpose:** A central **manager agent** repeatedly observes the current state and decides what should happen next — looping until it determines the task is complete.

**Architecture Diagram:**
```
                     ┌───────────────┐
              ┌─────▶│   Supervisor   │◀─────┐
              │      └───────┬───────┘       │
              │              │                │
              │      ┌───────┴────────┐       │
              │      ▼        ▼       ▼       │
              │ ┌────────┐┌───────┐┌────────┐ │
              └─│Research││Writer ││Reviewer│─┘
                └────────┘└───────┘└────────┘
                              │
                       (Supervisor decides
                        task is complete)
                              ▼
                             END
```

**Flow:**
`START → supervisor → (researcher | writer | reviewer) → supervisor → ... → END`

**Concepts Covered:**
- **Orchestration** — one node owns the decision of "what's next"
- **Feedback Loop** — the supervisor re-evaluates state after every worker finishes
- **Conditional Routing** — dynamic edges based on the supervisor's decision
- **Dynamic Decision Making** — the number of steps is not fixed in advance; it depends on the task

**Advantages:**
- Highly flexible — can handle open-ended tasks where the "right" sequence isn't known upfront
- Naturally supports retries, revisions, and quality loops (e.g., "send it back to the writer")
- Closest pattern to how a real human team lead manages work

**Limitations:**
- Harder to predict runtime and cost — the loop could run many iterations
- Supervisor's decision quality (usually LLM-driven) becomes a single point of failure
- Requires careful guardrails (max iterations, termination conditions) to avoid infinite loops

**Real-World Use Cases:**
- Autonomous coding agents (plan → write code → run tests → fix → repeat)
- Complex research assistants that iteratively refine an answer
- Multi-agent systems where quality gates trigger revisions (e.g., reviewer rejects, sends back to writer)

**When NOT to Use It:**
- When the task is simple and the sequence of steps is always the same (use **Sequential** — it's cheaper and more predictable)
- When you need strict cost/latency guarantees (open-ended loops make this hard)
- When a single routing decision is enough (use **Router** instead of paying for repeated supervisor calls)

---

## 📁 Folder Structure

```
workflow-patterns-langgraph/
│
├── agents/
│   ├── article_agent.py        # Writer agent
│   ├── research_agent.py       # Research agent
│   ├── review_agent.py         # Reviewer agent
|   ├── llm.py                  # Shared Groq LLM client
│   └── state.py
│      # Supervisor decision-making agent
│                   # Shared AgentState (TypedDict)
│
├── sequential/
│   └── app.py                  # Sequential workflow graph
│   └── graph.py
├── router/
│   └── app.py                  # Router workflow graph
│   └── graph.py
├── parallelism/
│   ├── splitter.py              # Task decomposition node
│   └── app.py                   # Parallel workflow graph (Send + reducers)
│   └── graph.py
├── supervisor/
│   └── app.py
|   └── supervisor.py                  # Supervisor workflow graph (feedback loop)
│   └── graph.py  
├── diagrams/
│   └── *.png                    # Auto-generated mermaid graph images
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧰 Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Core implementation language |
| **LangGraph** | Graph-based agent orchestration engine |
| **LangChain** | LLM abstractions and message handling |
| **Groq LLM** | Fast, low-latency inference backend |
| **TypedDict** | Strongly-typed shared state schema |
| **Conditional Edges** | Dynamic routing logic (Router, Supervisor) |
| **Send API** | Runtime fan-out for parallel execution |
| **Reducers** | Merging state across parallel branches |
| **State Management** | Passing and accumulating data across nodes |

---

## 📊 Workflow Comparison Table

| Pattern | Decision Making | Parallel | Scalability | Complexity | Best Use Case |
|---|---|---|---|---|---|
| **Sequential** | ❌ None | ❌ No | 🟡 Low | 🟢 Low | Fixed, always-the-same pipelines |
| **Router** | ✅ Single decision | ❌ No | 🟢 High | 🟡 Medium | Intent-based dispatch to one worker |
| **Parallel** | 🟡 Task-splitting only | ✅ Yes | 🟢 High | 🟠 High | Independent sub-tasks, batch work |
| **Supervisor** | ✅ Repeated decisions | ❌ No (usually) | 🟡 Medium | 🔴 Highest | Open-ended, iterative, quality-gated tasks |

---

## 💡 What I Learned

Building the same three agents into four different graph topologies taught me far more than building four separate projects would have. A few things that really clicked:

**State Management** — In LangGraph, state isn't just "shared memory," it's a contract. Every node reads and writes to a `TypedDict`-defined schema, and the shape of that schema determines what's even possible in your graph (e.g., you can't merge parallel branches without a reducer defined on the right field).

**Conditional Routing** — Both the Router and Supervisor patterns rely on `add_conditional_edges`, but the *intent* is different: Router makes one decision and exits; Supervisor makes a decision, executes, and comes back to decide again.

**Reducers** — This was the trickiest concept. Without a reducer (e.g., `Annotated[list, operator.add]`), parallel branches from `Send` will silently clobber each other's state instead of merging. Understanding reducers is what separates "my parallel graph runs" from "my parallel graph runs correctly."

**Send** — The `Send` API decouples "how many parallel tasks" from "how the graph is defined." You don't need to know at graph-construction time how many branches there will be — `Send` lets that be a runtime decision based on the splitter's output.

**Supervisor / Orchestration** — A supervisor node is really just a router that runs in a loop. The mental shift is treating "what happens next" as a *repeated* decision rather than a one-time fork.

**Dynamic Workflows** — Sequential and Router are static shapes; Parallel and Supervisor are dynamic — the actual execution graph at runtime can look different from run to run.

**Task Decomposition** — Splitting is only useful if the sub-tasks are genuinely independent. Forcing decomposition on a task with hidden dependencies leads to worse (and harder to debug) results than just running sequentially.

**Feedback Loops** — The Supervisor pattern is the first one where the graph can "change its mind" — e.g., sending writer output back for revision. This is the seed of self-correcting agent behavior.

---

## 🔑 Key Takeaways

- **There is no single "best" agent architecture.** The right pattern depends on whether your task is fixed vs. dynamic, and whether sub-tasks are independent vs. sequential.
- **Reducers and state schema design matter as much as the graph shape.** Most bugs in multi-agent systems come from state merging issues, not from the LLM being "wrong."
- **Supervisors are powerful but expensive.** Reach for Router or Sequential first; only introduce a Supervisor loop when the task genuinely requires repeated, open-ended decision-making.
- **The same agents can be reused across very different architectures.** Good agent design (clear inputs/outputs) is what makes a system composable across patterns.

---

## 🚀 Future Improvements

- 🧠 **Memory** — persistent conversation/task memory across runs
- 🧑‍💻 **Human-in-the-loop** — approval gates using LangGraph's `interrupt_before` / `interrupt_after`
- 🔌 **MCP (Model Context Protocol)** — standardized tool/data access across agents
- 🪞 **Reflection** — agents that critique and revise their own output before finishing
- 🗺️ **Planning** — an explicit planning node that precedes execution (plan → act → observe)
- 🛠️ **Tool Calling** — giving agents real external tools (search, code execution, APIs)
- 🤝 **Multi-Agent Collaboration** — agents that negotiate or debate rather than just hand off
- 💾 **Persistence** — durable state storage across sessions
- ✅ **Checkpoints** — resumable graph execution using LangGraph checkpointers
- 🧵 **Long-term Memory** — vector-store-backed memory for cross-session context

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/habibullashaik/workflow-patterns-langgraph.git
cd workflow-patterns-langgraph

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Add your GROQ_API_KEY inside .env
```

---

## ▶️ Running Each Workflow

```bash
# Sequential Workflow
python sequential/app.py

# Router Workflow
python router/app.py

# Parallel Workflow
python parallelism/app.py

# Supervisor Workflow
python supervisor/app.py
```

Each script builds its graph, compiles it, runs a sample input, and exports a Mermaid diagram (`.png`) of the graph structure to the `diagrams/` folder.

---

## 🖼️ Screenshots

> _Add generated graph diagrams and sample run outputs below._

**Sequential Workflow Graph**
`[ screenshot placeholder ]`

**Router Workflow Graph**
`[ screenshot placeholder ]`

**Parallel Workflow Graph**
`[ screenshot placeholder ]`

**Supervisor Workflow Graph**
`[ screenshot placeholder ]`

---

## 🤝 Contributing

Contributions, issues, and suggestions are welcome! If you'd like to add a new workflow pattern (e.g., Reflection, Planning, or a hybrid pattern), please open an issue first to discuss the direction, then submit a PR.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-pattern`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — free to use, learn from, and build upon.

---

<p align="center"><i>Built as part of a hands-on journey into Agentic AI system design.</i></p>
