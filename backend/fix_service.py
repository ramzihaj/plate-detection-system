#!/usr/bin/env python
"""Fix plate_detection_service.py file"""

with open("app/services/plate_detection_service.py", "r") as f:
    lines = f.readlines()

# Find the problematic section and fix it
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip duplicate/malformed exception blocks
    if '                except Exception as e:' in line and i > 500:
        # Skip to the next major block
        i += 1
        while i < len(lines) and not lines[i].startswith('#'):
            i += 1
        i -= 1  # Back up one line
    else:
        fixed_lines.append(line)
    
    i += 1

# Remove excessive empty lines at end
while fixed_lines and fixed_lines[-1].strip() == '':
    fixed_lines.pop()

fixed_lines.append('\n')

with open("app/services/plate_detection_service.py", "w") as f:
    f.writelines(fixed_lines)

print("✓ Fixed plate_detection_service.py")
