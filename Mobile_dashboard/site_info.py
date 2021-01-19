import requests
import pandas as pd
import load_cfg as cfg
import load_data as ld
import log_writer as lw

start_date = ld.GetPeriodForSite(ld.current_year, ld.current_week)[0]
end_date = ld.GetPeriodForSite(ld.current_year, ld.current_week)[1]


def get_site_info(start_date, end_date):
    headers = {'Authorization': 'OAuth ' + cfg.token}
    sources_sites = {
        'metrics': 'ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds',
        'dimensions': 'ym:s:startURL,ym:s:startURLPathLevel1,ym:s:startURLPathLevel2,ym:s:startURLPathLevel3,'
                      'ym:s:startURLPathLevel4',
        'date1': start_date,
        'date2': end_date,
        'ids': 23871871,
        'filters': "ALL(ym:s:startURL=='https://mbufk.roskazna.gov.ru/')"
    }

    response = requests.get('https://api-metrika.yandex.net/stat/v1/data', params=sources_sites, headers=headers)
    print(response.status_code)
    lw.log_writer(f"server response code {response.status_code}")

    metrika_data = response.json()

    list_of_dicts = []
    dimensions_list = metrika_data['query']['dimensions']
    metrics_list = metrika_data['query']['metrics']
    for data_item in metrika_data['data']:
        d = {}
        for i, dimension in enumerate(data_item['dimensions']):
            d[dimensions_list[i]] = dimension['name']
        for i, metric in enumerate(data_item['metrics']):
            d[metrics_list[i]] = metric
        list_of_dicts.append(d)

    metrika_df = pd.DataFrame(list_of_dicts)

    return metrika_df
