import pandas as pd
from pulp import *

class InvestmentOptimizer:

    def __init__(self, data_file, available_capital, cost_limit, minimum_per_category, maximum_medium_investment):
        self.data = pd.read_csv(data_file, sep=';', header=None, names=['Investment', 'Cost', 'Return', 'Risk'])
        self.available_capital = available_capital
        self.cost_limit = cost_limit
        self.minimum_per_category = minimum_per_category
        self.maximum_medium_investment = maximum_medium_investment

    def define_problem(self):
        number_of_investment_options = len(self.data)
        investment_costs = self.data['Cost'].values
        return_of_investments = self.data['Return'].values  # ROIs

        low_risk_category = [1 if r == 0 else 0 for r in self.data['Risk'].values]  # Low risk investments
        medium_risk_category = [1 if r == 1 else 0 for r in self.data['Risk'].values]  # Medium risk investments
        high_risk_category = [1 if r == 2 else 0 for r in self.data['Risk'].values]  # High risk investments

        prob = LpProblem("Investment_Optimization", LpMaximize)

        chosen_investments = LpVariable.dicts("Investment", range(number_of_investment_options), cat='Binary')

        prob += lpSum([chosen_investments[i] * return_of_investments[i] for i in range(number_of_investment_options)])

        prob += lpSum([chosen_investments[i] * investment_costs[i] for i in range(number_of_investment_options)]) <= self.available_capital, "Investment_Limit"
        prob += lpSum([chosen_investments[i] * low_risk_category[i] for i in range(number_of_investment_options)]) >= self.minimum_per_category[0], "Low_Risk_Min"
        prob += lpSum([chosen_investments[i] * medium_risk_category[i] for i in range(number_of_investment_options)]) >= self.minimum_per_category[1], "Medium_Risk_Min"
        prob += lpSum([chosen_investments[i] * high_risk_category[i] for i in range(number_of_investment_options)]) >= self.minimum_per_category[2], "High_Risk_Min"
        prob += lpSum([chosen_investments[i] * investment_costs[i] * low_risk_category[i] for i in range(number_of_investment_options)]) <= self.cost_limit[0], "Low_Risk_Max_Cost"
        prob += lpSum([chosen_investments[i] * investment_costs[i] * medium_risk_category[i] for i in range(number_of_investment_options)]) <= self.cost_limit[1], "Medium_Risk_Max_Cost"
        prob += lpSum([chosen_investments[i] * investment_costs[i] * high_risk_category[i] for i in range(number_of_investment_options)]) <= self.cost_limit[2], "High_Risk_Max_Cost"
        
        # Extra constraint
        prob += lpSum([chosen_investments[i] * medium_risk_category[i] for i in range(number_of_investment_options)]) <= self.maximum_medium_investment[0], "Medium_Risk_Max"

        self.prob = prob
        self.chosen_investments = chosen_investments
        self.low_risk_category = low_risk_category
        self.medium_risk_category = medium_risk_category
        self.high_risk_category = high_risk_category

    def solve(self):
        self.prob.solve(pulp.PULP_CBC_CMD(msg=True))

    def get_results(self):
        total_spent = 0
        investments = {"Low Risk": [], "Medium Risk": [], "High Risk": []}
        risk_dict = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}

        for i in range(len(self.data)):
            if self.chosen_investments[i].value() == 1.0:
                investment_info = self.data.iloc[i]
                risk_category = risk_dict[investment_info['Risk']] 
                print(f"Investment {i + 1}  - Cost: {investment_info['Cost']}, Return: {investment_info['Return']}, Risk: {risk_category}")

                total_spent += investment_info['Cost']

                if self.low_risk_category[i] == 1:
                    investments["Low Risk"].append(investment_info['Investment'])
                elif self.medium_risk_category[i] == 1:
                    investments["Medium Risk"].append(investment_info['Investment'])
                elif self.high_risk_category[i] == 1:
                    investments["High Risk"].append(investment_info['Investment'])

        print(f"\nInvestments by risk category:")
        for category, investments in investments.items():
            print(f"{category}: {investments}")

        print(f"\nTotal ROI = {self.prob.objective.value()}")
        print(f"Total Spent = {total_spent}")
        print(f"Available - Spent = {self.available_capital - total_spent}")

        print(f"Status: {LpStatus[self.prob.status]}")


# cost_limit = []
optimizer = InvestmentOptimizer('data.csv', available_capital = 2400000, cost_limit = [1200000, 1500000, 900000], minimum_per_category = [2, 2, 1], maximum_medium_investment = [5])
optimizer.define_problem()
optimizer.solve()
optimizer.get_results()
