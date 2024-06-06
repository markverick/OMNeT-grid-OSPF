# Geneate config
xml = """<?xml version="1.0"?>
<OSPFASConfig xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="OSPF.xsd">

  <!-- Areas -->
  <Area id="0.0.0.0">
"""
height = 4
width = 6
R1 = "R1"
N1 = "N1"
# N[i*width+j].ethg[0] <--> C <--> R[(i*width+j)*2].ethg[0];
# N[i*width+(j+1)%width].ethg[1] <--> C <--> R[(i*width+j)*2].ethg[1];

# N[i*width+j].ethg[2] <--> C <--> R[(i*width+j)*2 + 1].ethg[0];
# N[((i+1)%height)*width+j].ethg[3] <--> C <--> R[(i*width+j)*2 + 1].ethg[1];
entry = []
for i in range(height):
  for j in range(width):
    id = i * width + j
    entry.append((i*width+j, (i*width+j)*2))
    entry.append((i*width+(j+1)%width, (i*width+j)*2))
    entry.append((i*width+j,(i*width+j)*2 + 1))
    entry.append((((i+1)%height)*width+j,(i*width+j)*2 + 1))
for (N, R) in entry:
    xml += "    <AddressRange address=\"R[" + str(R) + "]>N[" + str(N) + "]\" mask=\"R[" + str(R) + "]>N[" + str(N) + "]/\" />\n"

entry = []
xml += "  </Area>\n"
xml += "  <!-- Routers -->\n"
for i in range(height*width*2):
  xml += "  <Router name=\"R[" + str(i) + "]\" RFC1583Compatible=\"true\">\n"
  xml += """    <BroadcastInterface ifName="eth0" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
  xml += """    <BroadcastInterface ifName="eth1" areaID="0.0.0.0" interfaceOutputCost="1" routerPriority="1" />\n"""
  xml += "  </Router>\n"
xml += "</OSPFASConfig>"
# print(xml)
with open('ASConfig.xml', 'w') as f:
    print(xml, file=f)  # Python 3.x