import re
import sys
import os

def find_all_func_def(code):
  functions = {}

  lines = code.split('\n')

  i = 0
  while i < len(lines):
    if not lines[i]:
      i += 1
      continue

    match = re.search(r'^\s*def\s+(\S+?)\s*\(', lines[i])
    if not match:
      i += 1
      continue

    func_name = match.group(1)

    j = i
    while j < len(lines):
      if not lines[j]:
        j += 1
        continue

      if lines[j].strip().endswith(':'):
        break
      else:
        j += 1
      
    if j == len(lines):
      break
    
    functions[func_name] = (i, j)
    i = j + 1

  return functions

def find_import_typing(code):
  lines = code.split('\n')
  imports = []

  for line in lines:
    match = re.search(r'^\s*from typing import', line)
    if match:
      imports.append(line)
      continue

    # match = re.search(r'^\s*from \..+ import', line)
    # if match:
    #   imports.append(line)


  return imports

def add_hints(hinted_code, non_hinted_code):
  hinted_lines = hinted_code.split('\n')
  non_hinted_lines = non_hinted_code.split('\n')

  hinted_funcs = find_all_func_def(hinted_code)
  non_hinted_funcs = find_all_func_def(non_hinted_code)

  non_hinted_funcs = [(non_hinted_funcs[func][0], non_hinted_funcs[func][1], func)
                      for func in non_hinted_funcs]
  non_hinted_funcs.sort()
  
  offset = 0
  for (i, j, func) in non_hinted_funcs:
    if func in hinted_funcs:
      start = hinted_funcs[func][0]
      end = hinted_funcs[func][1]
      non_hinted_lines = non_hinted_lines[: i + offset] +\
                         hinted_lines[start: end + 1] +\
                         non_hinted_lines[j + offset + 1:]

      offset += (end - start) - (j - i)

  non_hinted_lines = find_import_typing(hinted_code) + non_hinted_lines

  return '\n'.join(non_hinted_lines)

# recursively finds all *.py source files from the given directory.
def get_files_recursively(dir_path):
  file_lst = []
  for root, dirs, files in os.walk(dir_path):
    for f in files:
      if f.endswith('.py'):
        file_lst.append(os.path.join(root, f))

  return file_lst

def main():
  if len(sys.argv) < 4:
    print('Usage: python hinted_dir non_hinted_dir modified_dir')

  hinted_files = get_files_recursively(sys.argv[1])
  non_hinted_files = get_files_recursively(sys.argv[2])
  modified_dir = sys.argv[3]

  hinted_files = set(hinted_files)
  non_hinted_files = set(non_hinted_files)

  pairs = []

  for hf in hinted_files:
    # if '__init__' in hf:
    #   continue
    nhf = sys.argv[2] + '/' + hf[hf.find('/') + 1:]
    if nhf in non_hinted_files:
      pairs.append((hf, nhf))

  for (hf, nhf) in pairs:
    with open(hf) as hf_file:
      hinted_code = hf_file.read()

    with open(nhf) as nhf_file:
      non_hinted_code = nhf_file.read()

    modified_code = add_hints(hinted_code, non_hinted_code)
    modified_file_name = modified_dir + '/' + hf[hf.find('/') + 1:]

    os.makedirs(os.path.dirname(modified_file_name), exist_ok=True)
    with open(modified_file_name, "w") as f:
      f.write(modified_code)
   
if __name__ == '__main__':
  main()
