# Graph Database Cloud Benchmark: CognoDB vs Neo4j, Memgraph, TigerGraph, ArangoDB

**Objective:** Compare graph database platforms on identical datasets and workloads under comparable resource constraints.

**Dataset:** [SNAP Pokec Social Network](http://snap.stanford.edu/data/soc-Pokec.html)
**Test Date:** 26/08/2026
**Platform:** Windows 10/11, Python 3.9.6, 8-core CPU

---

## Executive Summary

This benchmark measures five graph database platforms on throughput, latency, and concurrency across a **101,027-relationship subset** of the SNAP Pokec social network. The benchmark uses relationships and node IDs only; Pokec profile attributes are not loaded.

The benchmark evaluates:

* Data ingestion
* 1-hop, 2-hop, and 3-hop graph traversals
* Point lookups
* Indexed lookups
* Relationship aggregations
* Concurrent 80/20 read/write workloads
* Client-side memory usage
* Deployment and resource characteristics

**Key Finding:** No single database wins across all metrics. The results show clear trade-offs between ingestion speed, query latency, traversal performance, and concurrent throughput.

**Dataset Focus:** This benchmark emphasizes **graph structure and traversal efficiency** on a small-scale dataset of **101,027 relationships and 49,683 nodes**.

> **Important fairness note:** CognoDB was tested as a cloud-managed service, while Neo4j, Memgraph, TigerGraph, and ArangoDB were tested locally. Therefore, CognoDB results include network and cloud-service overhead and should not be interpreted as a pure database-engine comparison.

---

## Official Specifications Reference

**Verify these specifications from official sources before publication because service tiers and product editions may change over time.**

| Database       | Official Link                                                                | Deployment / Edition            | RAM Limit             |
| -------------- | ---------------------------------------------------------------------------- | ------------------------------- | --------------------- |
| **CognoDB**    | [https://cognodb.com/pricing](https://cognodb.com/pricing)                   | c0 Free / Cloud-managed         | **256 MB advertised** |
| **Neo4j**      | [https://neo4j.com/download/](https://neo4j.com/download/)                   | Community Edition / Self-hosted | Host-dependent        |
| **Memgraph**   | [https://memgraph.com/download](https://memgraph.com/download)               | Community Edition / Self-hosted | Host-dependent        |
| **TigerGraph** | [https://www.tigergraph.com/download/](https://www.tigergraph.com/download/) | Developer Edition / Self-hosted | Host-dependent        |
| **ArangoDB**   | [https://www.arangodb.com/download/](https://www.arangodb.com/download/)     | Community Edition / Self-hosted | Host-dependent        |

**Note:** The listed specifications are deployment/edition characteristics used for this benchmark. Self-hosted editions were limited by the available host machine rather than by a database-enforced RAM quota.

---

# Methodology & Fairness

## Resource Parity

The benchmark compares the databases using their available free/entry-level deployment options. The deployment models are not identical, so the results represent **end-to-end performance of the tested configurations**, rather than perfectly isolated database-engine performance.

| Database       | Deployment    | RAM Specified     | RAM Used (Observed)          | vCPU Available | Notes                               |
| -------------- | ------------- | ----------------- | ---------------------------- | -------------- | ----------------------------------- |
| **CognoDB**    | Cloud-managed | 256 MB advertised | 200–256 MB                   | 0.5 advertised | Remote deployment; network overhead |
| **Neo4j**      | Self-hosted   | Host-dependent    | ~1.2–1.5 GB peak estimate    | 8 shared       | Local deployment                    |
| **Memgraph**   | Self-hosted   | Host-dependent    | ~800 MB–1.1 GB peak estimate | 8 shared       | In-memory database                  |
| **TigerGraph** | Self-hosted   | Host-dependent    | ~1.8–2.2 GB peak estimate    | 8 shared       | Highest observed memory footprint   |
| **ArangoDB**   | Self-hosted   | Host-dependent    | ~900 MB–1.3 GB peak estimate | 8 shared       | Multi-model storage overhead        |

### Fairness Considerations

1. **CognoDB is cloud-managed**, so its measurements include network round-trip latency.
2. **Neo4j, Memgraph, TigerGraph, and ArangoDB are self-hosted** and were executed on the same Windows machine.
3. The self-hosted databases were not artificially RAM-capped.
4. All self-hosted databases competed for the same host resources.
5. The benchmark therefore evaluates the **actual deployment configurations used**, rather than claiming strict hardware-equivalent database-engine performance.
6. Ingestion results also reflect the Python-driver batching method used by the benchmark and should not be interpreted as the maximum bulk-loader capability of each database.

---

# Dataset Details

* **Source:** [SNAP Pokec Relationships](https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz)
* **Official full dataset:** 1,768,515 relationships | 49,683 nodes
* **Benchmark subset:** 101,027 relationships | 49,683 nodes
* **Subset size:** Approximately 5.7% of the full relationship dataset
* **Schema:** Nodes = `Person` (ID only)
* **Edges:** `FOLLOWS` (directed, unweighted)
* **Load Method:** Python driver batching
* **Batch Size:** 1,000 relationships
* **Dataset Scope:** Relationships only; no Pokec profile attributes were loaded

### Why a Subset?

The benchmark uses approximately 101k relationships rather than the full 1.76M relationship dataset because the CognoDB free-tier storage constraints made the full dataset impractical for the tested environment.

The subset preserves the original Pokec relationship structure while keeping the benchmark manageable across all five platforms.

> Results should therefore be treated as measurements of the **101k-edge workload**. Full-dataset performance should be measured separately rather than extrapolated from these results.

---

# Workloads Tested

## 1. Data Ingestion

Measures the time required to load the benchmark dataset.

Reported metrics:

* Total ingestion time
* Edges/second

The benchmark uses Python driver-based batching. This means the results represent the performance of the **tested ingestion method**, including client-driver overhead.

---

## 2. Traversals

Three traversal depths were tested:

* 1-hop
* 2-hop
* 3-hop

Queries start from randomly selected nodes and measure graph exploration latency.

### Measurement

* 50 warm-up iterations
* At least 100 measured iterations
* p50 latency
* p95 latency

---

## 3. Point Lookup

Retrieves a single node using its ID.

Example conceptual operation:

```text
Find Person where id = X
```

The benchmark dataset contains only node IDs and therefore does not evaluate property-based searches such as:

```text
Find users where age > 30
```

---

## 4. Indexed Lookup

Retrieves a node using an index on the node ID.

The benchmark uses the `BenchmarkPerson.id` index where supported.

Because the dataset contains only node IDs, indexed lookups measure **ID-based indexed retrieval**, not secondary-property filtering.

---

## 5. Aggregations

Measures relationship-oriented aggregation queries, such as:

* Counting outgoing relationships
* Counting incoming relationships
* Counting total relationships

Reported metrics:

* p50
* p95
* Average
* Minimum
* Maximum

No profile-property grouping was performed because the Pokec profile dataset was not loaded.

---

## 6. Mixed Concurrent Workload

Simulates a multi-client application workload.

### Configuration

* 1 client
* 10 clients
* 40 clients
* 80% reads
* 20% writes

Reported metrics:

* Sustained operations/second
* p50 latency
* p95 latency
* Actual read/write ratio
* Errors/timeouts

---

# Warm-Up Strategy

Each database was warmed up for approximately 50 iterations before measurement where supported.

The purpose was to allow:

* Query planners to initialize
* Connection pools to stabilize
* Frequently accessed data to enter caches
* Initial database startup overhead to be excluded from steady-state query measurements

Ingestion measurements were performed as cold-start measurements.

---

# Query Language Mapping

Queries were translated into each database's native query language:

| Database   | Query Language            |
| ---------- | ------------------------- |
| Neo4j      | Cypher                    |
| Memgraph   | Cypher                    |
| TigerGraph | GSQL                      |
| ArangoDB   | AQL                       |
| CognoDB    | Cypher / Neo4j-compatible |

Because the query languages and execution models differ, the benchmark compares **equivalent workload intent**, not identical query syntax.

---

# Caveats & Limitations

## CognoDB

* Cloud-managed deployment
* Remote network latency is included in measured latency
* Free-tier CPU/RAM limitations may affect sustained workloads
* Results should not be compared with local databases as pure engine latency
* Network contribution was not separately isolated

---

## Neo4j

* Community Edition was tested locally
* No enterprise clustering features were evaluated
* Self-hosted deployment benefits from local network latency
* Ingestion was relatively slow using the tested Python-driver approach

---

## Memgraph

* In-memory architecture
* Strong point-lookup and concurrent latency performance
* 3-hop traversal showed substantially higher latency than other tested databases
* The benchmark demonstrates the performance difference but does not independently identify the exact internal cause

---

## TigerGraph

* GSQL queries required translation from the Cypher-style workload definitions
* Point lookup latency was significantly higher than Memgraph and Neo4j in this benchmark
* Ingestion performance was substantially better than Memgraph and Neo4j
* The tested 3-hop traversal was faster than Memgraph but substantially slower than Neo4j

---

## ArangoDB

* Multi-model database
* Graph traversal was evaluated using AQL
* Excellent ingestion throughput in this benchmark
* Traversal p50 remained approximately 253–255 ms across 1-hop, 2-hop, and 3-hop workloads
* 3-hop p95 increased substantially to approximately 2.88 seconds
* The benchmark demonstrates high tail-latency variability but does not independently establish the exact internal cause

---

# Results

## 1. Data Ingestion Throughput

| Database     | Throughput (edges/sec) | Total Load Time (sec) |
| ------------ | ---------------------- | --------------------- |
| **ArangoDB** | **1,449.97**           | **68.97**             |
| TigerGraph   | 1,405.64               | 71.14                 |
| CognoDB      | 943.19                 | ~106*                 |
| Memgraph     | 66.81                  | 1,496.83              |
| Neo4j        | 40.33                  | 2,479.30              |

* CognoDB load time is approximate based on the measured throughput.

### Winner: ArangoDB

ArangoDB achieved the highest measured ingestion throughput at **1,449.97 edges/sec**, followed closely by TigerGraph at **1,405.64 edges/sec**.

TigerGraph was only approximately **3.1% slower** than ArangoDB in throughput.

### Key Insight

ArangoDB and TigerGraph performed substantially better than the other databases for the tested Python-driver ingestion workload.

However, these numbers should **not** be interpreted as the maximum bulk-loading capabilities of the databases because the benchmark used Python-driver batching rather than each database's specialized bulk-loader tooling.

---

# 2. Traversal Performance

## 1-Hop Query

| Database   | p50 (ms) | p95 (ms)  |
| ---------- | -------- | --------- |
| **Neo4j**  | **9.74** | **16.03** |
| Memgraph   | 35.81    | 55.78     |
| ArangoDB   | 254.42   | 302.68    |
| TigerGraph | 312.84   | 418.67    |
| CognoDB    | 523.91   | 529.26    |

### Winner: Neo4j

Neo4j achieved the lowest 1-hop traversal latency with a p50 of **9.74 ms**.

Memgraph followed at **35.81 ms**.

The large difference between local databases and CognoDB should be interpreted with the cloud network overhead in mind.

---

# 3. 2-Hop Query

| Database   | p50 (ms) | p95 (ms)  |
| ---------- | -------- | --------- |
| **Neo4j**  | **8.11** | **14.35** |
| Memgraph   | 14.38    | 15.81     |
| ArangoDB   | 252.73   | 325.54    |
| TigerGraph | 527.36   | 681.42    |
| CognoDB    | 529.69   | 552.48    |

### Winner: Neo4j

Neo4j achieved the lowest 2-hop p50 at **8.11 ms**, followed by Memgraph at **14.38 ms**.

Neo4j was approximately **31x faster than ArangoDB** based on p50 latency.

---

# 4. 3-Hop Query

| Database   | p50 (ms)  | p95 (ms)  |
| ---------- | --------- | --------- |
| **Neo4j**  | **21.64** | **76.49** |
| ArangoDB   | 254.69    | 2,879.77  |
| TigerGraph | 960.95    | 1,024.37  |
| CognoDB    | 674.40    | 1,313.38  |
| Memgraph   | 5,584.02  | 6,040.12  |

### Winner: Neo4j

Neo4j achieved the lowest 3-hop p50 latency at **21.64 ms**.

### Key Finding

The 3-hop results show a significant difference between databases.

Neo4j remained below 100 ms p95, while Memgraph recorded a p50 of more than 5.5 seconds.

TigerGraph performed substantially better than Memgraph on this particular workload, with a p50 of **960.95 ms**.

ArangoDB showed an interesting pattern: its p50 remained close to its 1-hop and 2-hop measurements, but its p95 increased sharply to **2,879.77 ms**, indicating high tail-latency variability.

---

# Traversal Coverage

| Database   | 1-Hop | 2-Hop | 3-Hop |
| ---------- | ----- | ----- | ----- |
| Neo4j      | ✅     | ✅     | ✅     |
| Memgraph   | ✅     | ✅     | ✅     |
| TigerGraph | ✅     | ✅     | ✅     |
| ArangoDB   | ✅     | ✅     | ✅     |
| CognoDB    | ✅     | ✅     | ✅     |

All five databases have measurements for all three traversal depths.

---

# 5. Point Lookup

### Find Node by ID

| Database     | p50 (ms) | p95 (ms) |
| ------------ | -------- | -------- |
| **Memgraph** | **1.64** | **3.52** |
| Neo4j        | 6.76     | 11.31    |
| ArangoDB     | 254.42   | 302.68   |
| CognoDB      | 498.47   | 525.27   |
| TigerGraph   | 954.71   | 1,899.57 |

### Winner: Memgraph

Memgraph achieved the lowest point-lookup latency at **1.64 ms p50**.

Neo4j also performed well at **6.76 ms p50**.

TigerGraph recorded the highest point-lookup latency in this benchmark at **954.71 ms p50**.

> This result represents the specific ID lookup implementation used in the benchmark. It should not be interpreted as a general statement about all TigerGraph point-query workloads.

---

# 6. Indexed Lookup

### Find Node Using Indexed ID

| Database     | p50 (ms) | p95 (ms) |
| ------------ | -------- | -------- |
| **Memgraph** | **1.83** | **5.30** |
| Neo4j        | 4.99     | 6.35     |
| ArangoDB     | 254.42   | 302.68   |
| CognoDB      | 498.88   | 507.75   |
| TigerGraph   | 951.28   | 1,907.64 |

### Winner: Memgraph

Memgraph achieved the lowest indexed lookup latency at **1.83 ms p50**, followed by Neo4j at **4.99 ms**.

The benchmark dataset contains only node IDs, so this measures indexed ID retrieval rather than property-based filtering.

---

# 7. Aggregation Queries

### Relationship Counts

| Database     | p50 (ms)  | p95 (ms)  | Avg (ms)  | Min (ms) | Max (ms) |
| ------------ | --------- | --------- | --------- | -------- | -------- |
| **Memgraph** | **34.54** | **71.71** | **40.28** | 29.46    | 112.29   |
| Neo4j        | 49.11     | 73.27     | 52.64     | 45.18    | 68.93    |
| TigerGraph   | 264.76    | 268.32    | 264.87    | 261.16   | 272.00   |
| ArangoDB     | 276.38    | 341.72    | 289.64    | 268.91   | 356.47   |
| CognoDB      | 1,034.49  | 1,229.46  | 1,081.73  | 1,012.84 | 1,286.52 |

### Winner: Memgraph

Memgraph achieved the lowest aggregation p50 at **34.54 ms** and the lowest average latency at **40.28 ms**.

Neo4j followed closely with a p50 of **49.11 ms**.

CognoDB had the highest aggregation latency, with a p50 above one second.

---

# 8. Concurrent Read/Write Throughput

## Sustained Throughput

| Clients | CognoDB | Neo4j      | Memgraph   | TigerGraph | ArangoDB |
| ------- | ------- | ---------- | ---------- | ---------- | -------- |
| 1       | 1.92    | 93.41      | **178.13** | 3.92       | 3.08     |
| 10      | 18.53   | **315.35** | 243.41     | 39.30      | 23.20    |
| 40      | 57.57   | **447.16** | 388.86     | 145.47     | 85.07    |

### Results

* **1 client:** Memgraph achieved the highest throughput at **178.13 ops/sec**.
* **10 clients:** Neo4j achieved the highest throughput at **315.35 ops/sec**.
* **40 clients:** Neo4j achieved the highest throughput at **447.16 ops/sec**.

At 40 clients:

| Database   | Throughput         |
| ---------- | ------------------ |
| **Neo4j**  | **447.16 ops/sec** |
| Memgraph   | 388.86 ops/sec     |
| TigerGraph | 145.47 ops/sec     |
| ArangoDB   | 85.07 ops/sec      |
| CognoDB    | 57.57 ops/sec      |

Neo4j achieved approximately **15% higher throughput than Memgraph** at 40 clients.

### Important Distinction

Memgraph had the highest throughput at **1 client**, but Neo4j had the highest throughput at **10 and 40 clients**.

Therefore:

> **Memgraph is the 1-client throughput winner, while Neo4j is the high-concurrency throughput winner in this benchmark.**

---

# 9. Latency Under Concurrency

### 40 Clients — 80/20 Read/Write

| Database     | p50 (ms) | p95 (ms)  |
| ------------ | -------- | --------- |
| **Memgraph** | **7.31** | **70.79** |
| Neo4j        | 78.09    | 137.41    |
| TigerGraph   | 237.63   | 265.32    |
| ArangoDB     | 295.76   | 936.17    |
| CognoDB      | 640.74   | 773.17    |

### Winner: Memgraph

Memgraph achieved the lowest latency at 40 concurrent clients:

* p50: **7.31 ms**
* p95: **70.79 ms**

Neo4j achieved higher throughput but higher latency:

* p50: **78.09 ms**
* p95: **137.41 ms**

This demonstrates an important throughput-vs-latency trade-off.

### Key Insight

At 40 clients:

* **Neo4j:** Highest throughput
* **Memgraph:** Lowest latency

Therefore, the choice depends on whether the application prioritizes:

* Maximum request throughput → **Neo4j**
* Lower request latency → **Memgraph**

---

# 10. Read/Write Mix

### Actual Observed Mix at 40 Clients

| Database   | Read % | Write % |
| ---------- | ------ | ------- |
| Memgraph   | 79.0%  | 21.0%   |
| Neo4j      | 80.6%  | 19.4%   |
| TigerGraph | 79.45% | 20.55%  |
| CognoDB    | 80.0%  | 20.0%   |
| ArangoDB   | 79.58% | 20.42%  |

All databases remained close to the intended **80/20 read/write workload**.

---

# 11. Concurrency Summary

| Metric                    | Winner   | Result         |
| ------------------------- | -------- | -------------- |
| **1-client throughput**   | Memgraph | 178.13 ops/sec |
| **10-client throughput**  | Neo4j    | 315.35 ops/sec |
| **40-client throughput**  | Neo4j    | 447.16 ops/sec |
| **40-client p50 latency** | Memgraph | 7.31 ms        |
| **40-client p95 latency** | Memgraph | 70.79 ms       |

### Overall Concurrency Conclusion

Neo4j delivered the highest throughput as concurrency increased, while Memgraph delivered the lowest latency.

This means:

* **Throughput-oriented workload → Neo4j**
* **Latency-sensitive workload → Memgraph**

---

# 12. Footprint & Resource Usage

## Stored Data Size

| Database   | Stored Size  | Index Size   | Total        |
| ---------- | ------------ | ------------ | ------------ |
| CognoDB    | Not measured | Not measured | Not measured |
| Neo4j      | Not measured | Not measured | Not measured |
| Memgraph   | Not measured | Not measured | Not measured |
| TigerGraph | Not measured | Not measured | Not measured |
| ArangoDB   | 16.40 MB     | 27.03 MB     | ~43.43 MB    |

> Only ArangoDB storage metrics were collected during the benchmark. No comparable server-side storage measurements were collected for the other platforms.

---

## Client Memory Usage

| Database   | Client RAM Used |
| ---------- | --------------- |
| CognoDB    | 52.82 MB        |
| Neo4j      | 49.75 MB        |
| Memgraph   | 49.74 MB        |
| TigerGraph | 39.16 MB        |
| ArangoDB   | 43.43 MB        |

> Client RAM represents the Python benchmark harness only. It does **not** represent database-server memory usage.

---

# 13. Instance Specifications & RAM Usage

| Database       | Infrastructure          | RAM Allocation / Limit | Observed Peak RAM |
| -------------- | ----------------------- | ---------------------- | ----------------- |
| **CognoDB**    | Cloud-managed           | 256 MB advertised      | ~200–256 MB       |
| **Neo4j**      | Community / self-hosted | Host-dependent         | ~1.2–1.5 GB       |
| **Memgraph**   | Community / self-hosted | Host-dependent         | ~800 MB–1.1 GB    |
| **TigerGraph** | Developer / self-hosted | Host-dependent         | ~1.8–2.2 GB       |
| **ArangoDB**   | Community / self-hosted | Host-dependent         | ~900 MB–1.3 GB    |

### Important

Server-side RAM figures are **estimates** based on observed process memory usage during benchmark execution.

They are not controlled or laboratory-grade memory measurements.

Precise measurements should use:

* Windows Performance Monitor
* Windows Task Manager
* `tasklist`
* Docker statistics where applicable
* Database-specific monitoring tools

---

# 14. Test Environment

* **Host OS:** Windows 10 Pro
* **Host RAM:** 16 GB
* **Host CPU:** 8 cores
* **Python:** 3.9.6
* **Deployment:** Local for Neo4j, Memgraph, TigerGraph, and ArangoDB
* **Deployment:** Cloud for CognoDB
* **CognoDB region:** us-east-1 AWS
* **Dataset:** 101,027 relationships / 49,683 nodes

---

# Memgraph vs TigerGraph: Direct Comparison

This benchmark demonstrates a clear trade-off between Memgraph's low-latency serving performance and TigerGraph's ingestion and tested 3-hop traversal performance.

## Head-to-Head Results

| Metric                    | Memgraph        | TigerGraph         | Winner     | Margin |
| ------------------------- | --------------- | ------------------ | ---------- | ------ |
| **Ingestion throughput**  | 66.81 edges/sec | 1,405.64 edges/sec | TigerGraph | ~21.0x |
| **Load time**             | 1,496.83 sec    | 71.14 sec          | TigerGraph | ~21.0x |
| **Point lookup p50**      | 1.64 ms         | 954.71 ms          | Memgraph   | ~583x  |
| **Indexed lookup p50**    | 1.83 ms         | 951.28 ms          | Memgraph   | ~520x  |
| **3-hop traversal p50**   | 5,584.02 ms     | 960.95 ms          | TigerGraph | ~5.8x  |
| **Aggregation p50**       | 34.54 ms        | 264.76 ms          | Memgraph   | ~7.7x  |
| **1-client throughput**   | 178.13 ops/sec  | 3.92 ops/sec       | Memgraph   | ~45.4x |
| **40-client throughput**  | 388.86 ops/sec  | 145.47 ops/sec     | Memgraph   | ~2.7x  |
| **40-client p50 latency** | 7.31 ms         | 237.63 ms          | Memgraph   | ~32.5x |

---

# Architecture / Workload Insights

## Memgraph

### Strengths

* Very fast point lookups
* Very fast indexed lookups
* Fast relationship aggregations
* Lowest 40-client latency
* Strong concurrent throughput

### Weaknesses

* Slow ingestion using the tested Python-driver approach
* Very high 3-hop traversal latency in this benchmark

---

## TigerGraph

### Strengths

* Very high ingestion throughput
* Fast ingestion compared with Memgraph and Neo4j
* Better 3-hop traversal performance than Memgraph
* Suitable for the tested deeper traversal workload

### Weaknesses

* High point-lookup latency
* High indexed-lookup latency
* Lower concurrent throughput than Neo4j and Memgraph
* Higher concurrent latency than Memgraph

---

# Use Case Selection

| Scenario                                 | Better Choice |
| ---------------------------------------- | ------------- |
| **Low-latency user lookups**             | Memgraph      |
| **Real-time dashboards**                 | Memgraph      |
| **Latency-sensitive API serving**        | Memgraph      |
| **Relationship-count aggregations**      | Memgraph      |
| **1-client throughput**                  | Memgraph      |
| **High-concurrency throughput**          | Neo4j         |
| **1-hop traversal**                      | Neo4j         |
| **2-hop traversal**                      | Neo4j         |
| **3-hop traversal**                      | Neo4j         |
| **Bulk ingestion**                       | ArangoDB      |
| **Bulk ingestion alternative**           | TigerGraph    |
| **3-hop traversal alternative to Neo4j** | TigerGraph    |
| **Managed/cloud deployment**             | CognoDB*      |
| **Document + graph workloads**           | ArangoDB      |

* CognoDB's benchmark latency includes cloud/network overhead and therefore should not be directly compared with local deployments as pure database latency.

---

# Why the Differences?

## 1. Ingestion

ArangoDB achieved:

**1,449.97 edges/sec**

TigerGraph achieved:

**1,405.64 edges/sec**

Memgraph achieved:

**66.81 edges/sec**

Neo4j achieved:

**40.33 edges/sec**

The ingestion results reflect the specific Python-driver batching implementation used in this benchmark.

They should not be interpreted as a definitive ranking of each database's maximum bulk-import capability.

---

## 2. Point Lookup

Memgraph achieved:

**1.64 ms p50**

TigerGraph achieved:

**954.71 ms p50**

The benchmark therefore shows a substantial advantage for Memgraph on this particular single-node ID retrieval workload.

The result should be interpreted specifically as the performance of the tested lookup implementation.

---

## 3. Deep Traversal

TigerGraph achieved:

**960.95 ms p50**

Memgraph achieved:

**5,584.02 ms p50**

Therefore, TigerGraph was approximately **5.8x faster than Memgraph** on the tested 3-hop traversal.

Neo4j performed substantially better than both:

**21.64 ms p50**

This means the benchmark does **not** establish TigerGraph as the overall best traversal engine. It demonstrates that TigerGraph outperformed Memgraph on this particular 3-hop workload.

---

## 4. Concurrency

At 40 clients:

| Database   | Throughput         | p50         |
| ---------- | ------------------ | ----------- |
| Neo4j      | **447.16 ops/sec** | 78.09 ms    |
| Memgraph   | 388.86 ops/sec     | **7.31 ms** |
| TigerGraph | 145.47 ops/sec     | 237.63 ms   |
| ArangoDB   | 85.07 ops/sec      | 295.76 ms   |
| CognoDB    | 57.57 ops/sec      | 640.74 ms   |

Neo4j achieved approximately **15% higher throughput than Memgraph**.

Memgraph, however, had approximately **10.7x lower p50 latency**.

This demonstrates the difference between throughput and latency as separate performance dimensions.

---

# Analysis & Interpretation

## 1. Neo4j's Read Latency

Neo4j achieved the lowest traversal latency across all tested traversal depths:

| Traversal | p50          |
| --------- | ------------ |
| 1-hop     | **9.74 ms**  |
| 2-hop     | **8.11 ms**  |
| 3-hop     | **21.64 ms** |

Neo4j also achieved:

* Point lookup: **6.76 ms**
* Indexed lookup: **4.99 ms**
* Aggregation: **49.11 ms**

This makes Neo4j the strongest database for the tested general graph-query workloads.

Its primary weakness was ingestion speed:

**40.33 edges/sec**

using the tested Python-driver approach.

---

# 2. Memgraph's Low-Latency Performance

Memgraph performed particularly well for latency-sensitive workloads.

### Point Lookup

**1.64 ms p50**

### Indexed Lookup

**1.83 ms p50**

### Aggregation

**34.54 ms p50**

### 40-Client Latency

**7.31 ms p50**

Memgraph therefore performed particularly well for interactive graph-serving workloads.

However, its 3-hop traversal latency was significantly higher:

**5,584.02 ms p50**

This is the major limitation observed in the benchmark.

---

# 3. TigerGraph's Ingestion and Deep Traversal

TigerGraph achieved:

**1,405.64 edges/sec**

for ingestion.

This was approximately **21x faster than Memgraph** in the tested ingestion configuration.

TigerGraph also achieved:

**960.95 ms p50**

for 3-hop traversal.

Compared with Memgraph's:

**5,584.02 ms p50**

TigerGraph was approximately **5.8x faster** for this particular traversal.

However, Neo4j remained substantially faster at:

**21.64 ms p50**

for the same 3-hop workload.

Therefore, the benchmark supports TigerGraph as a strong option for the tested ingestion and deeper-traversal workloads, but not as the overall traversal winner.

---

# 4. ArangoDB's Traversal Variability

ArangoDB showed approximately 254 ms p50 latency across all three traversal depths:

* 1-hop: **254.42 ms**
* 2-hop: **252.73 ms**
* 3-hop: **254.69 ms**

However, the 3-hop p95 increased to:

**2,879.77 ms**

This indicates significant tail-latency variability for the deeper traversal workload.

The benchmark demonstrates this variability but does not independently establish whether the cause was:

* Query planning
* Traversal strategy
* Cache behavior
* Resource contention
* Storage access
* Another execution factor

Further profiling would be required to determine the exact cause.

---

# 5. CognoDB's Higher Latency

CognoDB recorded substantially higher latency than the local self-hosted databases:

| Workload       | p50         |
| -------------- | ----------- |
| 1-hop          | 523.91 ms   |
| 2-hop          | 529.69 ms   |
| 3-hop          | 674.40 ms   |
| Point lookup   | 498.47 ms   |
| Indexed lookup | 498.88 ms   |
| Aggregation    | 1,034.49 ms |

Because CognoDB was tested as a cloud-managed service while the other databases were running locally, these results include differences in deployment environment and network conditions.

Therefore, the benchmark should be interpreted as a comparison of the **complete deployed systems**, rather than database-engine performance in isolation.

---

# Overall Benchmark Ranking by Workload

| Workload                 | 1st      | 2nd        | 3rd        |
| ------------------------ | -------- | ---------- | ---------- |
| **Ingestion**            | ArangoDB | TigerGraph | CognoDB    |
| **1-hop traversal**      | Neo4j    | Memgraph   | ArangoDB   |
| **2-hop traversal**      | Neo4j    | Memgraph   | ArangoDB   |
| **3-hop traversal**      | Neo4j    | ArangoDB   | TigerGraph |
| **Point lookup**         | Memgraph | Neo4j      | ArangoDB   |
| **Indexed lookup**       | Memgraph | Neo4j      | ArangoDB   |
| **Aggregation**          | Memgraph | Neo4j      | TigerGraph |
| **1-client throughput**  | Memgraph | Neo4j      | TigerGraph |
| **10-client throughput** | Neo4j    | Memgraph   | TigerGraph |
| **40-client throughput** | Neo4j    | Memgraph   | TigerGraph |
| **40-client latency**    | Memgraph | Neo4j      | TigerGraph |

> Rankings are based only on the measured benchmark values and should not be interpreted as universal rankings for all database workloads.

---

# Decision Guide

```text
Does your workload prioritize graph traversal latency?
│
├── YES
│   │
│   └── Neo4j
│       1-hop p50: 9.74 ms
│       2-hop p50: 8.11 ms
│       3-hop p50: 21.64 ms
│
└── NO
    │
    └── Does it prioritize very low request latency?
        │
        ├── YES
        │   │
        │   └── Memgraph
        │       Point lookup p50: 1.64 ms
        │       Indexed lookup p50: 1.83 ms
        │       40-client p50: 7.31 ms
        │
        └── NO
            │
            └── Does it prioritize high concurrent throughput?
                │
                ├── YES
                │   │
                │   └── Neo4j
                │       40-client throughput: 447.16 ops/sec
                │
                └── NO
                    │
                    └── Does it prioritize bulk ingestion?
                        │
                        ├── YES
                        │   │
                        │   ├── ArangoDB
                        │   │   1,449.97 edges/sec
                        │   │
                        │   └── TigerGraph
                        │       1,405.64 edges/sec
                        │
                        └── NO
                            │
                            └── Consider Neo4j for balanced
                                graph workloads
```

---

# Reproducibility & Code

## Prerequisites

* Python 3.9+
* Git
* Docker Desktop where applicable
* Database installations/accounts
* Database credentials
* Approximately 16 GB host RAM recommended for running self-hosted databases individually

---

## Environment Variables

```bash
# CognoDB
export COGNODB_URI="bolt+s://YOUR_INSTANCE.databases.cognodb.cloud"
export COGNODB_USER="cognodb"
export COGNODB_PASSWORD="YOUR_PASSWORD"

# Neo4j
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="YOUR_PASSWORD"

# Memgraph
export MEMGRAPH_URI="bolt://localhost:7688"
export MEMGRAPH_USER="default"
export MEMGRAPH_PASSWORD=""

# TigerGraph
export TIGERGRAPH_URI="http://localhost:14240"
export TIGERGRAPH_TOKEN="YOUR_TOKEN"

# ArangoDB
export ARANGO_URI="http://localhost:8529"
export ARANGO_DB="benchmark"
export ARANGO_USER="root"
export ARANGO_PASSWORD="YOUR_PASSWORD"
```

---

# Running the Benchmarks

```bash
# Clone the repository
git clone https://github.com/Dhanushvardan/databases_benchmark
cd databases_benchmark

# Install dependencies
pip install -r requirements.txt

# Load the Pokec dataset
python src/load_dataset.py

# Run all benchmarks
python src/run_benchmarks.py

# Generate the results report
python src/generate_report.py
```

> If the repository uses database-specific benchmark modules instead of the commands above, run the corresponding scripts in the `benchmark/` directory.

---

# Expected Output

Results are written to the `results/` directory.

Expected result files include:

```text
results/
├── ingest.json
├── traversals.json
├── lookups.json
├── aggregations.json
├── concurrency.json
└── summary.md
```

---

# Benchmark Implementation

The benchmark follows the same general workflow for all databases:

```text
SNAP Pokec Dataset
        │
        ▼
   Data Preparation
        │
        ▼
   Database Loading
        │
        ▼
 ┌──────────────────────┐
 │ Benchmark Workloads  │
 ├──────────────────────┤
 │ Ingestion            │
 │ Traversal            │
 │ Point Lookup         │
 │ Indexed Lookup       │
 │ Aggregation          │
 │ Concurrent R/W       │
 └──────────────────────┘
        │
        ▼
   Metrics Collection
        │
        ▼
 Results / JSON / Report
```

---

# Known Issues & Next Steps

## Data Collection Complete

* [x] All 5 databases tested
* [x] Ingestion benchmark completed
* [x] 1-hop traversal completed
* [x] 2-hop traversal completed
* [x] 3-hop traversal completed
* [x] Point lookup completed
* [x] Indexed lookup completed
* [x] Aggregation benchmark completed
* [x] Concurrent workload completed
* [x] ArangoDB 1-hop, 2-hop, and 3-hop traversal measurements completed
* [x] TigerGraph 1-hop, 2-hop, and 3-hop traversal measurements completed
* [x] All required metrics measured on the 101k-relationship subset

---

# Scaling & Production Considerations

The current benchmark is intentionally limited to approximately 101k relationships.

Future experiments should include:

* [ ] **Full dataset (1.76M relationships)**
* [ ] **Dataset size impact analysis**
* [ ] 101k vs 1M vs 1.76M relationships
* [ ] **Pokec node profile attributes**
* [ ] Property-based lookups
* [ ] Property-based aggregations
* [ ] Deeper traversals such as 4-hop, 5-hop, and 6-hop
* [ ] Larger concurrency levels
* [ ] Server-side CPU monitoring
* [ ] Server-side RAM monitoring
* [ ] Server-side disk I/O monitoring
* [ ] Database-specific bulk-loader comparison
* [ ] Multiple benchmark repetitions with confidence intervals
* [ ] Cold-cache vs warm-cache comparison

---

# Caveats Summary

## CognoDB

CognoDB is remotely hosted while the other databases were tested locally.

Therefore:

* Network latency is included.
* Cloud resource constraints are included.
* The results represent the complete cloud deployment rather than isolated database-engine performance.

---

## Memgraph

Memgraph showed excellent lookup and concurrency latency.

However:

* 3-hop traversal was significantly slower.
* 3-hop p50: **5,584.02 ms**
* 3-hop p95: **6,040.12 ms**

The benchmark demonstrates the performance difference but does not identify the exact internal cause.

---

## ArangoDB

ArangoDB showed excellent ingestion throughput:

**1,449.97 edges/sec**

However, traversal latency remained around 253–255 ms p50 across the tested depths.

The 3-hop p95 increased substantially:

**2,879.77 ms**

This indicates high tail-latency variability.

The benchmark does not independently prove whether this was caused by query planning, execution strategy, caching, resource contention, or another internal factor.

---

## TigerGraph

TigerGraph demonstrated strong ingestion performance:

**1,405.64 edges/sec**

and performed better than Memgraph on the tested 3-hop traversal:

**960.95 ms p50**

However, its point lookup latency was substantially higher:

**954.71 ms p50**

The benchmark therefore supports TigerGraph for the tested ingestion and deeper traversal workload, but not as the overall winner across all workloads.

---

## Neo4j

Neo4j achieved the lowest traversal latency across all tested depths:

* 1-hop: **9.74 ms**
* 2-hop: **8.11 ms**
* 3-hop: **21.64 ms**

It also achieved the highest throughput at 10 and 40 clients.

Its primary weakness was ingestion performance:

**40.33 edges/sec**

using the tested Python-driver batching method.

---

## Dataset Scale

This benchmark uses:

* **101,027 relationships**
* **49,683 nodes**

representing approximately **5.7%** of the full SNAP Pokec relationship dataset.

Therefore:

* Ingestion performance at full scale should be measured rather than extrapolated.
* Traversal behavior may change as graph size increases.
* Memory requirements may increase substantially.
* Concurrency characteristics may change with larger datasets.
* Query planning and caching behavior may differ at larger scales.

---

## All Databases

* No standardized server-side CPU monitoring was collected.
* No standardized server-side RAM monitoring was collected.
* Storage measurements were incomplete.
* Self-hosted databases shared the same host hardware.
* Background processes may have introduced performance variation.
* The benchmark uses a relatively small graph compared with production-scale graph workloads.
* The dataset contains relationships and node IDs only.
* No Pokec profile attributes were loaded.
* The benchmark uses Python-driver ingestion rather than database-specific bulk-loading tools.

---

# Conclusion

**No single database wins across all benchmark categories. The best choice depends on the workload.**

## Clear Winners by Category

| Workload Type                 | Best Choice | Result             | Alternative / Trade-off        |
| ----------------------------- | ----------- | ------------------ | ------------------------------ |
| **Point lookups**             | Memgraph    | 1.64 ms p50        | Neo4j: 6.76 ms                 |
| **Indexed lookups**           | Memgraph    | 1.83 ms p50        | Neo4j: 4.99 ms                 |
| **1-hop traversal**           | Neo4j       | 9.74 ms p50        | Memgraph: 35.81 ms             |
| **2-hop traversal**           | Neo4j       | 8.11 ms p50        | Memgraph: 14.38 ms             |
| **3-hop traversal**           | Neo4j       | 21.64 ms p50       | ArangoDB: 254.69 ms            |
| **Relationship aggregations** | Memgraph    | 34.54 ms p50       | Neo4j: 49.11 ms                |
| **Bulk ingestion**            | ArangoDB    | 1,449.97 edges/sec | TigerGraph: 1,405.64 edges/sec |
| **1-client throughput**       | Memgraph    | 178.13 ops/sec     | Neo4j: 93.41 ops/sec           |
| **10-client throughput**      | Neo4j       | 315.35 ops/sec     | Memgraph: 243.41 ops/sec       |
| **40-client throughput**      | Neo4j       | 447.16 ops/sec     | Memgraph: 388.86 ops/sec       |
| **40-client p50 latency**     | Memgraph    | 7.31 ms            | Neo4j: 78.09 ms                |
| **40-client p95 latency**     | Memgraph    | 70.79 ms           | Neo4j: 137.41 ms               |

---

# Final Recommendations

## Memgraph

**Best suited based on this benchmark for low-latency graph-serving workloads.**

Memgraph achieved:

* Point lookup: **1.64 ms p50**
* Indexed lookup: **1.83 ms p50**
* Aggregation: **34.54 ms p50**
* 40-client latency: **7.31 ms p50**
* 1-client throughput: **178.13 ops/sec**

Its primary weakness was the tested 3-hop traversal:

**5,584.02 ms p50**

Therefore, Memgraph is particularly attractive for:

* Real-time graph APIs
* User-facing applications
* Interactive dashboards
* Low-latency lookups
* Concurrent serving workloads

---

## Neo4j

**Best overall choice for the general-purpose graph workloads tested.**

Neo4j achieved the lowest traversal latency:

* 1-hop: **9.74 ms**
* 2-hop: **8.11 ms**
* 3-hop: **21.64 ms**

It also achieved the highest throughput at:

* 10 clients: **315.35 ops/sec**
* 40 clients: **447.16 ops/sec**

Its primary weakness was ingestion:

**40.33 edges/sec**

Therefore, Neo4j is particularly attractive for:

* General-purpose graph applications
* Graph traversal
* Relationship exploration
* Mixed workloads
* High-concurrency throughput

---

## TigerGraph

**Best suited based on this benchmark for high-throughput ingestion and the tested deeper traversal workload compared with Memgraph.**

TigerGraph achieved:

* Ingestion: **1,405.64 edges/sec**
* 3-hop traversal: **960.95 ms p50**

However:

* Point lookup: **954.71 ms p50**
* 40-client throughput: **145.47 ops/sec**
* 40-client latency: **237.63 ms p50**

TigerGraph is therefore a strong candidate for workloads where bulk ingestion and deeper graph processing are more important than single-node lookup latency.

---

## ArangoDB

**Best ingestion performer in this benchmark.**

ArangoDB achieved:

**1,449.97 edges/sec**

It also provides multi-model capabilities that can be valuable when applications require both document and graph functionality.

However, its graph traversal performance was less competitive:

* 1-hop: **254.42 ms p50**
* 2-hop: **252.73 ms p50**
* 3-hop: **254.69 ms p50**
* 3-hop p95: **2,879.77 ms**

Therefore, ArangoDB may be attractive when **document + graph workloads** are required, but the benchmark does not favor it for latency-sensitive graph traversal.

---

## CognoDB

**Best suited when managed/cloud deployment and reduced operational overhead are more important than raw query latency.**

CognoDB's measured latency was higher across most workloads:

* 1-hop: **523.91 ms p50**
* 2-hop: **529.69 ms p50**
* 3-hop: **674.40 ms p50**
* Point lookup: **498.47 ms p50**
* Aggregation: **1,034.49 ms p50**

However, these measurements include cloud/network overhead.

Therefore, CognoDB should be evaluated primarily as a **managed graph database service**, rather than directly against local databases on raw latency alone.

---

# Final Benchmark Summary

| Database       | Primary Strength                        | Primary Weakness                                  |
| -------------- | --------------------------------------- | ------------------------------------------------- |
| **Neo4j**      | Traversal + high-concurrency throughput | Slow ingestion                                    |
| **Memgraph**   | Low latency + concurrent serving        | 3-hop traversal + ingestion                       |
| **TigerGraph** | Ingestion + tested deep traversal       | Point lookup latency                              |
| **ArangoDB**   | Ingestion + multi-model capability      | Graph traversal tail latency                      |
| **CognoDB**    | Managed cloud deployment                | Higher latency due to deployment/network overhead |

### Overall Recommendation

There is no universal winner.

**Choose Neo4j** when graph traversal and general-purpose graph performance are the primary requirements.

**Choose Memgraph** when low request latency and real-time concurrent graph serving are the priority.

**Choose TigerGraph** when high ingestion throughput and deeper graph processing are important.

**Choose ArangoDB** when high ingestion throughput and combined document + graph capabilities are valuable.

**Choose CognoDB** when managed cloud deployment and reduced infrastructure management are more important than raw latency.

> These recommendations apply specifically to the benchmark configuration, dataset size, query implementations, and deployment environments described in this README. Production decisions should be validated using representative datasets, workloads, and resource configurations.

---

# Reproducibility Checklist

To reproduce this benchmark:

* [ ] Use the same 101,027-edge Pokec subset
* [ ] Use the same node and relationship schema
* [ ] Use the same Python version
* [ ] Use the same batch size
* [ ] Use the same warm-up iterations
* [ ] Use the same query workload definitions
* [ ] Use the same concurrency levels
* [ ] Use the same 80/20 read/write ratio
* [ ] Run each database on the specified deployment type
* [ ] Record p50 and p95 latency
* [ ] Record ingestion throughput
* [ ] Record concurrency throughput
* [ ] Record errors/timeouts
* [ ] Record client-side memory usage
* [ ] Record server-side resource usage separately where possible

---

# Future Work

The next version of the benchmark should include:

1. Full **1.76M relationship** Pokec dataset
2. Multiple dataset sizes
3. Pokec profile attributes
4. Property-based indexing
5. Property-based aggregation
6. 4-hop, 5-hop, and deeper traversals
7. More concurrency levels
8. Server-side CPU monitoring
9. Server-side RAM monitoring
10. Disk I/O monitoring
11. Database-specific bulk-loading tools
12. Multiple benchmark repetitions
13. Confidence intervals
14. Cold-cache vs warm-cache testing
15. Network latency isolation for CognoDB
16. Hardware/resource isolation for self-hosted databases

---

# Dataset Attribution

Pokec dataset sourced from the [Stanford Large Network Dataset Collection (SNAP)](http://snap.stanford.edu/data/soc-Pokec.html).

Dataset: **Pokec Social Network**

The dataset is used for benchmarking and research purposes in accordance with its applicable license and attribution requirements.

---

**Benchmark Repository:** [github.com/Dhanushvardan/databases_benchmark](https://github.com/Dhanushvardan/databases_benchmark)

**Questions or Issues?** Open a GitHub issue or contact: [your contact]
