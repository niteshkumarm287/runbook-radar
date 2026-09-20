# High Disk-Space Usage

Service: shared-infrastructure
Team: platform

## Symptoms

- Filesystem usage exceeds the warning threshold.
- A host or persistent volume has little free disk space.
- Applications may fail to write logs or temporary files.

## Investigation

1. Identify the filesystem consuming the most space.
2. Find unexpectedly large files and directories.
3. Check log rotation and retention.
4. Use only an approved cleanup procedure.