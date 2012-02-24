

# post-order traversal needed here?
class BasicTypeExist(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)
    
    def visit_attr(self, node, data):
        variable = node.getAttribute()
        # consider storing variables in a list?
        if not variable in self.vars.keys(): print("Error: ", variable, "does not have a type!")
    
    def conclude(self):
        pass
