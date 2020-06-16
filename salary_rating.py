#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
import argparse
import csv
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import numpy as np
import os
import sys


class Employee:
    def __init__(self, id, name, birthday=None, age=None, salary=None):
        try:
            self.id = int(id)
        except:
            self.id = id
        self.name = name
        self.birthday = birthday
        try:
            self.age = float(age) if age else None
        except:
            self.age = age
        try:
            self.salary = float(salary) if salary else None
        except:
            self.salary = salary
        self.salary_rating = None
        # parse birthday
        if isinstance(self.birthday, str):
            try:
                dt = datetime.datetime.strptime(self.birthday, "%Y/%m/%d")
                self.birthday = date(dt.year, dt.month, dt.day)
            except:
                pass
        # update age if possible
        if isinstance(self.birthday, datetime.date):
            dage = relativedelta(datetime.date.today(), self.birthday)
            self.age = dage.years + dage.months/12.0

    def is_valid(self):
        return ((isinstance(self.age, float) or isinstance(self.age, int))
                and (isinstance(self.salary, float) or isinstance(self.salary, int)))

class EmployeeStatsBin:
    def __init__(self, age_min):
        self.age_min = age_min
        self.employees = {}
        self.age_average = None
        self.salaray_average = self.salary_std = None

    def add(self, employee):
        if not employee.is_valid():
            return
        self.employees[employee.id] = employee
        self.age_ave = self.salary_ave = self.salary_std = None

    def make(self):
        self.age_ave = np.average([e.age for e in self.employees.values()])
        self.salary_ave = np.average([e.salary for e in self.employees.values()])
        self.salary_std = np.std([e.salary for e in self.employees.values()])


class EmployeeStats:
    def __init__(self, age_mins=[20, 30, 40]):
        self.bins = []
        for age_min in age_mins:
            self.bins.append(EmployeeStatsBin(age_min))

    def add(self, employee):
        if not employee.is_valid():
            return
        for i in range(len(self.bins)-1):
            if employee.age < self.bins[i+1].age_min:
                self.bins[i].add(employee)
                return
        self.bins[-1].add(employee)

    def make(self):
        for bin in self.bins:
            bin.make()

    def calc_salary_ave_std(self, age):
        age = min(age, 50)
        salary_ave = self.bins[-1].salary_ave
        salary_std = self.bins[-1].salary_std
        for i in range(len(self.bins)-1):
            if age < self.bins[i+1].age_ave or i+1 == len(self.bins)-1:
                dage_ave = self.bins[i+1].age_ave - self.bins[i].age_ave
                dsalary_ave = self.bins[i+1].salary_ave - self.bins[i].salary_ave
                dsalary_std = self.bins[i+1].salary_std - self.bins[i].salary_std
                x = age - self.bins[i].age_ave
                salary_ave = dsalary_ave / dage_ave * x + self.bins[i].salary_ave
                salary_std = dsalary_std / dage_ave * x + self.bins[i].salary_std
                break
        return salary_ave, salary_std
        
    def calc_salary_rating(self, employee):
        if not employee.is_valid():
            return None
        salary_ave, salary_std = self.calc_salary_ave_std(employee.age)
        return 50.0 + ((employee.salary - salary_ave) / salary_std) * 10.0


def main():
    # parse arguments
    arg_parser = argparse.ArgumentParser(description="Calculate salary rating.")
    arg_parser.add_argument("input", metavar="INPUT", nargs=1, help="an input CSV file.")
    arg_parser.add_argument("-n", "--num", metavar="NUM", nargs=1, type=int, default=[sys.maxsize],
                            help="the number of rows to be analyzed.")
    args = arg_parser.parse_args()
    
    # read input and make stats
    employees = []
    stats = EmployeeStats([20, 30, 40])
    with open(args.input[0], 'r') as fin:
        reader = csv.reader(fin)
        for index, row in enumerate(reader):
            employee = Employee(row[0], row[1], row[2], row[3], row[4])
            employees.append(employee)
            if index < args.num[0]:
                stats.add(employee)
    stats.make()

    # calculate salary rating
    for index, employee in enumerate(employees):
        if index < args.num[0]:
            employee.salary_rating = stats.calc_salary_rating(employee)

    # write to ?_salary_rating.csv
    name = os.path.splitext(args.input[0])[0]
    with open(name + "_salary_rating.csv", "w") as fout:
        writer = csv.writer(fout)
        for employee in employees:
            writer.writerow([employee.id, employee.name, employee.salary_rating])

    # write to ?_salary_by_age.csv
    with open(name + "_salary_by_age.csv", "w") as fout:
        writer = csv.writer(fout)
        writer.writerow(["Age", "Salary Ave.", "Salary STD"])
        for i in range(22, 60):
            ave, std = stats.calc_salary_ave_std(i)
            writer.writerow([i, ave, std])

    # write to ?_salary_stats.csv
    with open(name + "_salary_stats.csv", "w") as fout:
        writer = csv.writer(fout)
        writer.writerow(["", "Age Ave.", "Salary Ave.", "Salary STD"])
        for bin in stats.bins:
              writer.writerow(["%ds" % bin.age_min, bin.age_ave, bin.salary_ave, bin.salary_std])

if __name__ == "__main__":
    main()
