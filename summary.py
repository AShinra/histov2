import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
import altair as alt
from common import get_agencies_list, page_title


@st.cache_data
def get_data(_client):

    try:
        # client = get_gsheet_client()
        sheet_id = "1VVLZ0O3NncvMjex8gonkgPTfIKzkJh22UON55991_QE"
        sheet = _client.open_by_key(sheet_id)

        data = sheet.sheet1.get_all_values()

        df = pd.DataFrame(data)
        df.columns = df.iloc[0]
        df = df[1:]
    
    except Exception as e:
        st.error(f"Error accessing Google Sheet: {e}")

    return df


def summary(client):
    page_title('Summary')

    db = client['histo']
    collection = db['data']
    documents = list(collection.find({}))

    df = pd.DataFrame(documents)

    # df = get_data(client)

    df['DATE'] = pd.to_datetime(df['DATE'])
    df['MONTH_NAME'] = df['DATE'].dt.month_name()
    df['YEAR'] = df['DATE'].dt.year
    monthly_data = df['MONTH_NAME'].value_counts(sort=False)

    year_list = df['YEAR'].unique()   
    
    selection_col, chart_col = st.columns([0.3, 0.7], border=True)
    with selection_col:
        
        req_type = st.pills(
            label='Request Type',
            options=['Regular', 'Ad Hoc', 'TOA'],
            width='stretch',
            default='Regular'
        )

        if req_type == 'Regular':
            df = df[df['TYPE']==1]
        elif req_type == 'Ad Hoc':
            df = df[df['TYPE']==2]
        elif req_type == 'TOA':
            df = df[df['TYPE']==3]

        # agency selection
        agency_list = (df['AGENCY'].unique()).tolist()

        
        # agency_list = get_agencies_list(client)
        # agency_list.insert(0, 'ALL')

        agency_selection = st.selectbox(
            label='AGENCY',
            options=agency_list
        )

        exit()

        agency_collection = db['agencies']
        if agency_selection != 'ALL':
            df_agency_filtered = df[df['AGENCY']==agency_selection]
            # client selection
            document = agency_collection.find_one({'AGENCY NAME':agency_selection})
            client_list_options = document['CLIENTS']
            client_list_options = sorted(client_list_options)
            client_list_options.insert(0, 'ALL')
        else:
            df_agency_filtered = df
            cursor = agency_collection.find({}, {'CLIENTS':1, '_id':0})

            client_list_options = []
            for items in cursor:
                for item in items['CLIENTS']:
                    client_list_options.append(item)
            
            client_list_options = sorted(list(dict.fromkeys(client_list_options)))
            client_list_options.insert(0, 'ALL')

        client_selection = st.selectbox(
            label='CLIENT',
            options=client_list_options
        )

        if client_selection != 'ALL':
            df_clientfiltered = df_agency_filtered[df_agency_filtered['CLIENT NAME']==client_selection]
        else:
            df_clientfiltered = df_agency_filtered
        
        total_request = df_clientfiltered.shape[0]

        months = df_clientfiltered['MONTH_NAME'].unique()
        number_of_months = months.shape[0]

        _days = df_clientfiltered['DATE'].unique()
        number_of_days = _days.shape[0]

        _misses = df_clientfiltered[df['CAPTURED']==0]
        total_misses = _misses.shape[0]

        _misses_tier = df_clientfiltered[(df['CAPTURED']==0) & (df['TIER'] != '')]        

        _misses_tier1 = _misses_tier[_misses_tier['TIER']==1]
        _misses_tier1_pub = _misses_tier1['FQDN'].to_list()
        count_misses_tier1 = _misses_tier1.shape[0]

        _misses_tier2 = _misses_tier[_misses_tier['TIER']==2]
        _misses_tier2_pub = _misses_tier2['FQDN'].to_list()
        count_misses_tier2 = _misses_tier2.shape[0]

        _misses_tier3 = _misses_tier[_misses_tier['TIER']==3]
        _misses_tier3_pub = _misses_tier3['FQDN'].to_list()
        count_misses_tier3 = _misses_tier3.shape[0]

        _misses_tieru = _misses_tier[_misses_tier['TIER']==0]
        _misses_tieru_pub = _misses_tieru['FQDN'].to_list()
        count_misses_tieru = _misses_tieru.shape[0]

        request_per_month = total_request/number_of_months
        request_per_day = total_request/number_of_days
        misses_per_month = total_misses/number_of_months
        misses_per_day = total_misses/number_of_days
        misses_percent = total_misses/total_request


        cola1, cola2 = st.columns(2)

        with cola1:
            cap_option = st.radio(
                label='OPTIONS',
                options=['Missed', 'Captured', 'Request'],
                horizontal=False                
            )
        
        with cola2:
            year_selected = st.selectbox(
                label='YEAR',
                options=year_list)
        
        # compute statistics
        with st.spinner('Processing Data', show_time=True):

            st.markdown(f"### Statistics ({client_selection})")

            st.markdown(f"#### Requests")
            st.markdown(f"""
            <div style="line-height: 0.3; font-size:20px;">
            <p style="color:#008B8B;"><b>Total: </b>{int(total_request):,}</p>
            <p style="color:#008B8B;"><b>Monthly Ave: </b>{int(request_per_month):,}</p>
            <p style="color:#008B8B;"><b>Daily Ave: </b>{int(request_per_day):,}</p>            
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"#### Misses")
            st.markdown(f"""
            <div style="line-height: 0.3; font-size:20px;">
            <p style="color:red;"><b>Total: </b>{int(total_misses):,} ({misses_percent:.2%})</p>
            <p style="color:red;"><b>Monthly Ave: </b>{int(misses_per_month):,}</p>
            <p style="color:red;"><b>Daily Ave: </b>{int(misses_per_day):,}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"#### Tier")           
            
            coltier1, coltier2 = st.columns([0.6, 0.4])

            with coltier1:
                if _misses_tier1_pub != 0:
                    with st.expander(
                        label=f':blue[**Tier 1 Missed: {count_misses_tier1}**]',
                    ):
                        _misses_tier1_pub = list(dict.fromkeys(_misses_tier1_pub))
                        for _pub in sorted(_misses_tier1_pub):
                            st.write(_pub)

                if _misses_tier2_pub != 0:
                    with st.expander(
                        label=f':blue[**Tier 2 Missed: {count_misses_tier2}**]'
                    ):
                        _misses_tier2_pub = list(dict.fromkeys(_misses_tier2_pub))
                        for _pub in sorted(_misses_tier2_pub):
                            st.write(_pub)

                if _misses_tier3_pub != 0:
                    with st.expander(
                        label=f':blue[**Tier 3 Missed: {count_misses_tier3}**]'
                    ):
                        _misses_tier3_pub = list(dict.fromkeys(_misses_tier3_pub))
                        for _pub in sorted(_misses_tier3_pub):
                            st.write(_pub)
                
                if _misses_tieru_pub != 0:
                    with st.expander(
                        label=f':blue[**Tier Unlisted Missed: {count_misses_tieru}**]'
                    ):
                        _misses_tieru_pub = list(dict.fromkeys(_misses_tieru_pub))
                        for _pub in sorted(_misses_tieru_pub):
                            st.write(_pub)

        if cap_option=='Captured':
            df_captured = df_clientfiltered[df_clientfiltered['CAPTURED'] == 1]
        elif cap_option=='Missed':
            df_captured = df_clientfiltered[df_clientfiltered['CAPTURED'] == 0]
        elif cap_option=='Request':
            df_captured = df_clientfiltered


    with chart_col:

        month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        chart_cola1, chart_cola2 = st.columns([0.3, 0.7], border=True)
        with chart_cola1:
            with st.spinner('Generating Table', show_time=True):
                monthcount = df_captured['MONTH_NAME'].value_counts(sort=False)
                df_monthcount = monthcount.to_frame()
                df_monthcount = df_monthcount.reset_index()

                # Sort using categorical order
                df_monthcount['MONTH_NAME'] = pd.Categorical(df_monthcount['MONTH_NAME'], categories=month_order, ordered=True)
                df_monthcount = df_monthcount.sort_values('MONTH_NAME')

                st.dataframe(df_monthcount, hide_index=True)
        with chart_cola2:
            with st.spinner('Generating Chart', show_time=True):
                _chart1 = alt.Chart(df_monthcount, title=alt.TitleParams(f'Monthly {cap_option}', anchor='middle')).mark_bar().encode(
                    x=alt.X('MONTH_NAME', sort=month_order, title='Month'),
                    y=alt.Y('count', title='Count'))
                st.write(_chart1)       
                
        chart_colb1, chart_colb2 = st.columns([0.3, 0.7], border=True)
        with chart_colb1:
            with st.spinner('Generating Table', show_time=True):
                countdate = df_captured['DATE'].value_counts(sort=False)
                df_countdate = countdate.to_frame()
                df_countdate = df_countdate.reset_index()            
                st.dataframe(df_countdate, hide_index=True)
        with chart_colb2:
            with st.spinner('Generating Chart', show_time=True):
                _chart2 = alt.Chart(df_countdate, title=alt.TitleParams(f'Daily {cap_option}', anchor='middle')).mark_bar().encode(
                        x=alt.X('yearmonthdate(DATE):O', sort=None, title='Date', axis=alt.Axis(format='%b %d')),
                        y=alt.Y('count', title='Count'))
                st.write(_chart2)
        
        chart_colc1, chart_colc2 = st.columns([0.3, 0.7], border=True)
        with chart_colc1:
            with st.spinner('Generating Table', show_time=True):
                countfqdn = df_captured['FQDN'].value_counts(sort=True)
                df_fqdn = countfqdn.to_frame()
                df_fqdn = df_fqdn.reset_index()
                top10_fqdn = df_fqdn[:10]
                st.dataframe(top10_fqdn, hide_index=True)
        with chart_colc2:
            with st.spinner('Generating Chart', show_time=True):
                _chart3 = alt.Chart(top10_fqdn, title=alt.TitleParams(f'Top 10 {cap_option}', anchor='middle')).mark_bar().encode(
                        x=alt.X('FQDN', sort=None, title='FQDN'),
                        y=alt.Y('count', title='Count'))
                st.write(_chart3)
    

        



    return