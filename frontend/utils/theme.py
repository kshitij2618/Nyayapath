"""
Visual identity for NyayaPath.

Streamlit's config.toml can only set a handful of flat colors — it can't
give you custom fonts, gradients, card shadows, or hover states. So this
module injects real CSS via st.markdown(unsafe_allow_html=True) on top of
that base theme.

Selectors below target Streamlit's data-testid attributes rather than its
internal class names, because internal class names can change between
Streamlit versions.

If you want to change the look later, every important value lives in the
TOKENS dict.
"""

import streamlit as st


# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------

TOKENS = {
    # --- color -------------------------------------------------------------

    "ink": "#17233E",
    "indigo_dark": "#101A31",

    "marigold": "#E2932E",
    "marigold_dark": "#C1770F",

    "paper": "#F5F7F1",
    "card": "#FFFFFF",

    "border": "#E3E0D3",
    "muted": "#5B6470",

    "success_bg": "#EAF4EC",
    "warning_bg": "#FBF1E3",

    # --- type --------------------------------------------------------------

    "font_display": "'Fraunces', Georgia, serif",
    "font_body": "'Hind', 'Noto Sans', sans-serif",
    "font_mono": "'IBM Plex Mono', monospace",
}


# --------------------------------------------------------------------------
# Product pipeline
# --------------------------------------------------------------------------

PIPELINE_STAGES = [
    ("Understand", ["input", "advice"]),
    ("Ask", ["questions", "anything_else"]),
    ("Ground & Explain", ["result"]),
    ("Prepare", ["draft"]),
]


# --------------------------------------------------------------------------
# Inject theme
# --------------------------------------------------------------------------

def inject_theme():

    t = TOKENS

    st.markdown(
        f"""
        <style>

        /* ==============================================================
           GLOBAL FONT + TEXT
           ============================================================== */

        @import url(
            'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Hind:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap'
        );

        html,
        body,
        [class*="css"] {{
            font-family: {t['font_body']};
            color: {t['ink']};
        }}


        /* ==============================================================
           APPLICATION BACKGROUND
           ============================================================== */

        .stApp {{
            background: {t['paper']};
            color: {t['ink']};
        }}

        [data-testid="stAppViewContainer"] {{
            background: {t['paper']};
            color: {t['ink']};
        }}


        /* ==============================================================
           GENERAL TEXT VISIBILITY
           
           This is the important fix for the white-text-on-light-
           background problem.
           ============================================================== */

        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] li {{
            color: {t['ink']};
        }}

        [data-testid="stMarkdownContainer"] {{
            color: {t['ink']};
        }}

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] li {{
            color: {t['ink']};
        }}


        /* ==============================================================
           HEADINGS
           ============================================================== */

        h1,
        h2,
        h3,
        h4,
        h5,

        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5 {{
            font-family: {t['font_display']};
            color: {t['ink']} !important;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}


        /* ==============================================================
           CAPTIONS
           ============================================================== */

        [data-testid="stCaptionContainer"] {{
            font-family: {t['font_mono']};
            color: {t['muted']} !important;
            letter-spacing: 0.01em;
        }}


        /* ==============================================================
           WIDGET LABELS
           ============================================================== */

        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label {{
            color: {t['ink']} !important;
            font-family: {t['font_body']};
        }}


        /* ==============================================================
           TEXT INPUTS / TEXT AREAS
           ============================================================== */

        textarea,
        input[type="text"],
        input[type="number"],
        [data-baseweb="textarea"] textarea {{
            border-radius: 10px !important;

            border: 1.5px solid {t['border']} !important;

            font-family: {t['font_body']} !important;

            color: {t['ink']} !important;

            background: {t['card']} !important;
        }}

        textarea:focus,
        input[type="text"]:focus,
        input[type="number"]:focus,
        [data-baseweb="textarea"] textarea:focus {{
            border-color: {t['marigold']} !important;

            box-shadow:
                0 0 0 3px rgba(226, 147, 46, 0.15) !important;
        }}

        textarea::placeholder,
        input[type="text"]::placeholder,
        input[type="number"]::placeholder {{
            color: {t['muted']} !important;
            opacity: 1 !important;
        }}


        /* ==============================================================
           SELECTBOX / DROPDOWN TEXT
           ============================================================== */

        [data-baseweb="select"] {{
            color: {t['ink']} !important;
        }}

        [data-baseweb="select"] div {{
            color: {t['ink']};
        }}


        /* ==============================================================
           PRIMARY BUTTON
           ============================================================== */

        button[kind="primary"] {{
            background:
                linear-gradient(
                    135deg,
                    {t['marigold']},
                    {t['marigold_dark']}
                );

            border: none;

            color: white !important;

            font-weight: 600;

            border-radius: 10px;

            padding: 0.55em 1.4em;

            box-shadow:
                0 2px 8px rgba(226, 147, 46, 0.35);

            transition:
                transform 0.12s ease,
                box-shadow 0.12s ease;
        }}

        button[kind="primary"]:hover {{
            transform: translateY(-1px);

            box-shadow:
                0 4px 14px rgba(226, 147, 46, 0.45);
        }}

        button[kind="primary"] p,
        button[kind="primary"] span {{
            color: white !important;
        }}


        /* ==============================================================
           SECONDARY BUTTON
           ============================================================== */

        button[kind="secondary"] {{
            background: {t['card']};

            border: 1.5px solid {t['ink']};

            color: {t['ink']} !important;

            font-weight: 500;

            border-radius: 10px;
        }}

        button[kind="secondary"]:hover {{
            background: {t['ink']};

            color: white !important;
        }}

        button[kind="secondary"] p,
        button[kind="secondary"] span {{
            color: inherit !important;
        }}


        /* ==============================================================
           BORDERED CONTAINERS
           st.container(border=True)
           ============================================================== */

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {t['card']};

            border: 1px solid {t['border']} !important;

            border-top: 3px solid {t['ink']} !important;

            border-radius: 12px !important;

            box-shadow:
                0 1px 3px rgba(23, 35, 62, 0.06);

            padding: 0.25rem 0.25rem;

            margin-bottom: 0.75rem;
        }}


        /* ==============================================================
           ALERT / INFO / WARNING BOXES
           ============================================================== */

        [data-testid="stAlertContainer"] {{
            border-radius: 10px;

            font-family: {t['font_body']};

            color: {t['ink']} !important;
        }}

        [data-testid="stAlertContainer"] p,
        [data-testid="stAlertContainer"] span {{
            color: {t['ink']} !important;
        }}


        /* ==============================================================
           PROGRESS STEPPER
           ============================================================== */

        .nyp-stepper {{
            display: flex;

            justify-content: space-between;

            margin:
                0.5rem 0
                1.75rem 0;
        }}

        .nyp-step {{
            flex: 1;

            text-align: center;

            font-family: {t['font_mono']};

            font-size: 0.72rem;

            letter-spacing: 0.04em;

            text-transform: uppercase;

            color: {t['muted']};

            position: relative;

            padding-top: 14px;
        }}

        .nyp-step::before {{
            content: "";

            position: absolute;

            top: 0;

            left: 0;

            right: 0;

            height: 3px;

            background: {t['border']};

            border-radius: 2px;
        }}

        .nyp-step.active {{
            color: {t['ink']};

            font-weight: 700;
        }}

        .nyp-step.active::before {{
            background:
                linear-gradient(
                    90deg,
                    {t['marigold']},
                    {t['marigold_dark']}
                );
        }}

        .nyp-step.done::before {{
            background: {t['ink']};
        }}


        /* ==============================================================
           HEADER
           ============================================================== */

        .nyp-header {{
            background:
                linear-gradient(
                    120deg,
                    {t['ink']},
                    {t['indigo_dark']}
                );

            border-radius: 16px;

            padding:
                1.4rem
                1.6rem;

            margin-bottom: 1.5rem;

            box-shadow:
                0 4px 18px rgba(16, 26, 49, 0.25);
        }}

        .nyp-header h1 {{
            color: white !important;

            font-family: {t['font_display']};

            font-size: 1.6rem;

            margin: 0;
        }}

        .nyp-header p {{
            color: rgba(255, 255, 255, 0.72) !important;

            font-family: {t['font_body']};

            margin:
                0.2rem
                0
                0
                0;

            font-size: 0.9rem;
        }}


        /* ==============================================================
           LINKS
           ============================================================== */

        a {{
            color: {t['marigold_dark']};
        }}

        a:hover {{
            color: {t['marigold']};
        }}


        /* ==============================================================
           STREAMLIT FOOTER
           ============================================================== */

        footer {{
            visibility: hidden;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

def render_header(
    app_title: str,
    subtitle: str
):
    st.markdown(
        f"""
        <div class="nyp-header">
            <h1>⚖ {app_title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Pipeline stepper
# --------------------------------------------------------------------------

def render_stepper(
    current_stage: str
):
    """
    Shows the user's position in the product's real:

        Understand → Ask → Ground & Explain → Prepare

    pipeline.
    """

    html = [
        '<div class="nyp-stepper">'
    ]

    found_current = False

    for label, stages in PIPELINE_STAGES:

        is_active = current_stage in stages

        if is_active:
            found_current = True

        css_class = (
            "active"
            if is_active
            else (
                "done"
                if not found_current
                else ""
            )
        )

        html.append(
            f'<div class="nyp-step {css_class}">'
            f'{label}'
            f'</div>'
        )

    html.append(
        "</div>"
    )

    st.markdown(
        "".join(html),
        unsafe_allow_html=True,
    )




# """
# Visual identity for NyayaPath.

# Streamlit's config.toml can only set a handful of flat colors — it can't
# give you custom fonts, gradients, card shadows, or hover states. So this
# module injects real CSS via st.markdown(unsafe_allow_html=True) on top of
# that base theme.

# Selectors below target Streamlit's data-testid attributes rather than its
# internal class names, because internal class names change between
# Streamlit versions but data-testid attributes are considered part of the
# stable public surface.

# If you want to change the look later, every value that matters lives in
# the TOKENS dict — edit that first before touching the CSS template.
# """

# import streamlit as st

# TOKENS = {
#     # --- color ---------------------------------------------------------
#     "ink": "#17233E",           # headings, primary text, header gradient start
#     "indigo_dark": "#101A31",   # header gradient end
#     "marigold": "#E2932E",      # primary accent — buttons, active states
#     "marigold_dark": "#C1770F", # hover state for the accent
#     "paper": "#F5F7F1",         # app background — cool sage-tinted, not cream
#     "card": "#FFFFFF",
#     "border": "#E3E0D3",
#     "muted": "#5B6470",
#     "success_bg": "#EAF4EC",
#     "warning_bg": "#FBF1E3",
#     # --- type ------------------------------------------------------------
#     "font_display": "'Fraunces', Georgia, serif",
#     "font_body": "'Hind', 'Noto Sans', sans-serif",
#     "font_mono": "'IBM Plex Mono', monospace",
# }

# # The real product pipeline from the project synopsis, condensed to the
# # stages the frontend actually surfaces to the user.
# PIPELINE_STAGES = [
#     ("Understand", ["input", "advice"]),
#     ("Ask", ["questions", "anything_else"]),
#     ("Ground & Explain", ["result"]),
#     ("Prepare", ["draft"]),
# ]


# def inject_theme():
#     t = TOKENS
#     st.markdown(
#         f"""
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Hind:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

#         html, body, [class*="css"] {
#             font-family: {t['font_body']};
#             color: {t['ink']};
#         }

#         .stApp {{
#             background: {t['paper']};
#         }}

#         /* Hide Streamlit's own footer branding — we render our own */
#         footer {{ visibility: hidden; }}

#         h1, h2, h3, h4, h5,
#         [data-testid="stMarkdownContainer"] h1,
#         [data-testid="stMarkdownContainer"] h2,
#         [data-testid="stMarkdownContainer"] h3 {{
#             font-family: {t['font_display']};
#             color: {t['ink']};
#             font-weight: 600;
#             letter-spacing: -0.01em;
#         }}

#         [data-testid="stCaptionContainer"] {{
#             font-family: {t['font_mono']};
#             color: {t['muted']};
#             letter-spacing: 0.01em;
#         }}

#         /* --- Primary button: the marigold accent, used sparingly --------- */
#         button[kind="primary"] {{
#             background: linear-gradient(135deg, {t['marigold']}, {t['marigold_dark']});
#             border: none;
#             color: white;
#             font-weight: 600;
#             border-radius: 10px;
#             padding: 0.55em 1.4em;
#             box-shadow: 0 2px 8px rgba(226, 147, 46, 0.35);
#             transition: transform 0.12s ease, box-shadow 0.12s ease;
#         }}
#         button[kind="primary"]:hover {{
#             transform: translateY(-1px);
#             box-shadow: 0 4px 14px rgba(226, 147, 46, 0.45);
#         }}

#         /* --- Secondary button: quiet, ink-outlined -------------------- */
#         button[kind="secondary"] {{
#             background: {t['card']};
#             border: 1.5px solid {t['ink']};
#             color: {t['ink']};
#             font-weight: 500;
#             border-radius: 10px;
#         }}
#         button[kind="secondary"]:hover {{
#             background: {t['ink']};
#             color: white;
#         }}

#         /* --- Text inputs / text areas ----------------------------------- */
#         textarea, input[type="text"], [data-baseweb="textarea"] textarea {{
#             border-radius: 10px !important;
#             border: 1.5px solid {t['border']} !important;
#             font-family: {t['font_body']} !important;
#         }}
#         textarea:focus, [data-baseweb="textarea"] textarea:focus {{
#             border-color: {t['marigold']} !important;
#             box-shadow: 0 0 0 3px rgba(226, 147, 46, 0.15) !important;
#         }}

#         /* --- Bordered containers (st.container(border=True)) --> cards -- */
#         [data-testid="stVerticalBlockBorderWrapper"] {{
#             background: {t['card']};
#             border: 1px solid {t['border']} !important;
#             border-top: 3px solid {t['ink']} !important;
#             border-radius: 12px !important;
#             box-shadow: 0 1px 3px rgba(23, 35, 62, 0.06);
#             padding: 0.25rem 0.25rem;
#             margin-bottom: 0.75rem;
#         }}

#         /* --- Info / warning boxes, recolored to match the palette ------- */
#         [data-testid="stAlertContainer"] {{
#             border-radius: 10px;
#             font-family: {t['font_body']};
#         }}

#         /* --- Progress stepper (signature element) ------------------------ */
#         .nyp-stepper {{
#             display: flex;
#             justify-content: space-between;
#             margin: 0.5rem 0 1.75rem 0;
#         }}
#         .nyp-step {{
#             flex: 1;
#             text-align: center;
#             font-family: {t['font_mono']};
#             font-size: 0.72rem;
#             letter-spacing: 0.04em;
#             text-transform: uppercase;
#             color: {t['muted']};
#             position: relative;
#             padding-top: 14px;
#         }}
#         .nyp-step::before {{
#             content: "";
#             position: absolute;
#             top: 0;
#             left: 0;
#             right: 0;
#             height: 3px;
#             background: {t['border']};
#             border-radius: 2px;
#         }}
#         .nyp-step.active {{
#             color: {t['ink']};
#             font-weight: 700;
#         }}
#         .nyp-step.active::before {{
#             background: linear-gradient(90deg, {t['marigold']}, {t['marigold_dark']});
#         }}
#         .nyp-step.done::before {{
#             background: {t['ink']};
#         }}

#         /* --- Header banner ------------------------------------------------ */
#         .nyp-header {{
#             background: linear-gradient(120deg, {t['ink']}, {t['indigo_dark']});
#             border-radius: 16px;
#             padding: 1.4rem 1.6rem;
#             margin-bottom: 1.5rem;
#             box-shadow: 0 4px 18px rgba(16, 26, 49, 0.25);
#         }}
#         .nyp-header h1 {{
#             color: white !important;
#             font-size: 1.6rem;
#             margin: 0;
#         }}
#         .nyp-header p {{
#             color: rgba(255,255,255,0.72);
#             font-family: {t['font_body']};
#             margin: 0.2rem 0 0 0;
#             font-size: 0.9rem;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# def render_header(app_title: str, subtitle: str):
#     st.markdown(
#         f"""
#         <div class="nyp-header">
#             <h1>⚖ {app_title}</h1>
#             <p>{subtitle}</p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# def render_stepper(current_stage: str):
#     """Signature element: shows the user's position in the product's real
#     Understand → Ask → Ground & Explain → Prepare pipeline, not a generic
#     1-2-3 progress bar."""
#     html = ['<div class="nyp-stepper">']
#     found_current = False
#     for label, stages in PIPELINE_STAGES:
#         is_active = current_stage in stages
#         if is_active:
#             found_current = True
#         css_class = "active" if is_active else ("done" if not found_current else "")
#         html.append(f'<div class="nyp-step {css_class}">{label}</div>')
#     html.append("</div>")
#     st.markdown("".join(html), unsafe_allow_html=True)