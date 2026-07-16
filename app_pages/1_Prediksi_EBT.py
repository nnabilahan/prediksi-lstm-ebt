
import streamlit as st

from components.prediction_header import render_prediction_header
from components.prediction_form import render_prediction_form
from components.prediction_result import render_prediction_result
from components.prediction_chart import render_prediction_chart
from components.prediction_table import render_prediction_table


def render():
    render_prediction_header()

    input_form = render_prediction_form()

    st.divider()

    if input_form is not None:
        df_prediksi = render_prediction_result(input_form)

        if df_prediksi is not None:
            st.divider()
            render_prediction_chart(input_form, df_prediksi)

            st.divider()
            render_prediction_table(input_form, df_prediksi)
    else:
        st.info("Lengkapi form di atas lalu klik **Prediksi Produksi EBT** untuk melihat hasilnya.")