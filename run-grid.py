import sys
import subprocess
import os
import numpy as np

def replace_placeholders_in_file(input_file: str, output_file: str, height: int, width: int) -> None:
    """
    Reads the input file, replaces <width> and <height> placeholders with the provided values,
    and writes the result to the output file.

    Parameters:
    - input_file (str): The path to the input file.
    - output_file (str): The path to the output file.
    - height (int): The value to replace <height> with.
    - width (int): The value to replace <width> with.
    """
    height = str(height)
    width = str(width)
    try:
        with open(input_file, 'r') as file:
            file_contents = file.read()

        # Replace placeholders
        file_contents = file_contents.replace("<width>", width).replace("<height>", height)

        with open(output_file, 'w') as file:
            file.write(file_contents)
            file.flush()
            os.fsync(file.fileno())

        print(f"Placeholders replaced and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def gen_as_config_compact(height, width):

  # Geneate config
  xml = """<?xml version="1.0"?>
  <OSPFASConfig xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="OSPF.xsd">

    <!-- Areas -->
    <Area id="0.0.0.0">
  """

  # R[i*width+j].ethg[0] <--> C <--> R[i*width+(j+1)%width].ethg[2];
  # R[i*width+j].ethg[1] <--> C <--> R[i*width+(j+1)%width].ethg[3];
  entry = []
  for i in range(height):
    for j in range(width):
      id = i * width + j
      entry.append((i*width+j, i*width+(j+1)%width))
      entry.append((i*width+j, ((i+1)%height)*width+j))
  for (R1, R2) in entry:
      xml += "    <AddressRange address=\"R[" + str(R1) + "]>R[" + str(R2) + "]\" mask=\"R[" + str(R1) + "]>R[" + str(R2) + "]/\" />\n"
      xml += "    <AddressRange address=\"R[" + str(R2) + "]>R[" + str(R1) + "]\" mask=\"R[" + str(R2) + "]>R[" + str(R1) + "]/\" />\n"

  entry = []
  xml += "  </Area>\n"
  xml += "  <!-- Routers -->\n"
  for i in range(height*width):
    xml += "  <Router name=\"R[" + str(i) + "]\" RFC1583Compatible=\"true\">\n"
    xml += """    <BroadcastInterface ifName="eth0" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
    xml += """    <BroadcastInterface ifName="eth1" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
    xml += """    <BroadcastInterface ifName="eth2" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
    xml += """    <BroadcastInterface ifName="eth3" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
    xml += "  </Router>\n"
  xml += "</OSPFASConfig>"
  # print(xml)
  with open('scenarios/ASConfig-' + str(height) + 'x' + str(width) + '.xml', 'w') as file:
      print(xml, file=file)  # Python 3.x
      file.flush()
      os.fsync(file.fileno())
      
# Generate link fail events 
def gen_one_event(time, duration, src, src_if, dst, dst_if):
  recover_time = str(int(time + duration))
  time = str(int(time))
  src_if = str(src_if)
  dst_if = str(dst_if)
  xml = "    <at t=\"" + time + "us\">\n"
  xml += "        <disconnect src-module=\"" + src + "\" src-gate=\"ethg$o[" + src_if + "]\" />\n"
  xml += "        <disconnect src-module=\"" + dst + "\" src-gate=\"ethg$o[" + dst_if + "]\" />\n"
  xml += "    </at>\n"
  xml += "    <at t=\"" + recover_time + "us\">\n"
  xml += "        <connect src-module=\"" + src + "\" src-gate=\"ethg[" + src_if + "]\"\n"
  xml += "                 dest-module=\"" + dst + "\" dest-gate=\"ethg[" + dst_if + "]\"\n"
  xml += "                 channel-type=\"inet.common.misc.ThruputMeteringChannel\">\n"
  xml += "            <param name=\"delay\" value=\"10ms\" />\n"
  xml += "            <param name=\"datarate\" value=\"100Mbps\" />\n"
  xml += "            <param name=\"thruputDisplayFormat\" value=\'\"#N\"\' />\n"
  xml += "        </connect>\n"
  xml += "    </at>\n"
  return xml

# Use Pareto distribution
def gen_events_one_link(src, src_if, dst, dst_if, stop_time):
  prob_fail = (2, 10 * 1000000) # (alpha, x_m)
  prob_recover = (2, 1 * 1000000) # (alpha, x_m)
  current_time = 100 * 1000000 # start at 100 seconds
  xml = ""
  current_time += (np.random.pareto(prob_fail[0]) + 1) * prob_fail[1]
  while current_time <= stop_time:
    duration = (np.random.pareto(prob_recover[0]) + 1) * prob_recover[1]
    xml += gen_one_event(current_time, duration, src, src_if, dst, dst_if)
    current_time += duration + (np.random.pareto(prob_fail[0]) + 1) * prob_fail[1]
  return xml

def gen_link_update(height, width):
  xml = "<scenario>\n"
  for i in range(height):
    for j in range(width):
      src = "R[" + str(i*width+j) + "]"
      src_if = 0
      dst = "R[" + str(i*width+(j+1)%width) + "]"
      dst_if = 2
      xml += gen_events_one_link(src, src_if, dst, dst_if, stop_time=200 * 1000000)
      
      src = "R[" + str(i*width+j) + "]"
      src_if = 1
      dst = "R[" + str(((i+1)%height)*width+j) + "]"
      dst_if = 3
      xml += gen_events_one_link(src, src_if, dst, dst_if, stop_time=200 * 1000000)
  xml += "</scenario>\n"
  return xml


# Example usage
input_file_path = "omnetpp.ini.in"
output_file_path = "omnetpp.ini"
if len(sys.argv) < 3:
    print("arguments: <width> <height> [config](static, linkfail)")
else:
    height = int(sys.argv[1])
    width = int(sys.argv[2])
    if len(sys.argv) == 3:
        config = "static"
    else:
        config = sys.argv[3]
    
    if (config == "linkfail"):
        xml = gen_link_update(height, width)
        with open('scenarios/LinkUpdate-' + str(height) + 'x' + str(width) + '.xml', 'w') as file:
            print(xml, file=file)  # Python 3.x
            file.flush()
            os.fsync(file.fileno())

    replace_placeholders_in_file(input_file_path, output_file_path, width, height)

    gen_as_config_compact(height, width)

    try:
        subprocess.run(["inet","-u","Cmdenv","--result-dir=results/" + str(height) + "x" + str(width), "-c", config])
        #result = subprocess.run(["inet","-u","Cmdenv","--result-dir=results-" + str(height) + "x" + str(width)], capture_output=True, text=True, check=True)
        #with open("results-" + str(height) + "x" + str(width) + "/out.log", 'w') as file:
        #    file.write(result.stdout)
        #    file.flush()  # Ensure data is written to disk
        #    os.fsync(file.fileno())  # Ensure the write is complete
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        if e.stderr:
            print(f"Standard error: {e.stderr}")

    print("done")
