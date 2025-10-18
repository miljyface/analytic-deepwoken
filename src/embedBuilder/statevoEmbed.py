import numpy as np
import plugins.dwbapi as dwb
import matplotlib.pyplot as plt
from plugins.shrineoforder import order
from matplotlib.lines import Line2D
import io

def statevograph(build):
    playerStats = {"Race": build.race, "PointsSpent": 0}
    flatpre = build.flatpre
    flatpost = build.flatpost
    ordered_stats = order(build.flatpre.copy(), playerStats)

    categories = [
        key for key in flatpre.keys()
        if flatpre[key] != 0 or ordered_stats[key] != 0 or flatpost[key] != 0
    ]
    gap = 4
    y = np.arange(len(categories)) * gap

    pre_values = [flatpre[key] for key in categories]
    ord_values = [ordered_stats[key] for key in categories]
    post_values = [flatpost[key] for key in categories]

    plt.figure(figsize=(11, len(categories)*0.55 + 2))
    color_pre = "#A31F34"           # MIT Red
    color_ord = "#5A5A5A"           # Deep Gray
    color_post = "#191919"          # Almost Black
    color_reinvest = "#007BFF88"      # Vibrant Pink, semi-transparent
    offset = 1
    lw = 2

    ys_pre  = y - offset
    ys_ord  = y
    ys_post = y + offset

    new_categories = [
        f"{cat} ({postval})" for cat, postval in zip(categories, post_values)
    ]

    plt.grid(axis='x', alpha=0.2, linewidth=1.0)

    for yy, val in zip(ys_pre, pre_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_pre, linewidth=lw)
            plt.plot(val, yy, 'o', color=color_pre, markersize=9)
            plt.text(val + 2, yy, str(val), va='center', ha='left', color=color_pre, fontsize=13, weight='bold')
    for yy, val in zip(ys_ord, ord_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_ord, linewidth=lw)
            plt.plot(val, yy, '^', color=color_ord, markersize=9)
            plt.text(val + 3, yy, str(val), va='center', ha='left', color=color_ord, fontsize=13, weight='bold')
    for yy, val in zip(ys_post, post_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_post, linewidth=lw)
            plt.plot(val, yy, 's', color=color_post, markersize=9)
            plt.text(val + 4, yy, str(val), va='center', ha='left', color=color_post, fontsize=13, weight='bold')


    for yy, ordv, postv in zip(ys_ord, ord_values, post_values):
        if ordv != postv:
            x0, x1 = sorted([ordv, postv])
            plt.plot([x0, x1], [yy, yy], color=color_reinvest, linewidth=11, alpha=0.35, solid_capstyle='projecting')

    plt.yticks(y, new_categories, fontsize=14)
    plt.ylim(min(ys_pre)-gap*0.6, max(ys_post)+gap*0.9)
    plt.xlabel('Stat Value', fontsize=15)
    plt.xlim(-2, max(pre_values+ord_values+post_values) + 20)
    plt.title('Stat Distribution and Evolution', fontsize=19, weight='semibold', pad=24)

    handles = [
        Line2D([0], [0], color=color_pre, marker='o', linestyle='-', linewidth=lw, markersize=9, label='Pre-Shrine'),
        Line2D([0], [0], color=color_ord, marker='^', linestyle='-', linewidth=lw, markersize=9, label='Order'),
        Line2D([0], [0], color=color_post, marker='s', linestyle='-', linewidth=lw, markersize=9, label='Post-Shrine'),
        Line2D([0], [0], color=color_reinvest, marker=None, linestyle='-', linewidth=11, alpha=0.35, label='Reinvest interval')
    ]
    plt.legend(handles=handles, loc='lower right', frameon=True, fontsize=13)
    plt.tight_layout(pad=2)
    plt.box(False)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf
