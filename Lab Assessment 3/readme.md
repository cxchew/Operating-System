# Lab Assessment 3: Automation via Bash Shell Scripting & POSIX Permissions 🛡️📝

## 1. Lab Summary
This laboratory addresses system administration scaling challenges by utilizing shell scripting for automation, alongside enforcing security policies through file system access permissions:

* **Activity 1: Shell Commands Tracing** Analyzed complex, multi-tiered file command structures containing directory jumps and data replication operations. Mapped out structural parent-to-child directory trees originating from the `$HOME` workspace to track tracking behaviors.
* **Activity 2: Shell Scripting and Access Control** Engineered automated Bash shell script scripts (`myname2a.sh`) to loop through raw documents, parse values, and automatically deploy structured file systems. Evaluated discretionary access permissions masks (`drwxrwxr-x`) and designed a security remediation script (`myname2c.sh`) using octal and symbolic modes (`chmod`) to enforce clean operational boundaries across Owner, Group, and Public access profiles.

---

## 2. Technical Reflection

### What I Learned
* **Automated Environment Provisioning:** Writing structural shell automation scripts proved how powerful scripting is for replacing manual console inputs, reducing error rates when setting up bulk server assets.
* **Octal and Symbolic Masking Models:** Working directly with access matrices made POSIX permissions highly concrete. I learned to balance open read access against safe execution constraints.
* **Defensive Security Management:** Designing security scripts emphasized that folders must be hardened carefully based on user roles, preventing unauthorized context jumps or file overrides in multi-tenant directories.
