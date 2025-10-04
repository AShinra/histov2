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
        
        if client_selection!='ALL':
            with st.container(border=True):
                st.header(f'{client_selection} - Requests and Misses Overview - Year 2025')

        cola, colb = st.columns([5,1])
        with cola:
            col13, col23 = st.columns([1,1])
            with col13:
                with st.container(border=True):
                    _monthly = working_df['MONTH'].value_counts(sort=False)
                    monthly_df = _monthly.to_frame()
                    if monthly_df.empty:
                        st.subheader('No Data to Plot')
                    else:
                        monthly_df = monthly_df.reset_index()

                        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

                        _chart1 = alt.Chart(monthly_df, title=alt.TitleParams(f'MONTHLY {_captured.upper()}', fontSize=40)).mark_bar().encode(
                            x=alt.X('MONTH', sort=month_order, title='Month', axis=alt.Axis(labelAngle=0, labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20)),
                            y=alt.Y('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20, values=list(range(0, monthly_df['count'].max() + 1)), format='.0f', grid=True)))
                        st.write(_chart1) 
                            
            with col23:
                with st.container(border=True):
                    _daily = working_df['DATE'].value_counts(sort=False)
                    daily_df = _daily.to_frame()
                    if daily_df.empty:
                        st.subheader('No Data to Plot')
                    else:
                        daily_df = daily_df.reset_index()
                    
                        _chart2 = alt.Chart(daily_df, title=alt.TitleParams(f'DAILY {_captured.upper()}', fontSize=40)).mark_bar().encode(
                            x=alt.X('yearmonthdate(DATE):O', sort=None, title='Date', axis=alt.Axis(format='%b %d', labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20, tickMinStep=1)),
                            y=alt.Y('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20, values=list(range(0, daily_df['count'].max() + 1)), format='.0f')))
                        st.write(_chart2)
            
            col14, col24 = st.columns([1,1])
            with col14:
                with st.container(border=True, height=450):
                    _fqdn = working_df['FQDN'].value_counts(sort=True)
                    fqdn_df = _fqdn.to_frame()
                    if fqdn_df.empty:
                        st.subheader('No Data to Plot')
                    else:
                        fqdn_df = fqdn_df.reset_index()
                        top10_fqdn_df = fqdn_df[:10]
                    
                        _chart2 = alt.Chart(top10_fqdn_df, title=alt.TitleParams(f'TOP 10 FQDN {_captured.upper()}', fontSize=40)).mark_bar().encode(
                            x=alt.X('count', title='Count', axis=alt.Axis(labelFontWeight='bold', labelFontSize=20, titleFontWeight='bold', titleFontSize=20, values=list(range(0, top10_fqdn_df['count'].max() + 1)), format='.0f')),
                            y=alt.Y('FQDN', sort=None, axis=alt.Axis(labelFontWeight='bold', titleFontWeight='bold', titleFontSize=20)))
                        st.write(_chart2)                   
            
            with col24:
                with st.container(border=True, height=450):
                    _tier = working_df['TIER'].value_counts(sort=True)
                    tier_df = _tier.to_frame()
                    if tier_df.empty:
                        st.subheader('No Data to Plot')
                    else:
                        tier_df = tier_df.reset_index()
                        tier_df['TIER'] = tier_df['TIER'].replace({0: 'Unlisted', 1: 'Tier 1', 2: 'Tier 2', 3: 'Tier 3'})

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
                    if tier1_missed_df.empty:
                        st.subheader('No Data to Show')
                    else:
                        tier1_fqdn_missed_df = tier1_missed_df['FQDN'].value_counts().reset_index()
                        st.dataframe(tier1_fqdn_missed_df, hide_index=True)
            
            with col25:
                with st.container(border=True, height=500):
                    st.subheader('TIER 2')
                    tier2_missed_df = working_df[working_df['TIER']==2]
                    if tier2_missed_df.empty:
                        st.subheader('No Data to Show')
                    else:
                        tier2_fqdn_missed_df = tier2_missed_df['FQDN'].value_counts().reset_index()
                        st.dataframe(tier2_fqdn_missed_df, hide_index=True)
            
            with col35:
                with st.container(border=True, height=500):
                    st.subheader('TIER 3')
                    tier3_missed_df = working_df[working_df['TIER']==3]
                    if tier3_missed_df.empty:
                        st.subheader('No Data to Show')
                    else:
                        tier3_fqdn_missed_df = tier3_missed_df['FQDN'].value_counts().reset_index()
                        st.dataframe(tier3_fqdn_missed_df, hide_index=True)
            
            with col45:
                with st.container(border=True, height=500):
                    st.subheader('UNLISTED')
                    tieru_missed_df = working_df[working_df['TIER']==0]
                    if tieru_missed_df.empty:
                        st.subheader('No Data to Show')
                    else:
                        tieru_fqdn_missed_df = tieru_missed_df['FQDN'].value_counts().reset_index()
                        st.dataframe(tieru_fqdn_missed_df, hide_index=True)

        with colb:
            if client_selection=='ALL':
                st.write('')
            else:
                with st.container(border=True):
                    client_df = df[(df['AGENCY']==agency_selection) & (df['CLIENT NAME']==client_selection)]

                    if client_df.empty:
                        st.subheader('No Data to Show')
                    else:
                        # get captured and misses count
                        captured_misses_df = client_df['CAPTURED'].value_counts().reset_index()
                        
                        try:
                            client_misses = int(captured_misses_df.loc[captured_misses_df['CAPTURED']==0, 'count'].iloc[0])
                        except:
                            client_misses = 0

                        try:
                            client_captured = int(captured_misses_df.loc[captured_misses_df['CAPTURED']==1, 'count'].iloc[0])
                        except:
                            client_captured = 0

                        client_requests = client_captured + client_misses
                        
                        # with st.container(border=True, horizontal_alignment='center'):
                        st.metric(
                            label=':blue[**Requests**]',
                            value=client_requests,
                            border=True
                        )

                        st.metric(
                            label=':green[**Captured**]',
                            value=client_captured,
                            border=True
                        )
                        
                        st.metric(
                            label=':red[**Misses**]',
                            value=client_misses,
                            border=True
                        )
                                            
                        st.metric(
                            label=':red[**Percentage**]',
                            value=f'{(client_misses/client_requests):.2%}',
                            border=True
                        )

                        st.metric(
                            label=f':red[**Tier1 Missed**] ({tier1_missed_df.shape[0]})',
                            value=f'{(tier1_missed_df.shape[0]/client_misses):.2%}',
                            border=True
                        )

                        st.metric(
                            label=f':red[**Tier2 Missed**] ({tier2_missed_df.shape[0]})',
                            value=f'{(tier2_missed_df.shape[0]/client_misses):.2%}',
                            border=True
                        )

                        st.metric(
                            label=f':red[**Tier3 Missed**] ({tier3_missed_df.shape[0]})',
                            value=f'{(tier3_missed_df.shape[0]/client_misses):.2%}',
                            border=True
                        )

                        st.metric(
                            label=f':red[**Unlisted Missed**] ({tieru_missed_df.shape[0]})',
                            value=f'{(tieru_missed_df.shape[0]/client_misses):.2%}',
                            border=True
                        )