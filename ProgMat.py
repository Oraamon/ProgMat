import math
from ortools.linear_solver import pywraplp

def read_data(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        n_sources, n_destinations = map(int, lines[0].split())
        supplies = list(map(int, lines[1].split()))
        demands = list(map(int, lines[2].split()))
        costs = [list(map(int, line.split())) for line in lines[3:3 + n_sources]]

        # Checar se há desbalanceamento
        total_supply = sum(supplies)
        total_demand = sum(demands)

        if total_supply > total_demand:
            # Adicionar destino fictício para absorver o excesso
            demands.append(total_supply - total_demand)
            for i in range(n_sources):
                costs[i].append(0)  # Custo zero para o destino fictício
            n_destinations += 1
        elif total_demand > total_supply:
            # Adicionar origem fictícia para suprir a falta
            supplies.append(total_demand - total_supply)
            costs.append([0] * n_destinations)  # Custo zero para a origem fictícia
            n_sources += 1
        
    return n_sources, n_destinations, supplies, demands, costs

def solve_transport_problem(n_sources, n_destinations, supplies, demands, costs):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    x = {}

    # Criar variáveis de decisão
    for i in range(n_sources):
        for j in range(n_destinations):
            x[i, j] = solver.NumVar(0, solver.infinity(), f'x[{i},{j}]')
            print(f'x[{i},{j}]')

    # Restrições de oferta
    for i in range(n_sources):
        constraint_supply = solver.Constraint(supplies[i], supplies[i], f'Supply_Constraint_{i}')
        for j in range(n_destinations):
            constraint_supply.SetCoefficient(x[i, j], 1)

    # Restrições de demanda
    for j in range(n_destinations):
        constraint_demand = solver.Constraint(demands[j], demands[j], f'Demand_Constraint_{j}')
        for i in range(n_sources):
            constraint_demand.SetCoefficient(x[i, j], 1)

    # Função objetivo
    objective = solver.Objective()
    for i in range(n_sources):
        for j in range(n_destinations):
            objective.SetCoefficient(x[i, j], costs[i][j])
    objective.SetMinimization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        result = []
        for i in range(n_sources):
            for j in range(n_destinations):
                solution_value = x[i, j].solution_value()
                fractional_part = solution_value - int(solution_value)

                if fractional_part >= 0.1:
                    amount = math.ceil(solution_value)
                else:
                    amount = int(solution_value)

                if amount > 0:
                    result.append((i, j, amount))
        return result
    else:
        print('No optimal solution was found.')
        return None

def write_solution(result, filename):
    with open(filename, 'w') as file:
        file.write('Política de transporte:\n')
        print('Solução Otima:')
        for i, j, value in result:
            file.write(f'Transporte de {int(value)} unidade(s) da origem {i + 1} para o destino {j + 1}.\n')
            print(f'Transporte de {int(value)} unidade(s) da origem {i + 1} para o destino {j + 1}.')

def main():
    input_filename = 'input.txt'
    output_filename = 'output.txt'
    n_sources, n_destinations, supplies, demands, costs = read_data(input_filename)
    result = solve_transport_problem(n_sources, n_destinations, supplies, demands, costs)
    if result:
        write_solution(result, output_filename)

main()
