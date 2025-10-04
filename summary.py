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

    # load mongodb
    db = client['histo'] #load database
    collection = db['data'] # get the collection
    documents = list(collection.find({})) # find all documents

    # convert document to dataframe
    df = pd.DataFrame(documents)

    # agency selection
    agency_list = sorted((df['AGENCY'].unique()).tolist()) # from dataframe result
    # agency_list = get_agencies_list(client) # from mongdb
    agency_list.insert(0, 'ALL')

    # get total number requests
    total_requests = df.shape[0]

    # get total number missed
    df_misses = df[df['CAPTURED']==0]
    total_misses = df_misses.shape[0]

    # get total number captured
    df_captured = df[df['CAPTURED']==1]
    total_captured = df_captured.shape[0]

    # get the number of months
    df['MONTH_NAME'] = df['DATE'].dt.month_name()
    months = df['MONTH_NAME'].unique()
    month_count = len(months)

    # get 3 letter month
    df['MONTH'] = df['MONTH_NAME'].str[:3]
        
    # get year
    df['YEAR'] = df['DATE'].dt.year
    monthly_data = df['MONTH_NAME'].value_counts(sort=False)

    
    # st.markdown("""<style>.st-emotion-cache-r44huj h3{
    #             padding-top: 0rem !important;
    #             padding-bottom: 0rem !important;
    #             }</style>""", unsafe_allow_html=True)
    
    st.markdown("""<style>.st-emotion-cache-pzw1tj {background-color:lightblue;}""",unsafe_allow_html=True)
    st.markdown("""<style>.st-emotion-cache-1ubukkv {background-color:lightpink;}""",unsafe_allow_html=True)
    st.markdown("""<style>.st-emotion-cache-pxdqmg {background-color:lightgreen;}""",unsafe_allow_html=True)


    # st.subheader("Requests and Misses Overview - Year 2025")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([0.4, 0.25, 0.25, 0.1])

        with col1:
            with st.container(border=True):
                col1a, col1b, col1c, col1d = st.columns([0.15, 0.35, 0.15, 0.35])
                with col1a:
                    st.write(':blue[**Agency**]')
                with col1b:
                    agency_selection = st.selectbox(
                        label='Agency',
                        options=agency_list,
                        label_visibility='collapsed'
                    )
                
                # get client list depending on the agency
                if agency_selection != 'ALL':
                    df_agency_filtered = df[df['AGENCY']==agency_selection] # filter dataframe
                    client_list_options = df_agency_filtered['CLIENT NAME'] # get clients from filtered df
                    client_list_options = client_list_options.unique() # get the unique values only
                    client_list_options = client_list_options.tolist() # convert to list
                    client_list_options = sorted(client_list_options) # sort list
                    client_list_options.insert(0, 'ALL')
                else:
                    df_agency_filtered = df
                    client_list_options = df_agency_filtered['CLIENT NAME'] # get clients from filtered df
                    client_list_options = client_list_options.unique() # get the unique values only
                    client_list_options = client_list_options.tolist() # convert to list
                    client_list_options = sorted(client_list_options) # sort list
                    client_list_options.insert(0, 'ALL')

                with col1c:
                    st.write(':blue[**Client**]')
                with col1d:
                    client_selection = st.selectbox(
                        label='Company',
                        options=client_list_options,
                        label_visibility='collapsed'
                    )

        with col2:
            with st.container(border=True):
                col2a, col2b = st.columns([0.2, 0.8])
                with col2a:
                    st.write(':blue[**Type**]')
                with col2b:
                    _type = st.pills(
                        label='Request Type',
                        options=['Regular', 'Ad Hoc', 'TOA'],
                        width='stretch',
                        label_visibility='collapsed',
                        default='Regular',
                        )
                    
        
        with col3:
            with st.container(border=True):
                col3a, col3b = st.columns([0.2, 0.8])
                with col3a:
                    st.write(':blue[**Options**]')
                with col3b:
                    _captured = st.pills(
                        label='Options',
                        options=['Missed', 'Captured'],
                        width='stretch',
                        label_visibility='collapsed',
                        default='Missed',
                        )
        
        with col4:
            with st.container(border=True):
                
                year_list = set(df['YEAR'].to_list())

                _year = st.selectbox(
                    label='Year',
                    options=year_list,
                    label_visibility='collapsed'
                )
        
        colmetric1, colmetric2, colmetric3 = st.columns([2,3,1], border=True)
        st.markdown("""<style>[data-testid="stMarkdownContainer"]{
                font-size: large;
                }</style>""", unsafe_allow_html=True)
        st.markdown("""<style>[data-testid="stMetricValue"]{
                font-size: xxx-large;
                font-weight: bold;
                }</style>""", unsafe_allow_html=True)
        st.markdown("""<style>div[data-testid="stMetricValue"]:nth-of-type(2){
                color: red !important;
                }</style>""", unsafe_allow_html=True)

        with colmetric1:
            st.write(f'**Requests**')

            colmetric11, colmetric12 = st.columns([1,1])

            with colmetric11:
                with st.container(border=True):
                    st.metric(
                    label='**Total**',
                    value=total_requests,
                    width='stretch'
                )
            with colmetric12:
                with st.container(border=True):
                    st.metric(
                    label='Monthly Average',
                    value=int(total_requests/month_count)
                )
            
            
        with colmetric2:
            st.write(f'**Misses**')

            colmetric21, colmetric22, colmetric23 = st.columns([1,1,1])

            with colmetric21:
                with st.container(border=True):
                    st.metric(
                        label='Total',
                        value = total_misses
                )
            with colmetric22:
                with st.container(border=True):
                    st.metric(
                        label='Monthly Average',
                        value = int(total_misses/month_count)
                )
            with colmetric23:
                with st.container(border=True):
                    st.metric(
                        label='Percentage',
                        value = f'{(total_misses/total_requests):.2%}'
                )
        
        with colmetric3:
            st.write(f'**Captured**')

            with st.container(border=True):
                st.metric(
                    label='Total',
                    value=total_captured
            )


        # working dataframe

        if _type=='Regular':
            type_selection=1
        elif _type=='Ad Hoc':
            type_selection=2
        elif _type=='TOA':
            type_selection=3

        if _captured=='Missed':
            capture_type=0
        elif _captured=='Captured':
            capture_type=1

        if agency_selection=='ALL' and client_selection=='ALL':
            working_df = df[(df['TYPE']==type_selection) & (df['CAPTURED']==capture_type) & (df['YEAR']==_year)]
        elif agency_selection!='ALL' and client_selection=='ALL':
            working_df = df[(df['AGENCY']==agency_selection) & (df['TYPE']==type_selection) & (df['CAPTURED']==capture_type & (df['YEAR']==_year))]
        elif agency_selection!='ALL' and client_selection!='ALL':
            working_df = df[(df['AGENCY']==agency_selection) & (df['CLIENT NAME']==client_selection) & (df['TYPE']==type_selection) & (df['CAPTURED']==capture_type & (df['YEAR']==_year))]
        # st.dataframe(working_df)
        
        with st.container(border=True):
            if client_selection=='ALL':
                st.header('ALL CLIENTS')    
            else:
                st.header(client_selection)

        cola, colb = st.columns([5,1])
        with cola:
            col13, col23 = st.columns([1,1])
            with col13:
                with st.container(border=True):
                    _monthly = working_df['MONTH'].value_counts(sort=False)
                    monthly_df = _monthly.to_frame()
                    monthly_df = monthly_df.reset_index()
                    # st.dataframe(monthly_missed_df, hide_index=True)

                    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

                    _chart1 = alt.Chart(monthly_df, title=alt.TitleParams(f'MONTHLY {_captured.upper()}', fontSize=40)).mark_bar().encode(
                        x=alt.X('MONTH', sort=month_order, title='Month', axis=alt.Axis(labelAngle=0, labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)),
                        y=alt.Y('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)))
                    st.write(_chart1) 
                            
            with col23:
                with st.container(border=True):
                    _daily = working_df['DATE'].value_counts(sort=False)
                    daily_df = _daily.to_frame()
                    daily_df = daily_df.reset_index()
                    # st.dataframe(daily_missed_df, hide_index=True)

                    _chart2 = alt.Chart(daily_df, title=alt.TitleParams(f'DAILY {_captured.upper()}', fontSize=40)).mark_bar().encode(
                        x=alt.X('yearmonthdate(DATE):O', sort=None, title='Date', axis=alt.Axis(format='%b %d', labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)),
                        y=alt.Y('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)))
                    st.write(_chart2)

            
            col14, col24 = st.columns([1,1])
            with col14:
                with st.container(border=True, height=450):
                    _fqdn = working_df['FQDN'].value_counts(sort=True)
                    fqdn_df = _fqdn.to_frame()
                    fqdn_df = fqdn_df.reset_index()
                    top10_fqdn_df = fqdn_df[:10]
                    # st.dataframe(top10_fqdn_df, hide_index=True)

                    _chart2 = alt.Chart(top10_fqdn_df, title=alt.TitleParams(f'TOP 10 FQDN {_captured.upper()}', fontSize=40)).mark_bar().encode(
                        x=alt.X('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)),
                        y=alt.Y('FQDN', sort=None, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold', titleFontSize=20)))
                    st.write(_chart2)
            
            with col24:
                with st.container(border=True, height=450):
                    _tier = working_df['TIER'].value_counts(sort=True)
                    tier_df = _tier.to_frame()
                    tier_df = tier_df.reset_index()
                    tier_df['TIER'] = tier_df['TIER'].replace({0: 'Unlisted', 1: 'Tier 1', 2: 'Tier 2', 3: 'Tier 3'})
                    # st.dataframe(tier_df, hide_index=True)

                    # Create pie chart
                    pie = alt.Chart(tier_df).mark_arc().encode(
                        theta=alt.Theta(field="count", type="quantitative"),
                        color=alt.Color(field="TIER", type="nominal", legend=alt.Legend(orient='left')),
                        tooltip=["TIER", "count"]

                    ).properties(
                        width=400,
                        height=400,
                        title=alt.TitleParams(
                            text=f"TIER {_captured.upper()}",
                            # anchor="middle",   # centers the title
                            fontSize=40,
                            fontWeight="bold"
                            )
                    )

                    st.altair_chart(pie, use_container_width=True)

            st.header('MISSED WEBSITES')
            col15, col25, col35, col45 = st.columns([1, 1, 1, 1])
            with col15:
                with st.container(border=True, height=500):
                    st.subheader('TIER 1')
                    tier1_missed_df = working_df[working_df['TIER']==1]
                    tier1_fqdn_missed_df = tier1_missed_df['FQDN'].value_counts().reset_index()
                    st.dataframe(tier1_fqdn_missed_df, hide_index=True)
            
            with col25:
                with st.container(border=True, height=500):
                    st.subheader('TIER 2')
                    tier2_missed_df = working_df[working_df['TIER']==2]
                    tier2_fqdn_missed_df = tier2_missed_df['FQDN'].value_counts().reset_index()
                    st.dataframe(tier2_fqdn_missed_df, hide_index=True)
            
            with col35:
                with st.container(border=True, height=500):
                    st.subheader('TIER 3')
                    tier3_missed_df = working_df[working_df['TIER']==3]
                    tier3_fqdn_missed_df = tier3_missed_df['FQDN'].value_counts().reset_index()
                    st.dataframe(tier3_fqdn_missed_df, hide_index=True)
            
            with col45:
                with st.container(border=True, height=500):
                    st.subheader('TIER UNLISTED')
                    tieru_missed_df = working_df[working_df['TIER']==0]
                    tieru_fqdn_missed_df = tieru_missed_df['FQDN'].value_counts().reset_index()
                    st.dataframe(tieru_fqdn_missed_df, hide_index=True)

        with colb:
            with st.container(border=True):
                if client_selection=='ALL':
                    st.write(':blue[**SELECT A CLIENT**]')
                else:
                    st.write(f':blue[**{client_selection}**]')

                    client_df = df[(df['AGENCY']==agency_selection) & (df['CLIENT NAME']==client_selection)]

                    # get captured and misses count
                    captured_misses_df = client_df['CAPTURED'].value_counts().reset_index()
                    client_misses = int(captured_misses_df.loc[captured_misses_df['CAPTURED']==0, 'count'].iloc[0])
                    client_captured = int(captured_misses_df.loc[captured_misses_df['CAPTURED']==1, 'count'].iloc[0])
                    client_requests = client_captured + client_misses
                    
                    with st.container(border=True):
                        st.metric(
                            label=':blue[**Requests**]',
                            value=client_requests
                        )

                    with st.container(border=True):
                        st.metric(
                            label=':green[**Captured**]',
                            value=client_captured
                        )
                    
                    with st.container(border=True):
                        st.metric(
                            label=':red[**Misses**]',
                            value=client_misses
                        )
                                        
                    with st.container(border=True):
                        st.metric(
                            label=':red[**Percentage**]',
                            value=f'{(client_misses/client_requests):.2%}'
                        )



        

    
    # db = client['histo']
    # collection = db['data']
    # documents = list(collection.find({}))

    # df = pd.DataFrame(documents)

    # # df = get_data(client)

    # df['DATE'] = pd.to_datetime(df['DATE'])
    # df['MONTH_NAME'] = df['DATE'].dt.month_name()
    # df['YEAR'] = df['DATE'].dt.year
    # monthly_data = df['MONTH_NAME'].value_counts(sort=False)

    # year_list = df['YEAR'].unique()   
    
    # selection_col, chart_col = st.columns([0.3, 0.7], border=True)
    # with selection_col:
    #     with st.container(border=True):
    #         req_type = st.pills(
    #             label='**:violet[REQUEST TYPE]**',
    #             options=['Regular', 'Ad Hoc', 'TOA'],
    #             width='stretch',
    #             default='Regular'
    #         )

    #     if req_type == 'Regular':
    #         df = df[df['TYPE']==1]
    #     elif req_type == 'Ad Hoc':
    #         df = df[df['TYPE']==2]
    #     elif req_type == 'TOA':
    #         df = df[df['TYPE']==3]

    #     # agency selection
    #     agency_list = sorted((df['AGENCY'].unique()).tolist()) # from dataframe result
    #     # agency_list = get_agencies_list(client) # from mongdb
    #     agency_list.insert(0, 'ALL')

    #     with st.container(border=True):
    #         agency_selection = st.selectbox(
    #             label='**:violet[AGENCY]**',
    #             options=agency_list
    #         )       
            
    #         if agency_selection != 'ALL':
    #             df_agency_filtered = df[df['AGENCY']==agency_selection] # filter dataframe
    #             client_list_options = df_agency_filtered['CLIENT NAME'] # get clients from filtered df
    #             client_list_options = client_list_options.unique() # get the unique values only
    #             client_list_options = client_list_options.tolist() # convert to list
    #             client_list_options = sorted(client_list_options) # sort list
    #             client_list_options.insert(0, 'ALL')
    #         else:
    #             df_agency_filtered = df
    #             client_list_options = df_agency_filtered['CLIENT NAME'] # get clients from filtered df
    #             client_list_options = client_list_options.unique() # get the unique values only
    #             client_list_options = client_list_options.tolist() # convert to list
    #             client_list_options = sorted(client_list_options) # sort list
    #             client_list_options.insert(0, 'ALL')

    #         client_selection = st.selectbox(
    #             label='**:violet[CLIENT]**',
    #             options=client_list_options
    #         )
        
    #     if client_selection != 'ALL':
    #         df_clientfiltered = df_agency_filtered[df_agency_filtered['CLIENT NAME']==client_selection]
    #     else:
    #         df_clientfiltered = df_agency_filtered
        
    #     total_request = df_clientfiltered.shape[0]

    #     months = df_clientfiltered['MONTH_NAME'].unique()
    #     number_of_months = months.shape[0]

    #     _days = df_clientfiltered['DATE'].unique()
    #     number_of_days = _days.shape[0]

    #     _misses = df_clientfiltered[df['CAPTURED']==0]
    #     total_misses = _misses.shape[0]

    #     _misses_tier = df_clientfiltered[(df['CAPTURED']==0) & (df['TIER'] != '')]        

    #     _misses_tier1 = _misses_tier[_misses_tier['TIER']==1]
    #     _misses_tier1_pub = _misses_tier1['FQDN'].to_list()
    #     count_misses_tier1 = _misses_tier1.shape[0]

    #     _misses_tier2 = _misses_tier[_misses_tier['TIER']==2]
    #     _misses_tier2_pub = _misses_tier2['FQDN'].to_list()
    #     count_misses_tier2 = _misses_tier2.shape[0]

    #     _misses_tier3 = _misses_tier[_misses_tier['TIER']==3]
    #     _misses_tier3_pub = _misses_tier3['FQDN'].to_list()
    #     count_misses_tier3 = _misses_tier3.shape[0]

    #     _misses_tieru = _misses_tier[_misses_tier['TIER']==0]
    #     _misses_tieru_pub = _misses_tieru['FQDN'].to_list()
    #     count_misses_tieru = _misses_tieru.shape[0]

    #     request_per_month = total_request/number_of_months
    #     request_per_day = total_request/number_of_days
    #     misses_per_month = total_misses/number_of_months
    #     misses_per_day = total_misses/number_of_days
    #     misses_percent = total_misses/total_request


    #     cola1, cola2 = st.columns([0.4, 0.6])

    #     with cola1:
    #         with st.container(border=True):
    #             # cap_option = st.radio(
    #             #     label='OPTIONS',
    #             #     options=['Missed', 'Captured', 'Request'],
    #             #     horizontal=False                
    #             # )
    #             cap_option = st.pills(
    #                 label='**:violet[OPTIONS]**',
    #                 options=['Missed', 'Captured', 'Request'],
    #                 width='stretch',
    #                 default='Missed'
    #             )
        
    #     with cola2:
    #         with st.container(border=True):
    #             year_selected = st.selectbox(
    #                 label='**:violet[YEAR]**',
    #                 options=year_list)
        
    #     # compute statistics
    #     with st.spinner('Processing Data', show_time=True):

    #         st.markdown(f"### Statistics ({client_selection})")

    #         st.markdown(f"#### Requests")
    #         st.markdown(f"""
    #         <div style="line-height: 0.3; font-size:20px;">
    #         <p style="color:#008B8B;"><b>Total: </b>{int(total_request):,}</p>
    #         <p style="color:#008B8B;"><b>Monthly Ave: </b>{int(request_per_month):,}</p>
    #         <p style="color:#008B8B;"><b>Daily Ave: </b>{int(request_per_day):,}</p>            
    #         </div>
    #         """, unsafe_allow_html=True)
    #         st.markdown(f"#### Misses")
    #         st.markdown(f"""
    #         <div style="line-height: 0.3; font-size:20px;">
    #         <p style="color:red;"><b>Total: </b>{int(total_misses):,} ({misses_percent:.2%})</p>
    #         <p style="color:red;"><b>Monthly Ave: </b>{int(misses_per_month):,}</p>
    #         <p style="color:red;"><b>Daily Ave: </b>{int(misses_per_day):,}</p>
    #         </div>
    #         """, unsafe_allow_html=True)
    #         st.markdown(f"#### Tier")           
            
    #         coltier1, coltier2 = st.columns([0.6, 0.4])

    #         with coltier1:
    #             if _misses_tier1_pub != 0:
    #                 with st.expander(
    #                     label=f':blue[**Tier 1 Missed: {count_misses_tier1}**]',
    #                 ):
    #                     _misses_tier1_pub = list(dict.fromkeys(_misses_tier1_pub))
    #                     for _pub in sorted(_misses_tier1_pub):
    #                         st.write(_pub)

    #             if _misses_tier2_pub != 0:
    #                 with st.expander(
    #                     label=f':blue[**Tier 2 Missed: {count_misses_tier2}**]'
    #                 ):
    #                     _misses_tier2_pub = list(dict.fromkeys(_misses_tier2_pub))
    #                     for _pub in sorted(_misses_tier2_pub):
    #                         st.write(_pub)

    #             if _misses_tier3_pub != 0:
    #                 with st.expander(
    #                     label=f':blue[**Tier 3 Missed: {count_misses_tier3}**]'
    #                 ):
    #                     _misses_tier3_pub = list(dict.fromkeys(_misses_tier3_pub))
    #                     for _pub in sorted(_misses_tier3_pub):
    #                         st.write(_pub)
                
    #             if _misses_tieru_pub != 0:
    #                 with st.expander(
    #                     label=f':blue[**Tier Unlisted Missed: {count_misses_tieru}**]'
    #                 ):
    #                     _misses_tieru_pub = list(dict.fromkeys(_misses_tieru_pub))
    #                     for _pub in sorted(_misses_tieru_pub):
    #                         st.write(_pub)

    #     if cap_option=='Captured':
    #         df_captured = df_clientfiltered[df_clientfiltered['CAPTURED'] == 1]
    #     elif cap_option=='Missed':
    #         df_captured = df_clientfiltered[df_clientfiltered['CAPTURED'] == 0]
    #     elif cap_option=='Request':
    #         df_captured = df_clientfiltered


    # with chart_col:

    #     month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    #     chart_cola1, chart_cola2 = st.columns([0.3, 0.7], border=True)
    #     with chart_cola1:
    #         with st.spinner('Generating Table', show_time=True):
    #             monthcount = df_captured['MONTH_NAME'].value_counts(sort=False)
    #             df_monthcount = monthcount.to_frame()
    #             df_monthcount = df_monthcount.reset_index()

    #             # Sort using categorical order
    #             df_monthcount['MONTH_NAME'] = pd.Categorical(df_monthcount['MONTH_NAME'], categories=month_order, ordered=True)
    #             df_monthcount = df_monthcount.sort_values('MONTH_NAME')

    #             st.dataframe(df_monthcount, hide_index=True)
    #     with chart_cola2:
    #         with st.spinner('Generating Chart', show_time=True):
    #             _chart1 = alt.Chart(df_monthcount, title=alt.TitleParams(f'Monthly {cap_option}', fontSize=40)).mark_bar().encode(
    #                 x=alt.X('MONTH_NAME', sort=month_order, title='Month'),
    #                 y=alt.Y('count', title='Count'))
    #             st.write(_chart1)     
    #     chart_colb1, chart_colb2 = st.columns([0.3, 0.7], border=True)
    #     with chart_colb1:
    #         with st.spinner('Generating Table', show_time=True):
    #             countdate = df_captured['DATE'].value_counts(sort=False)
    #             df_countdate = countdate.to_frame()
    #             df_countdate = df_countdate.reset_index()            
    #             st.dataframe(df_countdate, hide_index=True)
    #     with chart_colb2:
    #         with st.spinner('Generating Chart', show_time=True):
    #             _chart2 = alt.Chart(df_countdate, title=alt.TitleParams(f'Daily {cap_option}', anchor='middle')).mark_bar().encode(
    #                     x=alt.X('yearmonthdate(DATE):O', sort=None, title='Date', axis=alt.Axis(format='%b %d')),
    #                     y=alt.Y('count', title='Count'))
    #             st.write(_chart2)
        
    #     chart_colc1, chart_colc2 = st.columns([0.3, 0.7], border=True)
    #     with chart_colc1:
    #         with st.spinner('Generating Table', show_time=True):
    #             countfqdn = df_captured['FQDN'].value_counts(sort=True)
    #             df_fqdn = countfqdn.to_frame()
    #             df_fqdn = df_fqdn.reset_index()
    #             top10_fqdn = df_fqdn[:10]
    #             st.dataframe(top10_fqdn, hide_index=True)
    #     with chart_colc2:
    #         with st.spinner('Generating Chart', show_time=True):
    #             _chart3 = alt.Chart(top10_fqdn, title=alt.TitleParams(f'Top 10 {cap_option}', anchor='middle')).mark_bar().encode(
    #                     x=alt.X('FQDN', sort=None, title='FQDN'),
    #                     y=alt.Y('count', title='Count'))
    #             st.write(_chart3)

    #     chart_cold1, chart_cold2 = st.columns([0.3, 0.7], border=True)
    #     with chart_cold1:
    #         data = pd.DataFrame({
    #             'Category': ['Tier1', 'Tier2', 'Tier3', 'Unlisted'],
    #             'Value': [count_misses_tier1, count_misses_tier2, count_misses_tier3, count_misses_tieru]
    #             })
    #         st.dataframe(data, hide_index=True)

    #     with chart_cold2:
    #         # Create pie chart
    #         pie = alt.Chart(data).mark_arc().encode(
    #             theta=alt.Theta(field="Value", type="quantitative"),
    #             color=alt.Color(field="Category", type="nominal", legend=alt.Legend(orient='bottom')),
    #             tooltip=["Category", "Value"]

    #         ).properties(
    #             width=400,
    #             height=400,
    #             title=alt.TitleParams(
    #                 text="Distribution of Categories",
    #                 anchor="middle",   # centers the title
    #                 fontSize=18,
    #                 fontWeight="bold"
    #                 )
    #         )

    #         st.altair_chart(pie, use_container_width=True)
    

        



    return