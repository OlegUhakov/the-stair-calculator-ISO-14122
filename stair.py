import math

import streamlit as st

st.set_page_config(page_title="ISO 14122-3 Stair Calculator", layout="wide")

st.title("Industrial Stair Calculator")
st.caption("Calculation and verification per ISO 14122-3 (Safety of machinery)")

col_sidebar, col_main = st.columns([1, 2])

with col_sidebar:
    st.header("Input Parameters")

    H = st.number_input(
        "Total rise height (H), mm", min_value=300, max_value=4000, value=1500, step=5,
    )

    Pup = st.number_input("Pup (vertical top offset), mm", min_value=0, max_value=1000, value=0, step=5)
    Pdown = st.number_input("Pdown (vertical bottom offset), mm", min_value=0, max_value=1000, value=0, step=5)
    B = st.number_input("Bottom platform (B), mm", min_value=0, max_value=1000, value=0, step=5)
    r = st.number_input("Overlap (r), mm", min_value=0, max_value=50, value=10, step=1)

    st.markdown("---")

    N = st.slider("Steps (N)", min_value=1, max_value=30, value=8)
    g = st.slider("Tread (g), mm", min_value=150, max_value=320, step=1, value=280)

    def offs_L(a_deg):
        a_r = math.radians(a_deg)
        return (B + Pdown + Pup) / math.tan(a_r) if math.tan(a_r) > 0 else 0

    H_net = H - B - Pdown - Pup
    g_actual = g
    h_actual = H_net / N
    angle = math.degrees(math.atan(h_actual / g_actual))
    t_total = g + r
    L = g_actual * (N - 1) + offs_L(angle)

    st.markdown("---")
    st.number_input("Riser (h), mm", value=float(round(h_actual, 1)), disabled=True, format="%.1f", key="__dh")
    st.number_input("Tread (g), mm", value=float(g_actual), disabled=True, format="%.1f", key="__dg")
    st.number_input("Total tread (t), mm", value=float(t_total), disabled=True, format="%.1f", key="__dt")
    st.number_input("L (horizontal run), mm", value=float(round(L, 0)), disabled=True, format="%.0f", key="__dl")

    st.markdown("---")
    st.subheader("Step spacing")
    step_diagonal = math.sqrt(g_actual ** 2 + h_actual ** 2)
    st.number_input("Along slope, mm", value=float(round(step_diagonal, 1)), disabled=True, format="%.1f", key="__ddiag")

    st.markdown("---")
    st.subheader("Step offsets")
    angle_rad = math.radians(angle)
    Ad = (B + Pdown) / math.sin(angle_rad) if math.sin(angle_rad) > 0 else 0
    Aup = Pup / math.sin(angle_rad) if math.sin(angle_rad) > 0 else 0
    st.number_input("Ad (along stair, bottom), mm", value=float(round(Ad, 1)), disabled=True, format="%.1f")
    st.number_input("Aup (along stair, top), mm", value=float(round(Aup, 1)), disabled=True, format="%.1f")

    if angle < 45:
        stair_type = "Stairs (20\u00b0\u201345\u00b0)"
        angle_min_ok, angle_max_ok = 20, 45
        g_min_ok = 200
        h_max_ok = 240
        blondel_applies = True
    else:
        stair_type = "Stepladders (45\u00b0\u201375\u00b0)"
        angle_min_ok, angle_max_ok = 45, 75
        g_min_ok = 150
        h_max_ok = 250
        blondel_applies = False

    blondel = g_actual + 2 * h_actual

    is_valid_blondel = 600 <= blondel <= 660 if blondel_applies else True
    is_valid_angle = angle_min_ok <= angle <= angle_max_ok
    is_valid_h = h_actual <= h_max_ok
    is_valid_g = g_actual >= g_min_ok

    is_all_valid = all(
        [is_valid_blondel, is_valid_angle, is_valid_h, is_valid_g]
    )

with col_main:
    col_draw, col_metrics = st.columns([3, 1])

    with col_metrics:
        st.subheader("Parameters")
        if B > 0:
            st.metric("Platform (B)", f"{B} mm")
        if Pdown > 0:
            st.metric("Pdown", f"{Pdown} mm")
        st.metric("Steps (N)", f"{N}")
        st.metric("Riser (h)", f"{h_actual:.1f} mm")
        st.metric("Tread (g)", f"{g_actual:.1f} mm")
        st.metric("L (horizontal run)", f"{L:.0f} mm")
        st.metric("Angle (\u03b1)", f"{angle:.1f}\u00b0")
        st.metric("Along slope", f"{step_diagonal:.1f} mm")
        st.metric("Total tread (t)", f"{t_total:.1f} mm")
        st.metric("Overlap (r)", f"{r} mm")

    with col_draw:
        svg_w = 800
        svg_h = 500
        padding = 50

        max_real_w = max(L, 500)
        max_real_h = max(H, 500)

        scale_x = (svg_w - padding * 2) / max_real_w
        scale_y = (svg_h - padding * 2) / max_real_h
        scale = min(scale_x, scale_y)

        def to_svg(x, y):
            svg_x = padding + x * scale
            svg_y = (svg_h - padding) - y * scale
            return svg_x, svg_y

        svg_lines = []

        x_start, y_start = to_svg(-200, 0)
        x_floor_end, _ = to_svg(L + 200, 0)
        svg_lines.append(
            f'<line x1="{x_start}" y1="{y_start}" x2="{x_floor_end}" y2="{y_start}" '
            f'stroke="#94a3b8" stroke-width="2" stroke-dasharray="5,5" />'
        )

        a_rad_svg = math.radians(angle)
        x_off = ((B + Pdown) / math.tan(a_rad_svg)) if a_rad_svg > 0 and math.tan(a_rad_svg) > 0 else 0

        if B > 0:
            bw = 60 * scale
            bh = B * scale
            bx, by = to_svg(0, B)
            svg_lines.append(
                f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                f'fill="#94a3b8" stroke="#64748b" stroke-width="2" />'
            )
            svg_lines.append(
                f'<text x="{bx + bw + 5}" y="{by + bh / 2 + 4}" fill="#64748b" '
                f'font-family="sans-serif" font-size="11">B = {B} mm</text>'
            )

        if Pdown > 0:
            pd_x1, pd_y1 = to_svg(0, B)
            _, pd_y2 = to_svg(0, B + Pdown)
            svg_lines.append(
                f'<line x1="{pd_x1}" y1="{pd_y1}" x2="{pd_x1}" y2="{pd_y2}" '
                f'stroke="#22c55e" stroke-width="2" />'
            )
            svg_lines.append(
                f'<text x="{pd_x1 + 5}" y="{(pd_y1 + pd_y2) / 2}" fill="#22c55e" '
                f'font-family="sans-serif" font-size="11">Pdown = {Pdown:.0f} mm</text>'
            )

        step_color = "#3b82f6" if is_all_valid else "#ef4444"
        for i in range(N):
            x_curr = x_off + i * g_actual
            y_curr = B + Pdown + i * h_actual

            sx, sy = to_svg(x_curr, y_curr)
            s_g = g_actual * scale
            s_h = h_actual * scale

            svg_lines.append(
                f'<line x1="{sx}" y1="{sy}" x2="{sx + s_g}" y2="{sy}" '
                f'stroke="{step_color}" stroke-width="4" stroke-linecap="round" />'
            )

            if i < N - 1:
                svg_lines.append(
                    f'<line x1="{sx + s_g}" y1="{sy}" x2="{sx + s_g}" y2="{sy - s_h}" '
                    f'stroke="#cbd5e1" stroke-width="1" stroke-dasharray="2,2" />'
                )

        x_last = x_off + (N - 1) * g_actual
        y_last = B + Pdown + (N - 1) * h_actual
        x1_t, y1_t = to_svg(x_off, B + Pdown)
        x2_t, y2_t = to_svg(x_last, y_last)
        svg_lines.append(
            f'<line x1="{x1_t}" y1="{y1_t}" x2="{x2_t}" y2="{y2_t}" '
            f'stroke="#1e293b" stroke-width="6" opacity="0.7" />'
        )

        x_h_line, y_h_bottom = to_svg(L + 100, 0)
        _, y_h_top = to_svg(L + 100, H)
        svg_lines.append(
            f'<line x1="{x_h_line}" y1="{y_h_bottom}" x2="{x_h_line}" y2="{y_h_top}" '
            f'stroke="#64748b" stroke-width="1.5" />'
        )
        svg_lines.append(
            f'<text x="{x_h_line + 10}" y="{(y_h_bottom + y_h_top) / 2}" '
            f'fill="#64748b" font-family="sans-serif" font-size="12">H = {H} mm</text>'
        )

        x_l_left, y_l_line = to_svg(0, -100)
        x_l_right, _ = to_svg(L, -100)
        svg_lines.append(
            f'<line x1="{x_l_left}" y1="{y_l_line}" x2="{x_l_right}" y2="{y_l_line}" '
            f'stroke="#64748b" stroke-width="1.5" />'
        )
        svg_lines.append(
            f'<text x="{(x_l_left + x_l_right) / 2 - 30}" y="{y_l_line + 15}" '
            f'fill="#64748b" font-family="sans-serif" font-size="12">L = {L:.0f} mm</text>'
        )

        if Pup > 0:
            px1, py1 = to_svg(x_last + g_actual, H - Pup)
            _, py2 = to_svg(x_last + g_actual, H)
            svg_lines.append(
                f'<line x1="{px1}" y1="{py1}" x2="{px1}" y2="{py2}" '
                f'stroke="#f97316" stroke-width="2" />'
            )
            svg_lines.append(
                f'<text x="{px1 + 5}" y="{(py1 + py2) / 2}" fill="#f97316" '
                f'font-family="sans-serif" font-size="11">Pup = {Pup:.0f} mm</text>'
            )

        x_a, y_a = to_svg(80, 20)
        svg_lines.append(
            f'<text x="{x_a}" y="{y_a}" fill="#0f172a" font-family="sans-serif" '
            f'font-weight="bold" font-size="14">{angle:.1f}\u00b0</text>'
        )

        svg_content = "\n".join(svg_lines)
        svg_wrapper = f"""
        <svg width="{svg_w}" height="{svg_h}" style="background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {svg_content}
        </svg>
        """

        st.subheader("Side View")
        st.components.v1.html(svg_wrapper, height=svg_h + 20)

    if blondel_applies:
        st.info(
            f"**Blondel formula:** calculated value is **{blondel:.1f} mm** "
            f"(ISO range: 600\u2013660 mm)."
        )

    st.markdown("---")
    st.subheader("Compliance")

    st.info(f"Detected type: **{stair_type}**")

    if is_all_valid:
        st.success("Fully complies with requirements!")
    else:
        st.error("Violations detected:")
        if not is_valid_angle:
            st.warning(
                f"Inclination angle {angle:.1f}\u00b0 outside allowed range ({angle_min_ok}\u00b0\u2013{angle_max_ok}\u00b0)."
            )
        if not is_valid_blondel:
            st.warning(
                f"Blondel formula {blondel:.0f} mm outside allowed range (600\u2013660 mm)."
            )
        if not is_valid_g:
            st.warning(f"Tread depth {g_actual:.1f} mm too small (min. {g_min_ok} mm).")
        if not is_valid_h:
            st.warning(
                f"Riser height {h_actual:.1f} mm exceeds max allowed ({h_max_ok} mm)."
            )

st.markdown("---")
st.caption("Version: 1.8")
