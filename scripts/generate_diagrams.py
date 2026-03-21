# scripts/ — repo-level Python utilities (diagram generation, etc.).
"""
Generate architecture and process flow diagrams for Agentic Node.
Output: architecture_flow.png, process_flow.png
Requires: matplotlib (pip install matplotlib)
Run from repo root: python scripts/generate_diagrams.py
"""
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
except ImportError:
    print("Install matplotlib: pip install matplotlib")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(REPO_ROOT, "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# Styling
BG = "#f8f6f4"
LAYER_BG = "#eeeeec"
BOX_FACE = "#ffffff"
BOX_EDGE = "#1a1a1a"
ARROW_COLOR = "#333333"
TEXT_COLOR = "#1a1a1a"
TITLE_FONTSIZE = 16
NODE_FONTSIZE = 10
SMALL_FONTSIZE = 9

# Standard node size
W, H = 2.0, 0.75


def _box(ax, x, y, w, h, label, fontsize=NODE_FONTSIZE, bold=False):
    """Draw a rounded box and centered text."""
    rect = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                          facecolor=BOX_FACE, edgecolor=BOX_EDGE, linewidth=1.6)
    ax.add_patch(rect)
    weight = "bold" if bold else "normal"
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, color=TEXT_COLOR, fontweight=weight, wrap=True)


def _arrow(ax, xy_from, xy_to, label=None):
    """Draw arrow from -> to, optionally with label."""
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="->", color=ARROW_COLOR, lw=2,
                               connectionstyle="arc3,rad=0"))
    if label:
        mid = ((xy_from[0] + xy_to[0]) / 2, (xy_from[1] + xy_to[1]) / 2)
        ax.text(mid[0], mid[1], label, fontsize=8, color="gray", ha="center", va="center")


def draw_architecture(ax):
    """High-level architecture: clear 3-layer structure."""
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)

    # Title
    ax.text(6, 9.5, "Agentic Node — High-Level Architecture", ha="center", va="center",
            fontsize=TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR)

    # Layer 1: Client / Presentation
    ax.add_patch(Rectangle((0.2, 7.0), 11.6, 1.6, facecolor=LAYER_BG, edgecolor="none", zorder=0))
    ax.text(0.5, 8.2, "Presentation", fontsize=9, color="gray", va="center", fontweight="bold")
    _box(ax, 2.5, 7.8, 1.6, 0.7, "User\nBrowser", SMALL_FONTSIZE)
    _box(ax, 5.5, 7.8, 2.2, 0.7, "Frontend\n(GitHub Pages)\nHTML / JavaScript", SMALL_FONTSIZE)
    _arrow(ax, (3.3, 7.8), (4.4, 7.8), "HTTPS")
    _arrow(ax, (4.4, 7.8), (6.6, 7.8), "API calls")

    # Layer 2: Application
    ax.add_patch(Rectangle((0.2, 3.8), 11.6, 2.8, facecolor=LAYER_BG, edgecolor="none", zorder=0))
    ax.text(0.5, 6.2, "Application", fontsize=9, color="gray", va="center", fontweight="bold")
    _box(ax, 6, 5.2, 2.8, 1.2, "Backend API\nFastAPI on Railway\n· LangGraph (query pipeline)\n· Sessions · Upload", SMALL_FONTSIZE)

    # Layer 3: Data & Services
    ax.add_patch(Rectangle((0.2, 0.4), 11.6, 3.0, facecolor=LAYER_BG, edgecolor="none", zorder=0))
    ax.text(0.5, 3.0, "Data & external services", fontsize=9, color="gray", va="center", fontweight="bold")
    _box(ax, 2.5, 1.8, 2.0, 0.8, "PostgreSQL\nSessions + Analytics DB", SMALL_FONTSIZE)
    _box(ax, 6, 1.8, 2.0, 0.8, "ChromaDB\nRAG vector store", SMALL_FONTSIZE)
    _box(ax, 9.5, 1.8, 2.0, 0.8, "OpenAI\nLLM + Embeddings", SMALL_FONTSIZE)

    # Arrows: Backend to data layer
    _arrow(ax, (4.6, 4.6), (2.5, 2.2))
    _arrow(ax, (5.4, 4.6), (6, 2.2))
    _arrow(ax, (7.4, 4.6), (9.5, 2.2))


def draw_system_architecture(ax):
    """System Architecture Diagram: layered view with clear boundaries and labels."""
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ax.set_facecolor(BG)

    # Title
    ax.text(7, 11.4, "System Architecture Diagram", ha="center", va="center",
            fontsize=TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR)
    ax.text(7, 10.85, "Agentic Node", ha="center", va="center", fontsize=11, color="gray")

    # Layer 1: Client (y 9.2 - 10.2)
    ax.add_patch(Rectangle((0.3, 9.0), 13.4, 1.4, facecolor="#e8e6e4", edgecolor="#ccc", linewidth=1, zorder=0))
    ax.text(0.6, 10.0, "Client", fontsize=10, color="gray", va="center", fontweight="bold")
    _box(ax, 3.5, 9.6, 2.0, 0.65, "User / Browser\n(HTTPS)", SMALL_FONTSIZE)

    # Layer 2: Presentation (y 7.2 - 8.6)
    ax.add_patch(Rectangle((0.3, 7.0), 13.4, 1.8, facecolor=LAYER_BG, edgecolor="#ccc", linewidth=1, zorder=0))
    ax.text(0.6, 8.5, "Presentation", fontsize=10, color="gray", va="center", fontweight="bold")
    _box(ax, 5, 7.9, 2.6, 0.7, "Frontend\nGitHub Pages\n(HTML, CSS, JavaScript)", SMALL_FONTSIZE)
    _arrow(ax, (3.5, 9.35), (3.8, 8.25), "HTTPS")
    _arrow(ax, (4.2, 8.25), (6.35, 7.9), "REST API")

    # Layer 3: Application (y 4.2 - 6.4)
    ax.add_patch(Rectangle((0.3, 4.0), 13.4, 2.6, facecolor=LAYER_BG, edgecolor="#ccc", linewidth=1, zorder=0))
    ax.text(0.6, 6.1, "Application", fontsize=10, color="gray", va="center", fontweight="bold")
    _box(ax, 7, 5.3, 3.2, 1.4,
         "Backend API (FastAPI)\nHosted on Railway\n\n· POST /api/query (LangGraph)\n· POST /api/upload (RAG ingest)\n· GET/POST/DELETE /api/sessions\n· GET /health",
         SMALL_FONTSIZE)
    _arrow(ax, (6.35, 7.55), (5.4, 6.65))
    _arrow(ax, (5.4, 6.65), (7, 6.65))
    ax.text(6.2, 7.15, "JSON", fontsize=8, color="gray", ha="center")

    # Layer 4: Data & external (y 0.4 - 3.4)
    ax.add_patch(Rectangle((0.3, 0.2), 13.4, 3.4, facecolor="#e8e6e4", edgecolor="#ccc", linewidth=1, zorder=0))
    ax.text(0.6, 3.2, "Data & External Services", fontsize=10, color="gray", va="center", fontweight="bold")

    _box(ax, 2.8, 2.0, 2.2, 0.85, "PostgreSQL\n· chat_sessions\n· chat_messages\n· departments, employees,\n  salaries, projects, sales", 8)
    _box(ax, 6.2, 2.0, 2.2, 0.85, "ChromaDB\n(Persistent)\n· documents collection\n· OpenAI embeddings\n· cosine similarity", 8)
    _box(ax, 9.6, 2.0, 2.2, 0.85, "OpenAI API\n· gpt-4o-mini (LLM)\n· text-embedding-3-small\n(embeddings)", 8)

    _arrow(ax, (5.4, 4.0), (2.8, 2.45))
    _arrow(ax, (5.8, 4.0), (6.2, 2.45))
    _arrow(ax, (8.2, 4.0), (9.6, 2.45))
    ax.text(4.0, 3.25, "SQL / session", fontsize=7, color="gray", ha="center")
    ax.text(6.0, 3.25, "vectors", fontsize=7, color="gray", ha="center")
    ax.text(8.9, 3.25, "completions", fontsize=7, color="gray", ha="center")


def draw_process_flow(ax):
    """Process flow: two clear columns (Query | Upload) with structured steps."""
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 18)
    ax.axis("off")
    ax.set_facecolor(BG)

    # Title
    ax.text(7, 17.2, "Agentic Node — Process Flow", ha="center", va="center",
            fontsize=TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR)
    ax.text(7, 16.6, "From user action to response", ha="center", va="center", fontsize=10, color="gray")

    # ========== QUERY PATH (left column, x ≈ 3.5) ==========
    ax.add_patch(Rectangle((0.3, 0.2), 6.2, 15.8, facecolor=LAYER_BG, edgecolor="#ccc", linewidth=0.8, zorder=0))
    ax.text(1, 15.4, "Query path (POST /api/query)", fontsize=10, fontweight="bold", color=TEXT_COLOR)

    cx = 3.5
    steps = [
        (15.0, "User submits question"),
        (14.2, "Session check (max 12 questions per chat)"),
        (13.3, "Intent classifier\n→ database_query | rag_query | general"),
    ]
    for y, label in steps:
        _box(ax, cx, y, 2.6, 0.65, label, SMALL_FONTSIZE)
    _arrow(ax, (cx, 14.68), (cx, 14.2))
    _arrow(ax, (cx, 13.98), (cx, 13.3))

    # Branch labels
    ax.text(1.8, 12.5, "database_query", fontsize=9, fontweight="bold", color=TEXT_COLOR)
    ax.text(3.5, 12.5, "rag_query", fontsize=9, fontweight="bold", color=TEXT_COLOR)
    ax.text(5.2, 12.5, "general", fontsize=9, fontweight="bold", color=TEXT_COLOR)

    # DB branch (left)
    db_steps = [(11.8, "SQL generator\n(schema only)"), (10.8, "Execute query\n(PostgreSQL)"),
                (9.8, "Chart recommender"), (8.8, "Chart generator\n(matplotlib)")]
    for y, label in db_steps:
        _box(ax, 1.8, y, 2.0, 0.6, label, SMALL_FONTSIZE)
    for i in range(len(db_steps) - 1):
        _arrow(ax, (1.8, db_steps[i][0] - 0.35), (1.8, db_steps[i + 1][0] + 0.35))
    _arrow(ax, (1.8, 12.15), (1.8, 12.1))
    _arrow(ax, (1.8, 8.45), (cx, 6.525))

    # RAG branch (center)
    _box(ax, cx, 11.5, 2.2, 0.6, "RAG search\n(ChromaDB + LLM)", SMALL_FONTSIZE)
    _arrow(ax, (cx, 12.95), (cx, 11.8))
    _arrow(ax, (cx, 11.2), (cx, 6.525))

    # General branch (right)
    _box(ax, 5.2, 11.0, 1.6, 0.5, "General answer\n(LLM)", SMALL_FONTSIZE)
    _arrow(ax, (cx, 12.95), (5.2, 11.25))
    _arrow(ax, (5.2, 10.75), (cx, 6.525))

    # Converge: Response generator
    _box(ax, cx, 6.2, 2.6, 0.65, "Response generator\n(summary, table, chart, or RAG answer)", SMALL_FONTSIZE)
    _arrow(ax, (cx, 5.875), (cx, 5.3))  # response gen bottom -> persist top
    _box(ax, cx, 5.0, 2.4, 0.6, "Persist to session (PostgreSQL)\nReturn JSON to frontend", SMALL_FONTSIZE)
    _arrow(ax, (cx, 4.7), (cx, 3.9))  # persist bottom -> end
    ax.text(cx, 3.2, "End (query)", fontsize=10, ha="center", fontweight="bold", color=TEXT_COLOR)

    # ========== UPLOAD PATH (right column, x ≈ 10) ==========
    ax.add_patch(Rectangle((7.5, 0.2), 6.2, 15.8, facecolor=LAYER_BG, edgecolor="#ccc", linewidth=0.8, zorder=0))
    ax.text(8.2, 15.4, "Upload path (POST /api/upload)", fontsize=10, fontweight="bold", color=TEXT_COLOR)

    ux = 10.5
    upload_steps = [
        (14.2, "User uploads file\n(PDF / DOCX / TXT)"),
        (13.0, "Save to uploads/"),
        (11.8, "Load document & chunk text"),
        (10.6, "Embed chunks (OpenAI)"),
        (9.4, "Store in ChromaDB"),
        (8.2, "Return success (chunks stored)"),
    ]
    for y, label in upload_steps:
        _box(ax, ux, y, 2.4, 0.6, label, SMALL_FONTSIZE)
    for i in range(len(upload_steps) - 1):
        _arrow(ax, (ux, upload_steps[i][0] - 0.35), (ux, upload_steps[i + 1][0] + 0.35))
    _arrow(ax, (ux, 15.0), (ux, 14.55))
    ax.text(ux, 7.4, "End (upload)", fontsize=10, ha="center", fontweight="bold", color=TEXT_COLOR)


def main():
    # Architecture
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.patch.set_facecolor(BG)
    draw_architecture(ax)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "architecture_flow.png")
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print("Saved:", path)

    # System Architecture Diagram
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    draw_system_architecture(ax)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "system_architecture.png")
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print("Saved:", path)

    # Process flow
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    fig.patch.set_facecolor(BG)
    draw_process_flow(ax)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "process_flow.png")
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print("Saved:", path)
    print("Done. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
