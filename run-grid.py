import sys
import subprocess
import os
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
  with open('ASConfig.xml', 'w') as file:
      print(xml, file=file)  # Python 3.x
      file.flush()
      os.fsync(file.fileno())

# Example usage
input_file_path = "omnetpp.ini.in"
output_file_path = "omnetpp.ini"
if len(sys.argv) < 2:
    print("arguments: width height")
else:
    height = int(sys.argv[1])
    width = int(sys.argv[2])

    replace_placeholders_in_file(input_file_path, output_file_path, width, height)

    gen_as_config_compact(height, width)

    try:
        subprocess.run(["inet","-u","Cmdenv","--result-dir=results-" + str(height) + "x" + str(width)])
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
