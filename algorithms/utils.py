def transform_id_to_int(df_checkin_city):
    poi_int_id=df_checkin_city.reset_index()['business_id'].drop_duplicates().reset_index(drop=True).to_dict()
    poi_num=len(poi_int_id)
    user_int_id=df_checkin_city.reset_index().user_id.drop_duplicates().reset_index(drop=True).to_dict()
    user_num=len(user_int_id)
    for i,j in poi_int_id.copy().items():
        poi_int_id[j]=i
    for i,j in user_int_id.copy().items():
        user_int_id[j]=i
    df_checkin_city['user_id']=df_checkin_city['user_id'].apply(lambda user_id:user_int_id[user_id])
    df_checkin_city['business_id']=df_checkin_city['business_id'].apply(lambda poi_id:poi_int_id[poi_id])
    return user_int_id,poi_int_id

