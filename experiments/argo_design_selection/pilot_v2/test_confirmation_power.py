#!/usr/bin/env python3
from plan_confirmation import minimum_n,power,two_sided_sign_p
assert two_sided_sign_p(0,0)==1.0
assert two_sided_sign_p(10,10)<0.05
assert power(100,0.5,0.5)<=0.06
assert power(50,0.5,0.9)>power(50,0.5,0.75)>power(50,0.5,0.65)
for pd,pw,expected in [(0.25,0.75,135),(0.5,0.75,67),(0.75,0.9,16)]:
 n,p=minimum_n(pd,pw);assert n==expected and p>=0.8;assert power(n-1,pd,pw)<0.8
print("All checks passed.")
