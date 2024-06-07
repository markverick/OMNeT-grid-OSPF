import sys

height = int(sys.argv[1])
width = int(sys.argv[2])

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
with open('ASConfig.xml', 'w') as f:
    print(xml, file=f)  # Python 3.x