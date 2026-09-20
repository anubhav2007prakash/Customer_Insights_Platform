"""Safe expression evaluator for ABAC policies using AST parsing."""
from __future__ import annotations

import ast
from typing import Any

SAFE_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Attribute,
    ast.Load,
    ast.Constant,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.Is,
    ast.IsNot,
)


class _EvalVisitor(ast.NodeVisitor):
    def __init__(self, context):
        self.context = context

    def generic_visit(self, node):
        if not isinstance(node, SAFE_NODES):
            raise ValueError(f"Unsafe expression node: {type(node).__name__}")
        return super().generic_visit(node)


def _resolve_name(name: str, user=None, resource=None, context=None):
    # support names like User.Department, Resource.Owner
    parts = name.split(".")
    if parts[0] in ("User", "user"):
        obj = user
        parts = parts[1:]
    elif parts[0] in ("Resource", "resource"):
        obj = resource
        parts = parts[1:]
    else:
        # fallback to context
        return context.get(parts[0]) if context else None

    for p in parts:
        if obj is None:
            return None
        obj = getattr(obj, p.lower(), None) if hasattr(obj, p.lower()) else getattr(obj, p, None)
    return obj


def _safe_eval(node: ast.AST, user=None, resource=None, context=None):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, user, resource, context)
    if isinstance(node, ast.BoolOp):
        vals = [_safe_eval(v, user, resource, context) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(vals)
        return any(vals)
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            return not _safe_eval(node.operand, user, resource, context)
    if isinstance(node, ast.Compare):
        left = _safe_eval(node.left, user, resource, context)
        for op, comparator in zip(node.ops, node.comparators):
            right = _safe_eval(comparator, user, resource, context)
            if isinstance(op, ast.Eq):
                if left != right:
                    return False
            elif isinstance(op, ast.NotEq):
                if left == right:
                    return False
            elif isinstance(op, ast.Lt):
                if not (left < right):
                    return False
            elif isinstance(op, ast.Gt):
                if not (left > right):
                    return False
            else:
                raise ValueError(f"Unsupported comparator: {type(op)}")
            left = right
        return True
    if isinstance(node, ast.Attribute):
        val = _safe_eval(node.value, user, resource, context)
        if val is None:
            return None
        attr = node.attr
        if isinstance(val, dict):
            return val.get(attr.lower()) if attr.lower() in val else val.get(attr)
        return getattr(val, attr.lower(), None) if hasattr(val, attr.lower()) else getattr(val, attr, None)
    if isinstance(node, ast.Name):
        return _resolve_name(node.id, user=user, resource=resource, context=context)
    if isinstance(node, ast.Constant):
        return node.value
    raise ValueError(f"Unsupported expression node: {type(node)}")


def evaluate_expression(expr: str, *, user=None, resource=None, context=None) -> bool:
    """Evaluate a boolean expression safely against provided user/resource/context."""
    try:
        tree = ast.parse(expr, mode="eval")
        _EvalVisitor(context).visit(tree)
        return bool(_safe_eval(tree, user=user, resource=resource, context=context or {}))
    except Exception:
        return False
