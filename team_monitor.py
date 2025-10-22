import streamlit as st
from common import connect_to_zeno, connect_to_articles
from datetime import date, datetime, timedelta
import pandas as pd




def team_monitor():

    db = connect_to_zeno()
    article_collection = connect_to_articles()

    collection = db['users_app_user']
    documents = collection.find({
        'department_label_name':'Online News',
        '$or':[
            {'first_name':'terrence'},
            {'first_name':'joel'},
            {'first_name':'Virna'},
            {'first_name':'Mary Rose'}]
        })
    
    _users = {}
    for document in documents:
        _users[document['first_name']] = document['_id']

    today = date.today()
    tom = today + timedelta(days=1)
    
    st.subheader('OUTPUT TODAY')
    
    today_month = today.month
    today_day = today.day
    today_year = today.year

    tom_month = tom.month
    tom_day = tom.day
    tom_year = tom.year      

    cola, colb = st.columns(2)
    with cola:
        i = 1
        cols = st.columns(4)

        for first_name, user_id in _users.items():
            count = article_collection.count_documents({
                'created_by_id':user_id,
                "date_created": {
                    "$gte": datetime(today_year, today_month, today_day, 0, 0, 0),
                    "$lt": datetime(tom_year, tom_month, tom_day, 0, 0, 0)}})
            
            with cols[i % 4]:
                st.metric(
                    label=first_name.upper(),
                    value=count,
                    border=True
                )

                results = list(article_collection.find({
                    'created_by_id':user_id,
                    "date_created": {
                        "$gte": datetime(today_year, today_month, today_day, 0, 0, 0),
                        "$lt": datetime(tom_year, tom_month, tom_day, 0, 0, 0)}
                        },
                    {
                        '_id':0,
                        'publisher':1,
                        'article_clean_url':1
                    }))
                
                df = pd.DataFrame(results)
                st.dataframe(df, hide_index=True)

            i += 1
    
    start_date = today
    end_date = today

    _date = st.date_input(
        label=':calendar: :violet[**DATE RANGE**]',
        key='b_date',
        value=(start_date, end_date),
        min_value=date(2025, 1, 1),
        max_value=date(2030, 12, 31),
        width=200)
    
    with st.spinner(text='Loading Data...', show_time=True):
        try:
            st_date = _date[0]
            en_date = _date[1] + timedelta(days=1)

            st_month = st_date.month
            st_day = st_date.day
            st_year = st_date.year

            en_month = en_date.month
            en_day = en_date.day
            en_year = en_date.year

            
            col1, col2 = st.columns(2)
            with col1:
                i = 1
                cols = st.columns(4)
                for first_name, user_id in _users.items():
                    count = article_collection.count_documents({
                        'created_by_id':user_id,
                        "date_created": {
                            "$gte": datetime(st_year, st_month, st_day, 0, 0, 0),
                            "$lt": datetime(en_year, en_month, en_day, 0, 0, 0)}
                    })
                    with cols[i % 4]:
                        st.metric(
                            label=first_name.upper(),
                            value=count,
                            border=True
                        )

                    i += 1

        except:
            pass