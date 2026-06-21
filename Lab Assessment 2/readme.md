# Lab Assessment 2: Linux Process Monitoring, Architecture & Scheduling Controls 🧵📊

## 1. Lab Summary
This laboratory focuses on process lifecycle monitoring and CPU scheduling interventions. By spinning up continuous background mock workers, the workspace explores how the kernel monitors and interacts with executing threads:

* **Prerequisites & Process Ingestion** Acquired custom multi-threaded C source codes via remote terminal streaming (`wget`), compiled executable binaries with optimization paths, and initialized the cluster as an asynchronous background thread layer (`./mainprocess &`).
* **Process Monitoring and Management** Used system tracing utilities to inspect running jobs. Configured column filters (`ps -eo`) to monitor memory ingestion metrics, implemented descending sort parameters (`--sort=-pmem`) to find heavy processes, mapped process tree ancestry using `pstree -p -t`, adjusted execution priorities using root administrative commands (`renice`), and executed terminal termination sequences (`killall`).

---

## 2. Technical Reflection

### What I Learned
* **Process Ancestry & Thread Structures:** Mapping application lifecycles onto process trees clearly visualizes how a main process spawns independent child processing lanes to achieve parallelism.
* **Dynamic Priority Allocation:** Changing task priorities through `renice` demonstrated how operating system schedulers dynamically balance CPU cycles between low-priority background work and urgent active tasks.
* **System Resource Cleanups:** Mastering process signals changed my approach from forced program terminations to gracefully cleaning up hanging background threads, protecting resources from memory leaks.
