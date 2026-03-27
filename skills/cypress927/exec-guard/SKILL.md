---
name: exec-guard
description: Secure command execution for AI agents with memory protection (8KB ring buffer), timeout control, background process management, and clean child process termination. Use when executing system commands that need reliable output handling, long-running background tasks, or service startup monitoring.
---

# exec-guard - Secure Command Execution for AI Agents

Execute system commands safely with built-in protections against memory overflow, timeout, and orphan processes.

## Features

| Feature | Description |
|---------|-------------|
| **8KB Ring Buffer** | Head-Tail dual buffer prevents memory overflow from infinite output |
| **Timeout Control** | Automatically kill stuck processes |
| **Background Mode** | Run long tasks with PID tracking and status queries |
| **Watch Window** | Confirm service startup before returning (catch early errors) |
| **Process Groups** | Clean termination of all child processes (no orphans) |

## When to Use

| Trigger | Action |
|---------|--------|
| Run quick command | Sync exec with timeout |
| Long-running task | Background exec |
| Start a service | Background + watch window |
| Large output command | Automatic 8KB buffer protection |
| Check process status | Query by PID |
| Kill stuck process | Terminate by PID |

## Quick Examples

### CLI Mode

```bash
# Sync execution
echo '{"command": "ls -la"}' | ./cmd_exec_linux

# With timeout (5 minutes for npm install)
echo '{"command": "npm install", "timeout_seconds": 300}' | ./cmd_exec_linux

# Background execution
echo '{"command": "python train.py", "run_in_background": true}' | ./cmd_exec_linux

# Background + watch window (for service startup)
echo '{"command": "java -jar app.jar", "run_in_background": true, "watch_duration_seconds": 10}' | ./cmd_exec_linux
```

### HTTP Mode

```bash
# Start server
./cmd_exec_linux -server -port 8080

# Execute via API
curl -X POST http://localhost:8080/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'

# Check process status
curl http://localhost:8080/process/12345

# Kill process
curl -X DELETE http://localhost:8080/process/12345
```

## Request Parameters

```json
{
  "command": "required - system command to execute",
  "working_dir": "optional - working directory",
  "timeout_seconds": "optional - default 30",
  "run_in_background": "optional - default false",
  "watch_duration_seconds": "optional - monitor window for background",
  "env": "optional - custom environment variables"
}
```

## Response Structure

```json
{
  "status": "success|failed|timeout|killed|running",
  "exit_code": "0 for success, -1 for running/error",
  "stdout": "head-tail buffered output (max 8KB)",
  "stderr": "error output (max 8KB)",
  "system_message": "execution details"
}
```

## Status Values

| Status | Meaning |
|--------|---------|
| `success` | Exit code 0 |
| `failed` | Exit code non-0 |
| `timeout` | Killed after timeout |
| `killed` | Manually terminated |
| `running` | Background process active |

## Best Practices

1. **Quick commands**: Sync mode, default timeout
2. **Long tasks**: Background mode with PID tracking
3. **Service startup**: Background + watch_duration (catch startup errors early)
4. **Large output**: Automatic 8KB buffer prevents OOM
5. **Custom env**: Override carefully, don't replace PATH entirely

## Asset Location

The binary is at `assets/cmd_exec_linux`. Scripts wrap it for convenience.

## References

- `references/api.md` - Full API documentation
- `references/design.md` - Ring buffer and process group design details