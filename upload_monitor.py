import common
from datetime import date, datetime, timedelta
from bson.objectid import ObjectId
import streamlit as st
import pandas as pd

def upload_monitor():
    common.page_title('Website Upload Monitoring')

    # get collection from mongodb
    try:
        collection = common.connect_to_zeno_collections('articles_app_article')
    except:
        pass
    else:

        # website dict
        web_dict = {
            'Inquirer':'inquirer.net',
            'Manila Bulletin':'mb.com.ph',
            'Philstar':'philstar.com',
            "Business World":'bworldonline.com',
            'BusinessMirror':'businessmirror.com.ph',
            'Manila Times':'manilatimes.net',
            'Manila Standard Today':'manilastandard.net',
            'Daily Tribune':'tribune.net.ph',
            'Malaya Business Insight':'malaya.com.ph',
            'Bilyonaryo':'bilyonaryo.com'
        }
        
        st_date = st.date_input(
            label=':calendar: :violet[**DATE RANGE**]',
            width=200)

        # get yesterdays date
        end_date = st_date - timedelta(days=1)

        st_month = st_date.month
        st_day = st_date.day
        st_year = st_date.year

        end_month = end_date.month
        end_day = end_date.day
        end_year = end_date.year

        btn_get = st.button(
            label='Get Data',
            width=200)

        if btn_get:
            with st.spinner(
                text='Loading Data.....',
                show_time=True):
                with st.container(width=500):
                    data = []
                    for _name, _link in web_dict.items():
                        query = {
                            "created_by_id": ObjectId("619f0998a834a290ce4ef787"),
                            "media_source.media_source_type_flag": "web",
                            "date_publish": {
                                "$gte": datetime(end_year, end_month, end_day, 16, 0, 0),
                                "$lt": datetime(st_year, st_month, st_day, 16, 0, 0)},
                            "article_url": {"$regex": _link, "$options": "i"}
                            }
                        
                        query2 = {
                            "media_source.media_source_type_flag": "web",
                            "date_publish": {
                                "$gte": datetime(end_year, end_month, end_day, 16, 0, 0),
                                "$lt": datetime(st_year, st_month, st_day, 16, 0, 0)},
                            "article_url": {"$regex": _link, "$options": "i"}
                            }
                        
                        # Count documents matching the query
                        count_auto = collection.count_documents(query)
                        count_all = collection.count_documents(query2)
                        count_manual = count_all - count_auto

                        data.append(
                            {
                                'Website':_name,
                                'Auto':count_auto,
                                'Manual':count_manual,
                                'Total':count_all
                            }
                        )

                    df = pd.DataFrame(data)
                    st.dataframe(df, hide_index=True)