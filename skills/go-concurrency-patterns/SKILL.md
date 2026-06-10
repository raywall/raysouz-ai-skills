---
name: go-concurrency-patterns
description: >
  Use this skill whenever writing Go code that involves concurrency. Triggers include: goroutines, channels,
  sync primitives (Mutex, WaitGroup, Once), worker pools, fan-out/fan-in pipelines, parallel I/O, rate limiting,
  context cancellation propagation, errgroup usage, or any mention of "goroutine", "channel", "concurrent",
  "parallel", "worker pool", "pipeline", "race condition", "select", "ticker", or "semaphore" in Go.
  Apply before generating any concurrent Go code to ensure correctness, leak-freedom, and performance.
---

# Go Concurrency Patterns

Act as a Go concurrency expert. Concurrency bugs (goroutine leaks, data races, deadlocks) are silent and
hard to find in production. Generate only patterns that are demonstrably correct: every goroutine started
must have a clear, guaranteed termination path.

---

## Foundational Rules

1. **Never start a goroutine without knowing when it will stop** — document it in a comment
2. **Always propagate context** — goroutines must select on `ctx.Done()` to honor cancellation
3. **Channel ownership**: the sender creates and closes the channel; receivers never close
4. **Prefer `errgroup` over raw `sync.WaitGroup`** for goroutines that can fail
5. **Always run tests with `-race`** — make `go test -race ./...` part of CI
6. **Avoid `sync.Mutex` across layers** — prefer message-passing (channels) for coordination

---

## Pattern 1 — Worker Pool (Fan-out)

Use when: processing a large slice of items concurrently with bounded parallelism.

```go
// workerPool runs work items concurrently with a bounded number of workers.
// It respects context cancellation and collects all errors.
// The caller controls concurrency via the workers parameter.
func workerPool[T, R any](
    ctx    context.Context,
    items  []T,
    workers int,
    fn     func(context.Context, T) (R, error),
) ([]R, error) {
    type result struct {
        val R
        err error
        idx int
    }

    jobs    := make(chan int, len(items))
    results := make(chan result, len(items))

    // Seed the jobs channel — closed after seeding so workers know when to stop.
    for i := range items { jobs <- i }
    close(jobs)

    // Launch bounded workers — each terminates when jobs is exhausted or ctx cancelled.
    var wg sync.WaitGroup
    for range workers {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for idx := range jobs {
                select {
                case <-ctx.Done():
                    results <- result{idx: idx, err: ctx.Err()}
                    return
                default:
                    val, err := fn(ctx, items[idx])
                    results <- result{val: val, err: err, idx: idx}
                }
            }
        }()
    }

    // Close results after all workers are done.
    go func() { wg.Wait(); close(results) }()

    // Collect — preserve order.
    out := make([]R, len(items))
    var errs []error
    for r := range results {
        if r.err != nil { errs = append(errs, r.err); continue }
        out[r.idx] = r.val
    }
    return out, errors.Join(errs...)
}
```

---

## Pattern 2 — Pipeline (Fan-out / Fan-in)

Use when: data flows through sequential transformation stages, each with own concurrency.

```go
// stage returns a channel of transformed items from the input channel.
// It launches n goroutines and fans their output into a single output channel.
// The output channel is closed when all goroutines finish.
func stage[In, Out any](
    ctx context.Context,
    in  <-chan In,
    n   int,
    fn  func(context.Context, In) (Out, error),
) (<-chan Out, <-chan error) {
    out  := make(chan Out, n)
    errc := make(chan error, n)

    var wg sync.WaitGroup
    for range n {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for item := range in {
                select {
                case <-ctx.Done():
                    errc <- ctx.Err()
                    return
                default:
                    res, err := fn(ctx, item)
                    if err != nil { errc <- err; continue }
                    out <- res
                }
            }
        }()
    }

    go func() { wg.Wait(); close(out); close(errc) }()
    return out, errc
}

// Usage: chain stages into a pipeline.
// raw → parse → enrich → persist
func buildPipeline(ctx context.Context, raw <-chan []byte) <-chan error {
    parsed,  errc1 := stage(ctx, raw,    4, parseRecord)
    enriched, errc2 := stage(ctx, parsed, 4, enrichRecord)
    _, errc3        := stage(ctx, enriched, 2, persistRecord)
    return mergeErrors(errc1, errc2, errc3)
}
```

---

## Pattern 3 — errgroup (Parallel Tasks)

Use when: running a fixed set of independent async tasks, all must succeed.

```go
// fetchAll fetches multiple resources concurrently using errgroup.
// The context is cancelled automatically if any fetch returns an error.
func fetchAll(ctx context.Context, ids []string, client ResourceClient) ([]Resource, error) {
    g, gCtx := errgroup.WithContext(ctx)
    results  := make([]Resource, len(ids))

    for i, id := range ids {
        i, id := i, id  // capture loop vars (Go < 1.22)
        g.Go(func() error {
            res, err := client.Fetch(gCtx, id)
            if err != nil { return fmt.Errorf("fetch %s: %w", id, err) }
            results[i] = res
            return nil
        })
    }

    if err := g.Wait(); err != nil { return nil, err }
    return results, nil
}
```

**With concurrency limit (errgroup.SetLimit):**
```go
g, gCtx := errgroup.WithContext(ctx)
g.SetLimit(10)  // at most 10 concurrent goroutines
for _, id := range ids {
    id := id
    g.Go(func() error { return process(gCtx, id) })
}
```

---

## Pattern 4 — Rate Limiter

Use when: calling downstream APIs with rate limits; controlling throughput.

```go
// RateLimitedClient wraps a client with a token bucket rate limiter.
// Tokens is the burst capacity; rate is the refill rate per second.
type RateLimitedClient struct {
    inner   Client
    limiter *rate.Limiter  // golang.org/x/time/rate
}

// Do executes a request after acquiring a rate limiter token.
// Blocks until a token is available or ctx is cancelled.
func (c *RateLimitedClient) Do(ctx context.Context, req Request) (Response, error) {
    if err := c.limiter.Wait(ctx); err != nil {
        return Response{}, fmt.Errorf("rate limiter: %w", err)
    }
    return c.inner.Do(ctx, req)
}
```

---

## Pattern 5 — Ticker / Background Worker

Use when: periodic jobs (heartbeat, cache refresh, metrics flush).

```go
// backgroundRefresher refreshes a cache on a fixed interval until ctx is cancelled.
// It is started as a goroutine and guaranteed to stop when ctx is Done.
type backgroundRefresher struct {
    cache    Cache
    interval time.Duration
    logger   *slog.Logger
}

// Run starts the refresh loop. Call as: go r.Run(ctx).
// Returns when ctx is cancelled.
func (r *backgroundRefresher) Run(ctx context.Context) {
    ticker := time.NewTicker(r.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            if err := r.cache.Refresh(ctx); err != nil {
                r.logger.ErrorContext(ctx, "cache refresh failed", "err", err)
            }
        case <-ctx.Done():
            r.logger.InfoContext(ctx, "background refresher stopped")
            return
        }
    }
}
```

---

## Pattern 6 — Scatter/Gather with Timeout

Use when: parallel lookups where partial results are acceptable or all must succeed within a deadline.

```go
// scatterGather fans out calls and gathers results within a deadline.
// Returns whatever completed within the deadline; logs stragglers.
func scatterGather[K comparable, V any](
    ctx      context.Context,
    keys     []K,
    timeout  time.Duration,
    fn       func(context.Context, K) (V, error),
) map[K]V {
    ctx, cancel := context.WithTimeout(ctx, timeout)
    defer cancel()

    type pair struct { k K; v V }
    ch := make(chan pair, len(keys))

    for _, k := range keys {
        k := k
        go func() {
            v, err := fn(ctx, k)
            if err != nil { return }  // stragglers are simply not included
            ch <- pair{k, v}
        }()
    }

    results := make(map[K]V, len(keys))
    deadline := time.After(timeout)
    for range len(keys) {
        select {
        case p := <-ch:
            results[p.k] = p.v
        case <-deadline:
            return results  // return partial results
        }
    }
    return results
}
```

---

## Pattern 7 — Done Channel for Shutdown

Use in long-lived servers to propagate graceful shutdown to all subsystems:

```go
// Server coordinates lifecycle of all subsystems via a shared context.
// All goroutines select on ctx.Done() — no manual done channels needed.
func Run(ctx context.Context, cfg Config) error {
    g, gCtx := errgroup.WithContext(ctx)

    g.Go(func() error { return serveHTTP(gCtx, cfg) })
    g.Go(func() error { return consumeSQS(gCtx, cfg) })
    g.Go(func() error { return flushMetrics(gCtx, cfg) })

    return g.Wait()  // returns when any goroutine errors or ctx cancelled
}
```

---

## Concurrency Anti-Patterns (Never Generate)

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `go func() { work() }()` without WaitGroup/errgroup | Goroutine leak on shutdown | Use errgroup or WaitGroup |
| Closing a channel from receiver | Panic | Only sender closes |
| Shared mutable state without sync | Data race | Use channel or Mutex |
| `time.Sleep` for synchronization | Flaky timing | Use channels or sync primitives |
| Unbuffered channel with no guaranteed receiver | Goroutine leak | Buffer or use select with default |
| Goroutine without ctx.Done() select | Ignores cancellation | Always select ctx.Done() |
| Lock held across I/O or sleep | Deadlock risk / starvation | Release lock before I/O |

---

## Testing Concurrent Code

```go
// TestWorkerPool verifies concurrent processing produces correct results.
// Run with: go test -race -count=5 ./...
func TestWorkerPool(t *testing.T) {
    t.Parallel()
    ctx := context.Background()
    items := []int{1, 2, 3, 4, 5}

    results, err := workerPool(ctx, items, 3, func(_ context.Context, n int) (int, error) {
        return n * 2, nil
    })

    require.NoError(t, err)
    assert.ElementsMatch(t, []int{2, 4, 6, 8, 10}, results)
}
```

Always add `-race` in CI:
```yaml
# .github/workflows/ci.yml
- run: go test -race -timeout 120s ./...
```
