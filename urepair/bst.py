class TreeNode:
    def __init__(self, key, value):
        self.left = None
        self.right = None
        self.key = key
        self.value = value

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        if self.root is None:
            self.root = TreeNode(key, value)
        else:
            self._insert(self.root, key, value)

    def _insert(self, current, key, value):
        if key < current.key:
            if current.left is None:
                current.left = TreeNode(key, value)
            else:
                self._insert(current.left, key, value)
        elif key > current.key:
            if current.right is None:
                current.right = TreeNode(key, value)
            else:
                self._insert(current.right, key, value)
        else:
            current.value = value  # Update the value at this key

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, current, key):
        if current is None:
            return None
        elif key == current.key:
            return current.value
        elif key < current.key:
            return self._search(current.left, key)
        else:
            return self._search(current.right, key)

    def in_order_traversal(self, node, visit):
        if node is not None:
            self.in_order_traversal(node.left, visit)
            visit(node.key, node.value)
            self.in_order_traversal(node.right, visit)
