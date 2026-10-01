import time
import random
from adapter import Solver, cost_of

class MySolver(Solver):
    def solve(self, instance, submit_candidate):
        start_time = time.time()
        time_budget = 4.85  # Maximize the 5-second time limit ⏱️
        
        # 1. Expanded pool of smart starting heuristics 🧠📦
        orders = [
            sorted(range(instance.size), key=lambda b: (instance.fam[b], instance.due[b])),
            sorted(range(instance.size), key=lambda b: (instance.release[b], instance.due[b])),
            sorted(range(instance.size), key=lambda b: (instance.due[b], b)),
            sorted(range(instance.size), key=lambda b: (instance.weight[b] * -1, instance.due[b])),
            sorted(range(instance.size), key=lambda b: (instance.due[b] - instance.release[b], b))
        ]
        
        best_order = orders[0]
        best_cost = cost_of(instance, best_order)
        submit_candidate({"order": best_order})
        
        for initial_order in orders[1:]:
            cost = cost_of(instance, initial_order)
            if cost < best_cost:
                best_cost = cost
                best_order = initial_order
                submit_candidate({"order": best_order})
                
        current_order = list(best_order)
        current_cost = best_cost
        
        # 2. Advanced Local Search with Dual Neighborhoods (Relocate + 2-Opt) 🔄🛠️
        while (time.time() - start_time) < time_budget:
            improved = False
            
            # Neighborhood A: Relocate (Shift) 🚚
            indices = list(range(instance.size))
            if instance.size > 40:
                random.shuffle(indices)
                indices = indices[:min(instance.size, 50)]
                
            for i in indices:
                if (time.time() - start_time) >= time_budget:
                    break
                for j in indices:
                    if i == j:
                        continue
                        
                    candidate_order = list(current_order)
                    item = candidate_order.pop(i)
                    candidate_order.insert(j, item)
                    
                    cost = cost_of(instance, candidate_order)
                    if cost < current_cost:
                        current_cost = cost
                        current_order = candidate_order
                        if current_cost < best_cost:
                            best_cost = current_cost
                            best_order = list(current_order)
                            submit_candidate({"order": best_order})
                        improved = True
                        break
                if improved:
                    break
            
            # Neighborhood B: 2-Opt (Sub-segment Reversal) 🔄 if Relocate didn't improve
            if not improved and instance.size >= 6:
                for i in range(instance.size - 3):
                    if (time.time() - start_time) >= time_budget:
                        break
                    for j in range(i + 3, min(instance.size, i + 25)):
                        candidate_order = list(current_order)
                        candidate_order[i:j] = reversed(candidate_order[i:j])
                        
                        cost = cost_of(instance, candidate_order)
                        if cost < current_cost:
                            current_cost = cost
                            current_order = candidate_order
                            if current_cost < best_cost:
                                best_cost = current_cost
                                best_order = list(current_order)
                                submit_candidate({"order": best_order})
                            improved = True
                            break
                    if improved:
                        break
            
            # Perturbation / Shake if trapped in a local minimum 🌪️✨
            if not improved:
                if len(current_order) > 5:
                    for _ in range(3):
                        idx1, idx2 = random.sample(range(instance.size), 2)
                        current_order[idx1], current_order[idx2] = current_order[idx2], current_order[idx1]
                    current_cost = cost_of(instance, current_order)
                else:
                    break
                    
        return {"order": best_order}