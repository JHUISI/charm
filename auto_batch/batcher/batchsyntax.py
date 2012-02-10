

# post-order traversal needed here?
class TypeCheck(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)
    
    def visit_attr(self, node, data):
        pass