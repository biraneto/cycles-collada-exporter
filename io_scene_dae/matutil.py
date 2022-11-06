# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact Info: biraneto@gmail.com


# All the info we care about
class MatInfo:
    def __init__(self):
        self.mainBSDF = None
        self.diffuseTex = None
        self.addTex = None
        self.specTex = None
        self.normalTex = None
        self.mapTex = None
        self.diffuseUv = None
        self.addUv = None
        self.specUv = None
        self.normalUv = None        
        self.mapUv = None
        self.diffuseWrap = "WRAP"
        self.addWrap = "WRAP"
        self.specWrap = "WRAP"
        self.normalWrap = "WRAP"        
        self.mapWrap = "WRAP"
        self.emission_color = (0.0,0.0,0.0)
        self.emission_strength = 1.0
        self.base_color = (1.0,1.0,1.0)
        self.alpha = 1.0
        self.specular = 0.5
        self.metallic = 0.0
        self.roughness = 0.5
        self.ior = 1.45
        self.mapType = "Alpha"
    def getText(self, key):
        return getattr(self, key, None)


# Scanner methods so we can find BSDF shaders and textures
class MatWalker:
    def __init__(self):
        self.info = MatInfo()

    def findOutput(self, nodes):
        for node in nodes:
            if node.bl_idname == "ShaderNodeOutputMaterial":
                return node
        return None

    def loadMainBSDF(self, output):
        if not hasattr(output, 'inputs'):
            return None
        inputList = output.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        fromNode = link.from_node
                        if node.identifier == "Surface" and link.to_socket.bl_idname == "NodeSocketShader":
                            if fromNode.bl_idname == "ShaderNodeBsdfPrincipled":
                                return fromNode
                            else:
                                newList.append(fromNode)
                if hasattr(node, 'inputs'):
                    for input in node.inputs:
                        if hasattr(input, 'links'):
                            newList.append(input)
            inputList = newList
        return None

    def loadTexture(self, srcnode, main = None):
        if hasattr(srcnode, 'bl_idname') and srcnode.bl_idname == "ShaderNodeTexImage" and main != srcnode:
            return srcnode
        if not hasattr(srcnode, 'inputs'):
            return None
        inputList = srcnode.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        fromNode = link.from_node
                        if fromNode.bl_idname == "ShaderNodeTexImage" and link.to_socket.bl_idname == "NodeSocketColor":
                            if main != fromNode:
                                return fromNode
                        else:
                            newList.append(fromNode)
                if hasattr(node, 'inputs'):
                    for input in node.inputs:
                        if hasattr(input, 'links'):
                            newList.append(input)
            inputList = newList
        return None
    
    def loadMapTexture(self, srcnode):
        if not hasattr(srcnode, 'inputs'):
            return None
        inputList = srcnode.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        fromNode = link.from_node
                        fromSocket = link.from_socket
                        if fromNode.bl_idname == "ShaderNodeTexImage" and link.to_socket.name == "Fac":
                            if fromSocket.identifier == "Alpha":
                                self.info.mapType = "Alpha"
                            if fromSocket.identifier == "Color":
                                self.info.mapType = "Color"
                            return fromNode
                        else:
                            newList.append(fromNode)
            inputList = newList
        return None

    def loadBSDFTexture(self, bsdf, main = None):
        if not hasattr(bsdf, 'inputs'):
            return None
        inputList = bsdf.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        if node.identifier == "Base Color":
                            fromNode = link.from_node
                            theTexture = self.loadTexture(fromNode, main)
                            if theTexture is not None:
                                return theTexture
                            else:
                                newList.append(fromNode)
            inputList = newList
        return None
    
    def loadBSDFMapTexture(self, bsdf):
        if not hasattr(bsdf, 'inputs'):
            return None
        inputList = bsdf.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        if node.identifier == "Base Color":
                            fromNode = link.from_node
                            theTexture = self.loadMapTexture(fromNode)
                            if theTexture is not None:
                                return theTexture
                            else:
                                newList.append(fromNode)
            inputList = newList
        return None

    def loadBumpTexture(self, bsdf):
        if not hasattr(bsdf, 'inputs'):
            return None
        inputList = bsdf.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        if node.identifier == "Normal" and link.to_socket.bl_idname == "NodeSocketVector":
                            fromNode = link.from_node
                            if hasattr(fromNode, 'uv_map'):
                                self.info.normalUv = fromNode.uv_map
                            theTexture = self.loadTexture(fromNode)
                            if theTexture is not None:
                                return theTexture
                            else:
                                newList.append(fromNode)
            inputList = newList
        return None

    def loadUVIndex(self, texture):
        if not hasattr(texture, 'inputs'):
            return None
        inputList = texture.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        fromNode = link.from_node
                        if fromNode.bl_idname == "ShaderNodeUVMap":
                            uvIndex = fromNode.uv_map
                            return uvIndex
                        else:
                            newList.append(fromNode)
                if hasattr(node, 'inputs'):
                    for input in node.inputs:
                        if hasattr(input, 'links'):
                            newList.append(input)
            inputList = newList
        return None
    
    def loadSpecTexture(self, bsdf): 
        if not hasattr(bsdf, 'inputs'):
            return None
        inputList = bsdf.inputs
        while len(inputList) > 0:
            newList = list()
            for node in inputList:
                if hasattr(node, 'links'):
                    for link in node.links:
                        if node.identifier == "Specular" :
                            fromNode = link.from_node
                            theTexture = self.loadTexture(fromNode)
                            if theTexture is not None:
                                return theTexture
                            else:
                                newList.append(fromNode)
            inputList = newList
        return None

    # Retrieves material info based on the material nodes    
    def getMaterialInfo(self, material):

        if material.node_tree is not None:
            nodes =  material.node_tree.nodes
            output = self.findOutput(nodes)
            mainBSDF = self.loadMainBSDF(output)
            if mainBSDF is None:
                mainText = self.loadTexture(output)
            else:
                mainText = self.loadBSDFTexture(mainBSDF) 
            specText = self.loadSpecTexture(mainBSDF)
            bumpText = self.loadBumpTexture(mainBSDF)
            addText = self.loadBSDFTexture(mainBSDF, mainText)
            mapText = self.loadBSDFMapTexture(mainBSDF)
            
            if addText is not None:
                self.info.addUv = self.loadUVIndex(addText)
            if bumpText is not None:
                if self.info.normalUv is None:
                    self.info.normalUv = self.loadUVIndex(bumpText)
                
            if specText is not None:
                self.info.specUv = self.loadUVIndex(specText)
            if mapText is not None:
                self.info.mapUv = self.loadUVIndex(mapText)
            
            if mainText is not None:
                self.info.diffuseUv = self.loadUVIndex(mainText)

            if mainBSDF is not None:
                self.info.emission_color = (mainBSDF.inputs["Emission"].default_value[0],  mainBSDF.inputs["Emission"].default_value[1],  mainBSDF.inputs["Emission"].default_value[2])
                self.info.emission_strength = mainBSDF.inputs["Emission Strength"].default_value
                self.info.base_color = (mainBSDF.inputs["Base Color"].default_value[0],  mainBSDF.inputs["Base Color"].default_value[1],  mainBSDF.inputs["Base Color"].default_value[2])
                self.info.alpha = mainBSDF.inputs["Alpha"].default_value
                self.info.specular = mainBSDF.inputs["Specular"].default_value
                self.info.metallic = mainBSDF.inputs["Metallic"].default_value
                self.info.roughness = mainBSDF.inputs["Roughness"].default_value
                self.info.ior = mainBSDF.inputs["IOR"].default_value
            
            self.info.mainBSDF = mainBSDF
            self.info.diffuseTex = mainText
            if mainText is not None :
                self.info.diffuseWrap = "WRAP" if mainText.extension == "REPEAT" else "CLAMP"
            self.info.addTex = addText
            if addText is not None :
                self.info.addWrap = "WRAP" if addText.extension == "REPEAT" else "CLAMP"
            self.info.specTex = specText
            if specText is not None :
                self.info.specWrap = "WRAP" if specText.extension == "REPEAT" else "CLAMP"
            self.info.normalTex = bumpText
            if bumpText is not None :
                self.info.normalWrap = "WRAP" if bumpText.extension == "REPEAT" else "CLAMP"
            self.info.mapTex = mapText
            if mapText is not None :
                self.info.mapWrap = "WRAP" if mapText.extension == "REPEAT" else "CLAMP"
            
        return self.info



