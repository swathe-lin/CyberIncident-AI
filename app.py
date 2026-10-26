# ============================================================

if page == "Evaluation" and st.session_state.get("analysis_ready", False) and "rag_result" in locals():
    try:
        retrieved = rag_result.get("retrieved_knowledge", []) if isinstance(rag_result, dict) else []
        entities = rag_result.get("entities", {}) if isinstance(rag_result, dict) else {}
        entity_categories = ["PERSON", "ORGANIZATION", "LOCATION", "ATTACK_TYPE", "SEVERITY", "AFFECTED_SYSTEM", "INDICATORS"]
        detected_by_category = {category: bool(entities.get(category, [])) for category in entity_categories}
        detected_categories = sum(detected_by_category.values())
        extraction_coverage = detected_categories / len(entity_categories) if entity_categories else 0.0
        similarity_scores = []
        for item in retrieved:
            if isinstance(item, dict):
                score = item.get("score", item.get("similarity"))
                try:
                    score = float(score)
                    if score >= 0:
                        similarity_scores.append(score)
                except (TypeError, ValueError):
                    pass
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        best_similarity = max(similarity_scores) if similarity_scores else 0.0
        indicator_items = indicators if isinstance(indicators, list) else ([indicators] if indicators else [])
        indicator_count = len({str(x).strip().casefold() for x in indicator_items if str(x).strip()})
        processing_time = float(st.session_state.get("analysis_processing_time", 0.0) or 0.0)

        st.markdown("""
        <style>
        .eval-heading{color:#103d73;font-size:32px;font-weight:850;margin:8px 0 4px}
        .eval-subtitle{color:#6886a6;font-size:15px;margin:0 0 18px}
        .eval-card{height:100%;background:rgba(255,255,255,.93);border:1px solid #d3e6f8;border-top:4px solid #328cff;
          border-radius:13px;padding:14px 14px;box-shadow:0 6px 18px rgba(35,100,170,.06);margin-bottom:12px}
        .eval-label{color:#58799b;font-size:14px;margin-bottom:7px}
        .eval-value{color:#234f7b;font-size:24px;font-weight:850;line-height:1.2;overflow-wrap:anywhere}
        .eval-panel{background:rgba(255,255,255,.91);border:1px solid #d3e6f8;border-radius:14px;padding:16px;margin:10px 0}
        .eval-panel-title{color:#103d73;font-size:21px;font-weight:800;margin-bottom:10px}
        .colour-chart{background:rgba(255,255,255,.94);border:1px solid #d3e6f8;border-radius:13px;padding:15px 16px;margin-top:10px;box-shadow:0 5px 14px rgba(35,100,170,.05)}
        .chart-row{margin:0 0 13px}
        .chart-row:last-child{margin-bottom:0}
        .chart-row-label{display:flex;justify-content:space-between;gap:10px;color:#315d88;font-size:15px;font-weight:700;margin-bottom:6px}
        .chart-row-label span{color:#6b86a3;font-size:14px;font-weight:600;white-space:nowrap}
        .chart-track{height:13px;background:#eaf2fb;border-radius:99px;overflow:hidden}
        .chart-fill{height:100%;border-radius:99px;min-width:0;transition:width .25s ease}
        </style>
        <div class="eval-heading">📊 Evaluation &amp; Performance</div>
        <div class="eval-subtitle">Live measurements from the incident currently analyzed. Classification accuracy and F1-score require labelled test data and are not inferred from one incident.</div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4, gap="small")
        for col, label, value in [
            (k1, "🎯 Detected Attack Type", str(attack_type)),
            (k2, "🧩 Entity Coverage", f"{extraction_coverage * 100:.1f}%"),
            (k3, "📚 Average RAG Similarity", f"{avg_similarity:.4f}" if similarity_scores else "N/A"),
            (k4, "🔎 Indicators Detected", str(indicator_count)),
        ]:
            with col:
                st.markdown(f'<div class="eval-card"><div class="eval-label">{label}</div><div class="eval-value">{value}</div></div>', unsafe_allow_html=True)

        left_panel, right_panel = st.columns([1.05, 1], gap="medium")
        with left_panel:
            st.markdown('<div class="eval-panel"><div class="eval-panel-title">🧩 Entity Detection</div></div>', unsafe_allow_html=True)
            st.caption(f"Detected entity categories: {detected_categories} of {len(entity_categories)}")
            st.progress(extraction_coverage, text=f"Entity coverage · {extraction_coverage * 100:.1f}%")
            # Bright horizontal bars are used instead of the dark default Streamlit chart.
            # Bars show only the entity categories detected in this actual incident.
            category_colours = ["#2787F5", "#19B8A6", "#FFAD42", "#8B5CF6", "#F45B69", "#14A8D4", "#5B78E5"]
            entity_rows_html = []
            for idx, (name, found) in enumerate(detected_by_category.items()):
                pct = 100 if found else 0
                colour = category_colours[idx % len(category_colours)]
                status = "Detected" if found else "Not detected"
                entity_rows_html.append(
                    f'<div class="chart-row"><div class="chart-row-label">{name.replace("_", " ").title()}<span>{status}</span></div>'
                    f'<div class="chart-track"><div class="chart-fill" style="width:{pct}%;background:{colour};"></div></div></div>'
                )
            st.markdown('<div class="colour-chart">' + ''.join(entity_rows_html) + '</div>', unsafe_allow_html=True)
        with right_panel:
            st.markdown('<div class="eval-panel"><div class="eval-panel-title">📚 RAG Retrieval Evaluation</div></div>', unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            r1.metric("Retrieved Sources", len(retrieved))
            r2.metric("Average Similarity", f"{avg_similarity:.4f}" if similarity_scores else "N/A")
            r3.metric("Best Similarity", f"{best_similarity:.4f}" if similarity_scores else "N/A")
            if similarity_scores:
                rag_colours = ["#2787F5", "#19B8A6", "#8B5CF6", "#FFAD42", "#F45B69", "#14A8D4"]
                max_score = max(max(similarity_scores), 0.0001)
                rag_rows_html = []
                for idx, score in enumerate(similarity_scores, start=1):
                    width = max(0, min(100, (score / max_score) * 100))
                    colour = rag_colours[(idx - 1) % len(rag_colours)]
                    rag_rows_html.append(
                        f'<div class="chart-row"><div class="chart-row-label">Source {idx}<span>{score:.4f}</span></div>'
                        f'<div class="chart-track"><div class="chart-fill" style="width:{width:.2f}%;background:{colour};"></div></div></div>'
                    )
                st.markdown('<div class="colour-chart">' + ''.join(rag_rows_html) + '</div>', unsafe_allow_html=True)
                st.caption("Bar lengths are scaled relative to the highest similarity score in this retrieval.")
            else:
                st.info("The retrieval pipeline did not return numeric similarity scores.")

        st.markdown('<div class="eval-panel"><div class="eval-panel-title">📋 Evaluation Details</div></div>', unsafe_allow_html=True)
        metric_rows = [
            {"Metric": "Detected attack type", "Description": "Attack type reported for the current incident", "Value": str(attack_type)},
            {"Metric": "Entity categories detected", "Description": "Number of entity categories with at least one value", "Value": f"{detected_categories}/{len(entity_categories)}"},
            {"Metric": "Entity coverage", "Description": "Detected categories divided by the seven tracked categories", "Value": f"{extraction_coverage * 100:.1f}%"},
            {"Metric": "Security indicators", "Description": "Unique indicators found in the current incident", "Value": str(indicator_count)},
            {"Metric": "RAG sources retrieved", "Description": "Number of knowledge chunks returned by retrieval", "Value": str(len(retrieved))},
            {"Metric": "Average RAG similarity", "Description": "Mean of numeric retrieval scores returned by RAG", "Value": f"{avg_similarity:.4f}" if similarity_scores else "N/A"},
            {"Metric": "Analysis processing time", "Description": "Elapsed time recorded for the incident analysis", "Value": f"{processing_time:.2f} seconds"},
            {"Metric": "Classification accuracy / precision / recall / F1", "Description": "Requires a labelled test dataset with expected outputs; not measured from one incident", "Value": "Not measured"},
        ]
        st.markdown("<style>div[data-testid='stDataFrame']{font-size:15px} div[data-testid='stCaptionContainer'] p{font-size:14px !important}</style>", unsafe_allow_html=True)
        st.dataframe(metric_rows, use_container_width=True, hide_index=True)
        st.info("These live measurements describe this incident's extraction and retrieval. They are not benchmark accuracy scores. To calculate accuracy, precision, recall, or F1-score, evaluate a labelled set of incidents with known correct answers.")
    except Exception as evaluation_error:
        st.warning(f"Live evaluation could not be calculated: {evaluation_error}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    🔐 CyberIncident AI
    • AI-Powered Cybersecurity Incident Analysis
</div>
""",
    unsafe_allow_html=True
)