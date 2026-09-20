import streamlit as st
import toml
import pandas as pd


st.set_page_config(layout="wide")


@st.cache_data()
def load_data(filename):
    return toml.load(filename)


def make_dataframe(groups):
    # TOML 구조: {카테고리: {보이스 그룹: [악기, ...]}}
    # make_toml.py 가 만드는 [["카테고리"."그룹"]] 테이블과 같은 모양이다.
    flat_list = []
    for group, instruments in groups.items():
        for inst in instruments:
            # 보이스 그룹 정보를 추가하여 새로운 딕셔너리 생성
            row = {'Category': group}
            row.update(inst)
            flat_list.append(row)
    df = pd.DataFrame(flat_list)
    df['bank'] = 128*df['msb'] + df['lsb']
    df = df[['Category', 'name', 'bank', 'msb', 'lsb', 'prog']]
    return df

@st.cache_data()
def convert_data_to_dataframes(data):
    return [(category, make_dataframe(data[category])) for category in data]


def main():
    st.title("MIDI Instrument Finder")
    data_info = {
        'Yamaha CLP 685': 'data/yamaha-clp685-data.toml',
    }
    # device = st.radio('Select Device', ['Yamaha CLP 685', 'Roland HP605'], captions=['Yamaha CLP 685', 'Roland HP605'], horizontal=True)
    device = st.radio('Select Device', data_info.keys(), horizontal=True)

    if device not in data_info:
        st.error(f'Not supported device: {device}')
        return

    data = load_data(data_info[device])
    df_list = convert_data_to_dataframes(data)
    selected_categories = [0]*len(df_list)
    input_text = st.text_input('Find instrument(regex):', icon=':material/search:')
    cols = st.columns(len(df_list), border=True)
    for index, (col, (group, df)) in enumerate(zip(cols, df_list)):
        with col:
            st.subheader(f'{group}')

            values = df.groupby('Category').groups.keys()
            selected_categories[index]=st.pills('Categories', values, selection_mode='multi', width='stretch', help='Click one or more categories')

            st.divider()

            filter_df = df[df['Category'].isin(selected_categories[index])]
            if input_text:
                filter_df = filter_df[filter_df['name'].str.contains(input_text, case=False)]

            if len(filter_df) > 0:
                st.dataframe(filter_df)
            else:
                st.warning(f'No matching instrument for {group}')


if __name__ == '__main__':
    main()
