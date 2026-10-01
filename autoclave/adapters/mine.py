"""Multi-start insertion search for the Autoclave Queue challenge."""

import random
import time

from adapter import Solver, cost_of


class MySolver(Solver):
    def solve(self, instance, submit_candidate):
        started = time.perf_counter()
        deadline = started + 4.65
        n = instance.size
        ids = list(range(n))
        rng = random.Random(str(instance.digest) + ":3")

        if n == 0:
            return {"order": []}

        # Start with several useful priorities. Weighted slack helps bring
        # urgent, high-penalty batches forward, especially in tight instances.
        starts = [
            sorted(ids, key=lambda b: (instance.fam[b], instance.due[b], b)),
            sorted(ids, key=lambda b: (instance.release[b], instance.due[b], b)),
            sorted(ids, key=lambda b: (instance.due[b], b)),
            sorted(ids, key=lambda b: (instance.weight[b], instance.due[b], b)),
            sorted(ids, key=lambda b: ((instance.due[b] - instance.release[b] - instance.proc[b]) / instance.weight[b], instance.due[b], b)),
            sorted(ids, key=lambda b: (instance.due[b] / instance.weight[b], instance.due[b], b)),
        ]

        best_order = list(starts[0])
        best_cost = cost_of(instance, best_order)
        submit_candidate({"order": best_order})
        for order in starts[1:]:
            c = cost_of(instance, order)
            if c < best_cost:
                best_order, best_cost = list(order), c
                submit_candidate({"order": best_order})

        current_order = list(best_order)
        current_cost = best_cost
        restart_count = 0

        while time.perf_counter() < deadline:
            improved = False
            positions = list(range(n))
            if n > 50:
                rng.shuffle(positions)
                positions = positions[:45]

            # First-improvement relocate search, matching the reliable core of
            # your current solver while varying scan order between passes.
            for i in positions:
                if time.perf_counter() >= deadline:
                    break
                for j in positions:
                    if i == j:
                        continue
                    candidate = list(current_order)
                    item = candidate.pop(i)
                    candidate.insert(j, item)
                    c = cost_of(instance, candidate)
                    if c < current_cost:
                        current_order, current_cost = candidate, c
                        improved = True
                        break
                if improved:
                    break

            # Try some swaps too; they can cross plateaus where one insertion
            # at a time cannot improve the plan.
            if not improved and time.perf_counter() < deadline:
                for _ in range(80):
                    i, j = rng.sample(range(n), 2)
                    candidate = list(current_order)
                    candidate[i], candidate[j] = candidate[j], candidate[i]
                    c = cost_of(instance, candidate)
                    if c < current_cost:
                        current_order, current_cost = candidate, c
                        improved = True
                        break
                    if time.perf_counter() >= deadline:
                        break

            if current_cost < best_cost:
                best_order, best_cost = list(current_order), current_cost
                submit_candidate({"order": best_order})

            if not improved:
                # Periodically restart near the global best, with a larger
                # shake each time instead of letting the search drift randomly.
                restart_count += 1
                current_order = list(best_order)
                shake_count = 1 + (restart_count % 6)
                for _ in range(shake_count):
                    i = rng.randrange(n)
                    if n > 1:
                        distance = rng.randint(1, min(8, n - 1))
                        j = max(0, min(n - 1, i + (distance if rng.random() < 0.5 else -distance)))
                        if i != j:
                            item = current_order.pop(i)
                            current_order.insert(j, item)
                current_cost = cost_of(instance, current_order)

        return {"order": best_order}
