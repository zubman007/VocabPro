"""Visual identities for charts; independent of Tk and data calculations."""
STYLES = {
    "Number of words to review next days": ("#416d58", "#e0e5d2"),
    "Growth of the vocabulary": ("#9e6f3a", "#e8dec5"),
    "Vocabulary by Part of Speech": ("#60794e", "#e2e4ce"),
    "Vocabulary trailing successes": ("#416d58", "#e0e5d2"),
    "Conjugation trailing successes": ("#9e6650", "#e7d4c2"),
}


def style_chart(fig, ax, name, title, label_size):
    accent, surface = STYLES[name]
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)
    ax.set_title(title, loc="left", fontsize=18, fontweight="bold", color=accent, pad=22)
    ax.set_axisbelow(True)
    ax.grid(True, axis="y", color="#b7b49a", alpha=0.35, linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#bbb69b")
    ax.tick_params(colors="#5e6450", axis="both", length=0)
    ax.tick_params(axis="x", rotation=35 if "days" in name or "Growth" in name else 0,
                   labelsize=min(label_size, 12))
    ax.yaxis.label.set_color("#5e6450")
    ax.xaxis.label.set_color("#5e6450")
    for line in ax.lines:
        line.set_color(accent)
        line.set_linewidth(2.5)
    if "trailing successes" in name:
        for bar in ax.patches:
            bar.set_facecolor(accent)
            bar.set_edgecolor(surface)
            bar.set_linewidth(1.5)
            bar.set_alpha(0.85)
        if len(ax.patches) <= 18:
            for container in ax.containers:
                ax.bar_label(container, fmt="%.0f", padding=4, color=accent, fontsize=10)
        ax.margins(y=0.16)
    fig.tight_layout(pad=2.2)
