#!/usr/bin/python
"""
Binary tree node structure for representing parsed ZK statements.

This module provides the BinNode class used by the ZKP compiler to represent
parsed zero-knowledge proof statements as a binary tree structure.

Note:
    This module is part of the experimental ZKP compiler and should be
    considered proof-of-concept quality.
"""


class BinNode:
    """
    Binary tree node for representing ZK proof statement components.

    Node types:
        - ATTR (0): Attribute/variable node (leaf)
        - OR (1): Logical OR node
        - AND (2): Logical AND node
        - EXP (3): Exponentiation node (^)
        - EQ (4): Equality node (=)

    Args:
        value: Either a string (creates ATTR node) or int (creates operator node)
        left: Left child node (optional)
        right: Right child node (optional)
    """

    def __init__(self, value, left=None, right=None):
        # Node type constants
        self.OR = 1
        self.AND = 2
        self.EXP = 3  # '^' or exponent
        self.EQ = 4   # ==
        self.ATTR = 0

        if isinstance(value, str):
            self.type = self.ATTR
            self.attribute = value.upper()  # Python 3 compatible

        elif isinstance(value, int):
            if value > 0 and value <= self.EQ:
                self.type = value
            self.attribute = ''

        self.left = left
        self.right = right

    def __str__(self):
        if self.type == self.ATTR:
            return self.attribute
        else:
            left = str(self.left)
            right = str(self.right)

            if self.type == self.OR:
                return '(' + left + ') or (' + right + ')'
            elif self.type == self.AND:
                return '(' + left + ') and (' + right + ')'
            elif self.type == self.EXP:
                return left + '^' + right
            elif self.type == self.EQ:
                return left + ' = ' + right
        return None

    def getAttribute(self):
        """Return the attribute value if this is an ATTR node, else None."""
        if self.type == self.ATTR:
            return self.attribute
        else:
            return None

    def getLeft(self):
        """Return the left child node."""
        return self.left

    def getRight(self):
        """Return the right child node."""
        return self.right

    def addSubNode(self, left, right):
        """Set the left and right child nodes."""
        self.left = left if left is not None else None
        self.right = right if right is not None else None  # Fixed: was checking left

    def traverse(self, function):
        """
        Traverse the tree and apply function to each node.

        Args:
            function: Callable that takes (node_type, node) as arguments
        """
        # Visit node then traverse left and right
        function(self.type, self)
        if self.left is None:
            return None
        self.left.traverse(function)
        if self.right is None:
            return None
        self.right.traverse(function)
        return None


