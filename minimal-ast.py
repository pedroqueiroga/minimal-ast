import ast

with open('./example03.py') as f:
    source = ''.join(f.readlines())


class MinimalExtractor(ast.NodeVisitor):
    required_context = set()
    built_context = set()

    def __init__(self, source, bad_context):
        if isinstance(source, str):
            self.source_node = ast.parse(source)
        elif isinstance(source, ast.Module):
            self.source_node = source
        self.bad_context = bad_context

    def extract(self, isname=False):
        visited_nodes = self.generic_visit(self.source_node, init=True)
        for node in filter(
            lambda n: isinstance(n, ast.FunctionDef), visited_nodes
        ):
            self.built_context.add(node.name)

        extracted_definitions = []
        for required in self.required_context:
            extracted = NameExtractor(
                self.source_node, required, self.built_context
            ).extract()
            definitions = list(
                filter(lambda d: isinstance(d, ast.AST), extracted)
            )
            if len(definitions) > 0:
                extracted_definitions.extend(definitions)
            for definition in definitions:
                self.built_context.add(definition.name)

        return ast.Module(
            self.move_imports_up(extracted_definitions + visited_nodes),
            self.source_node.type_ignores,
        )

    def move_imports_up(self, definitions):
        return sorted(
            definitions,
            key=lambda d: not (
                isinstance(d, ast.Import) or isinstance(d, ast.ImportFrom)
            ),
        )

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if (
                node.id not in self.built_context
                and node.id not in dir(__builtins__)
                and node.id != self.bad_context
            ):
                self.required_context.add(node.id)

        if isinstance(node.ctx, ast.Store):
            if node.id in self.required_context:
                self.built_context.add(node.id)

    def visit_FunctionDef(self, node):
        if node.name != self.bad_context:
            return None

        for arg in (
            (node.args.posonlyargs or [])
            + (node.args.args or [])
            + (node.args.vararg or [])
            + (node.args.kwonlyargs or [])
            + (node.args.kwarg or [])
        ):
            self.built_context.add(arg.arg)

        self.generic_visit(node)
        return node

    def generic_visit(self, node, init=False):
        child_nodes = ast.iter_child_nodes(node)
        visited_nodes = []

        for child_node in child_nodes:
            if init and not isinstance(child_node, ast.FunctionDef):
                continue

            visited = self.visit(child_node)
            if isinstance(visited, ast.AST):
                visited_nodes.append(visited)

        return visited_nodes


class NameExtractor(ast.NodeVisitor):
    def __init__(self, node, name, global_context):
        self.source_node = node
        self.name = name
        self.global_context = global_context

    def extract(self):
        return self.generic_visit(self.source_node)

    def visit_Import(self, node):
        if (
            len(
                list(filter(lambda alias: alias.name == self.name, node.names))
            )
            > 0
        ):
            return node
        return None

    def visit_ImportFrom(self, node):
        if (
            len(
                list(filter(lambda alias: alias.name == self.name, node.names))
            )
            > 0
        ):
            return node
        return None

    def visit_FunctionDef(self, node):
        if node.name != self.name:
            return None

        local_context = set()

        for arg in (
            (node.args.posonlyargs or [])
            + (node.args.args or [])
            + (node.args.vararg or [])
            + (node.args.kwonlyargs or [])
            + (node.args.kwarg or [])
        ):
            local_context.add(arg.arg)

        required_nodes = self.generic_visit(node)

        self.global_context.add(node.name)

        return node, list(
            filter(
                lambda n: n not in local_context
                and n not in self.global_context,
                required_nodes,
            )
        )

    def visit_Name(self, node):
        if node.id == self.name and isinstance(node.ctx, ast.Store):
            return node
        if isinstance(node.ctx, ast.Load):
            return node.id
        return None

    def generic_visit(self, node):
        child_nodes = ast.iter_child_nodes(node)
        visited_nodes = []

        for child_node in child_nodes:
            visited = self.visit(child_node)
            if isinstance(visited, ast.AST) or isinstance(visited, str):
                visited_nodes.append(visited)
            elif (
                isinstance(visited, list)
                and len(visited) > 0
                and isinstance(visited[0], str)
            ):
                visited_nodes.extend(visited)
            elif (
                isinstance(visited, tuple)
                and len(visited) == 2
                and isinstance(visited[0], ast.AST)
                and isinstance(visited[1], list)
            ):
                visited_nodes.append(visited[0])
                for required in visited[1]:
                    extracted = NameExtractor(
                        self.source_node, required, self.global_context
                    ).extract()
                    definitions = list(
                        filter(lambda d: isinstance(d, ast.AST), extracted)
                    )
                    if len(definitions) > 0:
                        visited_nodes.extend(definitions)

        return visited_nodes


me = MinimalExtractor(source, 'calculate')
print(ast.unparse(me.extract()))
