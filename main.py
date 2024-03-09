#!/usr/bin/env python
"""RISC240 assembly language code commenter
@author luethan2025
@release 2024
"""
import argparse
import pathlib

# RISC240 instruction-to-comment mapping
isa_comment_map = {
  "ADD" : "{} <- {} + {}",
  "ADDI": "{} <- {} + {}",
  "AND" : "{} <- {} AND {}",
  "BRA" : "goto {}",
  "BRC" : "if carry, goto {}",
  "BRN" : "if negative, goto {}",
  "BRNZ": "if negative or zero, goto {}",
  "BRV" : "if overflow, goto {}",
  "BRZ" : "if zero, goto {}",
  "LI"  : "{} <- {}",
  "LW"  : "{} <- M[{} + {}]",
  "MV"  : "{} <- {}",
  "NOT" : "{} <- {} NOT {}",
  "OR"  : "{} <- {} OR {}",
  "SLL" : "{} <- {rs1} << {}",
  "SLLI": "{} <- {rs1} << {}",
  "SLT" : "{} - {}",
  "SLTI": "{} - {}",
  "SRA" : "{} <- {} >>> {}",
  "SRAI": "{} <- {} >>> {}",
  "SRL" : "{} <- {} >> {}",
  "SRLI": "{} <- {} >> {}",
  "STOP": "all done",
  "SUB" : "{} <- {} - {}",
  "SW"  : "M[{} + {}] <- {}",
  "XOR" : "{} <- {} XOR {}"
}

def decompose_file(filename):
  """Returns the line-by-line structure of a file
  Argument:
    filename - filename
  """
  with open(filename, "r") as f:
    lines = f.readlines()
  
  breakdown = {}
  for line_num in range(len(lines)):
    if lines[line_num] != "\n":
      line = lines[line_num].split(";")[0].strip()
      if line != "":
        line = line.strip().replace(",","").split()
        if line[0] not in isa_comment_map:
          # the line has an existing label
          breakdown[line_num] = {
            "label"      : line[0 ],
            "instruction": line[1 ],
            "args"       : line[2:]
          }
        else:
          # the line does not have a label
          breakdown[line_num] = {
            "instruction" : line[0 ],
            "args"        : line[1:]
          }
    else:
      breakdown[line_num] = {}
  return breakdown

def align_labels(breakdown):
  """Aligns the labels
  Argument:
    breakdown - dictionary containing the file structure
  """
  labels = [
    breakdown[line]["label"] for line in breakdown if "label" in breakdown[line]
  ]
  label_lengths = [len(label) for label in labels]
  if len(label_lengths) != 0:
    maximum_length_of_label = max(label_lengths)
  else:
    maximum_length_of_label = 0

  if maximum_length_of_label > 0:
    for line_num in breakdown:
      if breakdown[line_num] != {}:
        if "label" in breakdown[line_num]:
          # the line has an existing label
          breakdown[line_num]["label"] = breakdown[line_num]["label"] + \
            (" " * (maximum_length_of_label - len(breakdown[line_num]["label"])))
        else:
          # the line does not have a label
          breakdown[line_num]["instruction"] = (" " * (maximum_length_of_label + 1)) + \
            breakdown[line_num]["instruction"]
          
def align_instructions(breakdown):
  """Aligns the instruction
  Argument:
    breakdown - dictionary containing the file structure
  """
  instructions = [
    breakdown[line]["instruction"] for line in breakdown if "instruction" in breakdown[line]
  ]
  instruction_lengths = [len(instruction.strip()) for instruction in instructions]
  maximum_length_of_instruction = max(instruction_lengths)

  # preappends whitespace to each line with an instruction
  for line_num in breakdown:
    if "instruction" in breakdown[line_num]:
      breakdown[line_num]["instruction"] =  breakdown[line_num]["instruction"] + \
        (" " * (maximum_length_of_instruction - len(breakdown[line_num]["instruction"].strip())))

def align_args(breakdown):
  """Aligns the instruction arguments
  Argument:
    breakdown - dictionary containing the file structure
  """
  line_components = [
    list(breakdown[line].values()) for line in breakdown
  ]

  line_lengths = []
  for line_num in range(len(line_components)):
    if len(line_components[line_num]) != 0:
      if len(line_components[line_num]) == 3:
        # the line has an existing label
        label, instruction, args = line_components[line_num]
        arguments = ", ".join(args)

        line = " ".join([label,instruction, arguments])
        line_lengths.append(len(line))

        breakdown[line_num]["line"] = line
      elif len(line_components[line_num]) == 2:
        # the line does not have a label
        instruction, args = line_components[line_num]
        arguments = ", ".join(args)

        line = " ".join([instruction, arguments])
        line_lengths.append(len(line))

        breakdown[line_num]["line"] = line
      else:
        raise Exception()
      
  maximum_length_of_line = max(line_lengths)

  # preappends whitespace to each line with an instruction
  for line_num in breakdown:
    if "line" in breakdown[line_num]:
      breakdown[line_num]["line"] = breakdown[line_num]["line"] + \
        (" " * (maximum_length_of_line - len(breakdown[line_num]["line"])))

def put_comments(breakdown):
  """Appends RISC240 comments to the end of any line with an instruction on it.
  Argument:
    breakdown - dictionary containing the file structure
  """
  for line_num in breakdown:
    if "instruction" in breakdown[line_num]:
      format_string = isa_comment_map[breakdown[line_num]["instruction"].strip()]
      comment = format_string.format(*breakdown[line_num]["args"])
      breakdown[line_num]["line"] = breakdown[line_num]["line"] + " ; " + comment

def reconstruct_file(filename, breakdown):
  """Writes to the destination file using the provided file structure.
  Argument:
    filename - destination file
    breakdown - dictionary containing the file structure
  """
  output = []
  for line_num in breakdown:
    if "line" in breakdown[line_num]:
      output.append(breakdown[line_num]["line"])
    else:
      output.append("")
  with open(filename, "w") as f:
    f.write("\n".join(output))

def main(filename):
  """Main routine.
  Argument:
    filename - parsed argument from the command-line
  """
  file = pathlib.Path(filename)
  if not file.is_file():
    print(f"Aborting. Could not find {filename}\n")
    return

  if not filename.endswith(".asm"):
    extension = file.suffix
    print("Aborting. Expected a file ending with '.asm', but " +
         f"recieved '{extension}'\n")
    return
  
  breakdown = decompose_file(filename)
  align_labels(breakdown)
  align_instructions(breakdown)
  align_args(breakdown)
  put_comments(breakdown)
  reconstruct_file(filename, breakdown)
  print("doc240 has finished\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog="doc240",
                      description="RISC240 assembly language code commenter")
  parser.add_argument("--filename",
           help="specify the RISC240 source file",
           required=True)
  args = parser.parse_args()

  filename = args.filename
  main(filename)
