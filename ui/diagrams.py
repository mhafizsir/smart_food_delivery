"""Gambar struktur data dengan graphviz."""
import pandas as pd
import streamlit as st

from core.linear import LinkedQueue
from ui.common import CHAIN_LIMIT, PRIORITY_FILL, TREE_LIMIT, rupiah


def _clean(text):
    return str(text).replace('"', "'")


def chain_dot(labels, first_tag, last_tag, rankdir="LR", end_null=False, limit=CHAIN_LIMIT):
    """Rantai node untuk linked list, queue, dan stack. Rantai panjang diringkas jadi awal ... akhir."""
    if len(labels) > limit:
        labels = labels[:limit - 1] + ["..."] + labels[-1:]
    lines = ["digraph chain {", f"rankdir={rankdir};",
             'node [shape=box, style="rounded,filled", fillcolor="#e7f1ff", fontname="Helvetica"];']
    last = len(labels) - 1
    for i, label in enumerate(labels):
        tags = []
        if label != "...":
            if i == 0:
                tags.append(first_tag)
            if i == last:
                tags.append(last_tag)
        text = _clean(label)
        if tags:
            text += "\\n[" + " / ".join(tags) + "]"
        fill = "#ffffff" if label == "..." else "#e7f1ff"
        lines.append(f'n{i} [label="{text}", fillcolor="{fill}"];')
        if i:
            lines.append(f"n{i - 1} -> n{i};")
    if end_null and labels:
        lines.append('null [label="NULL", shape=plaintext, style=""];')
        lines.append(f"n{last} -> null;")
    lines.append("}")
    return "\n".join(lines)


def order_node(order):
    return f"#{order.id} {order.customer}\\n{order.priority} {order.status}"


def action_node(action):
    return f"{action['type']}\\n#{action['order'].id}"


def show_chain(items, label_of, first_tag, last_tag, empty_message, rankdir="LR", end_null=False):
    items = list(items)
    if not items:
        st.info(empty_message)
        return
    labels = [label_of(item) for item in items]
    st.graphviz_chart(chain_dot(labels, first_tag, last_tag, rankdir=rankdir, end_null=end_null))
    if len(items) > CHAIN_LIMIT:
        st.caption(f"Total {len(items)} node, gambar diringkas.")


def heap_dot(items):
    lines = ["digraph heap {", 'node [shape=box, style="rounded,filled", fontname="Helvetica"];']
    for i, order in enumerate(items[:TREE_LIMIT]):
        label = f"[{i}] #{order.id} {order.priority}"
        lines.append(f'n{i} [label="{label}", fillcolor="{PRIORITY_FILL[order.priority]}"];')
        if i:
            lines.append(f"n{(i - 1) // 2} -> n{i};")
    lines.append("}")
    return "\n".join(lines)


def bst_dot(root, limit=TREE_LIMIT):
    lines = ["digraph bst {", 'node [shape=box, style="rounded,filled", fillcolor="#e7f1ff", fontname="Helvetica"];']
    pending = LinkedQueue()  # level order memakai queue buatan sendiri
    drawn = 0
    if root:
        pending.enqueue(root)
    while not pending.is_empty() and drawn < limit:
        node = pending.dequeue()
        drawn += 1
        names = [item.name for item in node.items]
        shown = ", ".join(names[:3])
        if len(names) > 3:
            shown += f" +{len(names) - 3}"
        lines.append(f'n{id(node)} [label="{rupiah(node.key)}\\n{_clean(shown)}"];')
        for side, child in (("L", node.left), ("R", node.right)):
            if child and drawn + len(pending) < limit:
                lines.append(f'n{id(node)} -> n{id(child)} [label="{side}"];')
                pending.enqueue(child)
    lines.append("}")
    return "\n".join(lines)


def heap_rows(heap):
    rows = []
    for i, o in enumerate(heap.as_array()):
        parent = "-"
        if i:
            parent = str((i - 1) // 2)
        rows.append({
            "Index": i, "Parent": parent, "Order": f"#{o.id}",
            "Prioritas": o.priority, "Key": str(heap.key_of(o)),
        })
    return rows


def show_heap(heap):
    items = heap.as_array()
    if not items:
        st.info("Heap kosong.")
        return
    tree, array = st.columns(2)
    tree.graphviz_chart(heap_dot(items))
    array.dataframe(pd.DataFrame(heap_rows(heap)), hide_index=True)
    array.caption(f"Heap property valid: {heap.is_valid()}. Anak index i ada di 2i+1 dan 2i+2.")
    if len(items) > TREE_LIMIT:
        tree.caption(f"Gambar menampilkan {TREE_LIMIT} dari {len(items)} node.")
