import os
import tree_sitter
import tree_sitter_python
from pathlib import Path
from typing import List, Dict, Optional, Any

# Initialize tree-sitter parser with python grammar
try:
    # tree-sitter 0.22+ API
    PY_LANGUAGE = tree_sitter.Language(tree_sitter_python.language())
    parser = tree_sitter.Parser(PY_LANGUAGE)
except Exception:
    # Older API fallback
    parser = tree_sitter.Parser()
    PY_LANGUAGE = tree_sitter.Language(tree_sitter_python.language(), "python")
    parser.set_language(PY_LANGUAGE)

def _walk_tree(node: Any, relative_path: str, current_class: Optional[str] = None, chunks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Recursively walks the AST to find semantic blocks (classes and functions).
    
    Args:
        node: The Tree-sitter node to start walking from.
        relative_path: The path of the file relative to the repository root.
        current_class: Name of the class if the node is within a class definition.
        chunks: Accumulator list for the discovered code chunks.
        
    Returns:
        List[Dict[str, Any]]: A list of chunks containing metadata and code snippets.
    """
    if chunks is None:
        chunks = []
        
    if node.type == 'class_definition':
        name_node = node.child_by_field_name('name')
        class_name = name_node.text.decode('utf-8') if name_node else 'Unknown'
        
        chunks.append({
            'file_path': relative_path,
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'type': 'class',
            'code_snippet': f"# File: {relative_path}\n" + node.text.decode('utf-8')
        })
        
        for child in node.children:
            _walk_tree(child, relative_path, current_class=class_name, chunks=chunks)
            
    elif node.type == 'function_definition':
        header = f"# File: {relative_path}\n"
        if current_class:
            header += f"# Class: {current_class}\n"
            
        chunks.append({
            'file_path': relative_path,
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'type': 'function',
            'code_snippet': header + node.text.decode('utf-8')
        })
        
        for child in node.children:
            _walk_tree(child, relative_path, current_class=current_class, chunks=chunks)
            
    else:
        for child in node.children:
            _walk_tree(child, relative_path, current_class=current_class, chunks=chunks)
            
    return chunks

def chunk_python_file(file_path: str, root_dir: str) -> List[Dict[str, Any]]:
    """
    Reads a Python file, parses it via Tree-sitter, and returns semantic chunks.
    
    Args:
        file_path: Absolute path to the source file.
        root_dir: Root directory of the repository for path relativization.
        
    Returns:
        List[Dict[str, Any]]: List of discovered class/function chunks.
    """
    try:
        with open(file_path, 'rb') as f:
            source_code = f.read()
    except Exception:
        return []

    relative_path = os.path.relpath(file_path, root_dir)
    tree = parser.parse(source_code)
    
    return _walk_tree(tree.root_node, relative_path)
