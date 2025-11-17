#!/usr/bin/env python3
from app.utils.tunisian_plate_formatter import format_tunisian_plate

# Test case 1: Should be 202TN2806 but got 000TN2522
test1 = ['0', '0', '0', '2', '5', '2', '2']
result1 = format_tunisian_plate(test1, 'center')
print(f'Test 1 - Got: {result1}')
print(f'Test 1 - Expected: 202 TN 2806')
print()

# Test case 2: Should be 152TN8355 but got 355TN0521
test2 = ['3', '5', '5', '0', '5', '2', '1']
result2 = format_tunisian_plate(test2, 'center')
print(f'Test 2 - Got: {result2}')
print(f'Test 2 - Expected: 152 TN 8355')
print()

# Correct cases
test3 = ['1', '5', '2', '8', '3', '5', '5']
result3 = format_tunisian_plate(test3, 'center')
print(f'Test 3 - Got: {result3}')
print(f'Test 3 - Expected: 152 TN 8355')
