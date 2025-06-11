import streamlit as st
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import json
import pandas as pd
import joblib

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="서울 날씨 & 모기 지수",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [수정됨] 커스텀 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

    /* 전체 배경 및 폰트 설정 */
    .stApp {
        background: linear-gradient(135deg, #1a1a3a 0%, #0f0c29 100%);
        font-family: 'Nanum Gothic', sans-serif;
    }

    /* 기본 컨테이너 (너비 조정) */
    .main-container {
        max-width: 1100px; /* 너비 축소 */
        margin: 0 auto;
        padding: 1.5rem; /* 패딩 약간 축소 */
    }

    /* 타이틀 스타일 (폰트 크기 조정) */
    .main-title {
        text-align: center; font-size: 3.2rem; font-weight: 800; /* 폰트 크기 축소 */
        margin-bottom: 0.5rem; letter-spacing: -2px;
        background: linear-gradient(90deg, #89f7fe, #66a6ff, #a1c4fd);
        -webkit-background-clip: text; background-clip: text;
        color: transparent;
        text-shadow: 0 0 5px rgba(174, 214, 241, 0.5), 0 0 15px rgba(137, 247, 254, 0.5), 0 0 30px rgba(102, 166, 255, 0.4);
    }
    .sub-title {
        text-align: center; font-size: 1.2rem; margin-bottom: 2.5rem; font-weight: 400; /* 폰트/마진 축소 */
        color: rgba(255,255,255,0.85);
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    }

    /* 카드 공통 스타일 (리퀴드 글래스) (패딩, 그림자 조정) */
    .liquid-card {
        background: radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.3), transparent 40%),
                    linear-gradient(to right bottom, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; /* 테두리 반경 축소 */
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
        padding: 1.8rem; /* 패딩 축소 */
        margin: 1rem 0;
    }
    .liquid-card:hover {
        transform: translateY(-8px) scale(1.01); /* 호버 효과 미세 조정 */
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        border-color: rgba(255, 255, 255, 0.4);
    }

    /* 현재 날씨 카드 (크기 및 폰트 조정) */
    .current-weather {
        min-height: 350px; /* 최소 높이 축소 */
        display: flex; flex-direction: column;
        justify-content: center; align-items: center; position: relative;
    }
    .current-weather-icon { width: 110px; height: 110px; margin-bottom: 0.8rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.3)); } /* 아이콘 크기 축소 */
    .current-temp { font-size: 4.5rem; font-weight: 800; color: white; text-shadow: 0 0 20px rgba(0,0,0,0.5); line-height: 1; } /* 폰트 크기 축소 */
    .current-condition { font-size: 1.6rem; color: rgba(255,255,255,0.95); font-weight: 700; margin-top: 0.8rem; } /* 폰트 크기 축소 */
    .current-time { font-size: 0.9rem; color: rgba(255,255,255,0.8); position: absolute; top: 20px; right: 25px; } /* 폰트 크기 축소 */

    /* 상세 정보 (간격 및 폰트 조정) */
    .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1.2rem; margin-top: 1.5rem; } /* 간격, 마진 축소 */
    .detail-item, .forecast-card {
        background: radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.2), transparent 50%),
                    linear-gradient(to right bottom, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 25px; /* 테두리 반경 축소 */
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        padding: 1.2rem; /* 패딩 축소 */
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .detail-item:hover, .forecast-card:hover { transform: translateY(-6px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3); border-color: rgba(255, 255, 255, 0.3); } /* 호버 효과 조정 */
    .forecast-card { padding: 1.2rem 0.8rem; height: 100%; } /* 패딩 축소 */
    .detail-icon { font-size: 2.2rem; margin-bottom: 0.4rem; } /* 아이콘 크기/마진 축소 */
    .detail-label { color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-bottom: 0.4rem; } /* 폰트 크기/마진 축소 */
    .detail-value { color: white; font-size: 1.4rem; font-weight: 700; } /* 폰트 크기 축소 */

    /* 시간별 예보 (크기 및 폰트 조정) */
    .forecast-time { color: rgba(255,255,255,0.9); font-size: 1.1rem; font-weight: 700; margin-bottom: 0.8rem; } /* 폰트 크기/마진 축소 */
    .forecast-icon { width: 45px; height: 45px; margin: 0.4rem 0; } /* 아이콘 크기/마진 축소 */
    .forecast-temp { color: white; font-size: 1.4rem; font-weight: 700; } /* 폰트 크기 축소 */
    .forecast-condition { color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 0.4rem; } /* 폰트 크기/마진 축소 */
    
    /* [수정됨] 모기 지수 카드 스타일 (4단계) */
    .mosquito-card {
        padding: 1.8rem 2rem;
        text-align: center;
        min-height: 350px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    /* 1단계: 쾌적 */
    .mosquito-good { border-color: #66a6ff; } 
    /* 2단계: 관심 */
    .mosquito-watch { border-color: #fdd835; } 
    /* 3단계: 주의 (새로 추가) */
    .mosquito-caution { border-color: #fb8c00; }
    /* 4단계: 불쾌 */
    .mosquito-bad { border-color: #d81b60; }

    .mosquito-title {
        font-size: 1.2rem; font-weight: 700;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 0.8rem;
    }
    .mosquito-value {
        font-size: 2.5rem; font-weight: 800;
        color: white; line-height: 1.2;
    }
    .mosquito-desc {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.8rem;
    }
    .detail-icon-svg, .mosquito-title-icon-svg {
        width: 2.2rem;
        height: 2.2rem;
        filter: invert(1) drop-shadow(0 0 5px rgba(255, 255, 255, 0.3)); /* 흰색으로 만들고 그림자 효과 */
        margin-bottom: 0.4rem;
    }
    .mosquito-title-icon-svg {
        width: 1.5rem; /* 타이틀 옆 아이콘은 약간 작게 */
        height: 1.5rem;
        margin-right: 0.5rem;
        vertical-align: -0.25rem; /* 텍스트와 세로 정렬 */
        }
    .mosquito-level-icon-svg {
    width: 2.3rem; /* 단계 텍스트와 어울리는 크기 */
        height: 2.3rem;
        filter: invert(1) drop-shadow(0 0 5px rgba(255, 255, 255, 0.3)); /* 흰색 아이콘, 그림자 효과 */
        margin-left: 0.5rem;
        vertical-align: -0.5rem; /* 큰 텍스트 옆에서 세로 중앙 정렬 */
        }

    /* 에러 메시지 */
    .error-message {
        background: rgba(255, 87, 87, 0.2); border-radius: 20px; padding: 1rem; color: white;
        text-align: center; margin: 1rem 0; border: 1px solid rgba(255, 87, 87, 0.3);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    }
    /* Streamlit 기본 요소 숨기기 */
    .stDeployButton, footer, .stApp > header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- API 및 날씨 정보 설정 ---
# ※※※ 중요: 본인의 공공데이터포털 일반 인증키(Decoding)로 교체하세요 ※※※
API_KEY = st.secrets["API_KEY"]
SEOUL_NX = 60
SEOUL_NY = 127

# 아이콘 및 날씨 텍스트 매핑
SKY_ICONS = {'1': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/day.svg", '3': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/cloudy-day-1.svg", '4': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/cloudy.svg"}
PTY_ICONS = {'1': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/rainy-6.svg", '2': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/rainy-7.svg", '3': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/snowy-6.svg", '5': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/rainy-1.svg", '6': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/rainy-7.svg", '7': "https://www.amcharts.com/wp-content/themes/amcharts4/css/img/icons/weather/animated/snowy-5.svg"}
SKY_DICT = {'1': '맑음', '3': '구름많음', '4': '흐림'}
PTY_DICT = {'0': '없음', '1': '비', '2': '비/눈', '3': '눈', '5': '빗방울', '6': '빗방울눈날림', '7': '눈날림'}

# --- 모델 로드 ---
@st.cache_resource
def load_models():
    try:
        # ※※※ 중요: 모델 파일의 경로를 실제 환경에 맞게 수정해주세요. ※※※
        # 예: model_rf = joblib.load("models/random_forest_model.pkl")
        model_rf = joblib.load(r"C:\Users\itwill\Downloads\random_forest_model.pkl")
        model_xgb = joblib.load(r"C:\Users\itwill\Downloads\xgboost_model.pkl")
        return model_rf, model_xgb
    except FileNotFoundError:
        return None, None

# --- 핵심 함수들 ---
def api_call(url, params):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get('response', {})
        if data.get('header', {}).get('resultCode') == '00':
            return {'success': True, 'data': data}
        else:
            return {'success': False, 'error': data.get('header', {}).get('resultMsg')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@st.cache_data(ttl=600)
def get_live_observation(nx, ny):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    now = datetime.now()
    target_time = now - timedelta(minutes=45)
    base_date = target_time.strftime('%Y%m%d')
    base_time = target_time.strftime('%H00')
    params = {"serviceKey": API_KEY, "numOfRows": 100, "pageNo": 1, "dataType": "JSON", "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny}
    result = api_call(url, params)
    if result['success']:
        items = result['data'].get('body', {}).get('items', {}).get('item', [])
        live_data = {item['category']: item['obsrValue'] for item in items}
        result['data'] = live_data
        result['base_time'] = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]} {base_time[:2]}:00"
    return result

@st.cache_data(ttl=600)
def get_ultra_short_term_forecast(nx, ny):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    now = datetime.now()
    target_time = now - timedelta(minutes=45)
    base_date = target_time.strftime('%Y%m%d')
    base_time = target_time.strftime('%H30')
    params = {"serviceKey": API_KEY, "numOfRows": 100, "pageNo": 1, "dataType": "JSON", "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny}
    result = api_call(url, params)
    if result['success']:
        items = result['data']['body']['items']['item']
        forecast_data = defaultdict(dict)
        for item in items:
            forecast_data[item['fcstTime']][item['category']] = item['fcstValue']
        result['data'] = forecast_data
        result['base_time'] = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]} {base_time[:2]}:{base_time[2:]}"
    return result

@st.cache_data(ttl=1800)
def get_short_term_forecast(nx, ny):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    if now.hour < 2 or (now.hour == 2 and now.minute < 45):
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
    params = {"serviceKey": API_KEY, "numOfRows": 1000, "pageNo": 1, "dataType": "JSON", "base_date": base_date, "base_time": "0200", "nx": nx, "ny": ny}
    result = api_call(url, params)
    if result['success']:
        items = result['data'].get('body', {}).get('items', {}).get('item', [])
        today_str = datetime.now().strftime('%Y%m%d')
        daily_data = {}
        for item in items:
            if item['category'] == 'TMX' and item['fcstDate'] == today_str:
                daily_data['TMX'] = item['fcstValue']
            if item['category'] == 'TMN' and item['fcstDate'] == today_str:
                daily_data['TMN'] = item['fcstValue']
            if 'TMX' in daily_data and 'TMN' in daily_data:
                break
        result['data'] = daily_data
        result['base_time'] = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]} 02:00"
    return result

# --- AI 예측에 필요한 데이터를 가공하는 함수 ---
@st.cache_data(ttl=1800)
def get_daily_forecast_for_model(nx, ny):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    now = datetime.now()
    base_date = (now - timedelta(days=1)).strftime("%Y%m%d") if now.hour < 3 else now.strftime("%Y%m%d")
    base_time = "2300" if now.hour < 3 else "0200"
    params = {"serviceKey": API_KEY, "numOfRows": 1000, "pageNo": 1, "dataType": "JSON", "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny}
    result = api_call(url, params)
    
    if not result.get('success') or result['data'].get('header', {}).get('resultCode') != '00':
        return {'success': False, 'error': '일별 예보 데이터 호출 실패'}
        
    items = result['data']['body']['items']['item']
    today_str = now.strftime('%Y%m%d')
    
    daily_temps = [float(item['fcstValue']) for item in items if item['fcstDate'] == today_str and item['category'] == 'TMP']
    daily_precip_str = [item['fcstValue'] for item in items if item['fcstDate'] == today_str and item['category'] == 'PCP']
    daily_precip = [float(p[:-2]) for p in daily_precip_str if 'mm' in p] # 'mm' 단위 처리
    daily_humidity = [float(item['fcstValue']) for item in items if item['fcstDate'] == today_str and item['category'] == 'REH']
    daily_wind = [float(item['fcstValue']) for item in items if item['fcstDate'] == today_str and item['category'] == 'WSD']

    model_features = {
        'avg_temp': sum(daily_temps) / len(daily_temps) if daily_temps else 0,
        'rainfall': sum(daily_precip) if daily_precip else 0,
        'humidity': sum(daily_humidity) / len(daily_humidity) if daily_humidity else 0,
        'wind_speed': sum(daily_wind) / len(daily_wind) if daily_wind else 0,
    }
    return {'success': True, 'data': model_features}

# --- 메인 앱 실행 ---
def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🌤️ 서울 날씨 & 모기 지수</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">실시간 날씨와 AI가 예측한 모기 활동 지수를 확인하세요.</p>', unsafe_allow_html=True)

    model_rf, model_xgb = load_models()
    if not model_rf or not model_xgb:
        st.error("오류: 모기 예측 모델 파일(random_forest_model.pkl, xgboost_model.pkl)을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    live_result = get_live_observation(SEOUL_NX, SEOUL_NY)
    ultra_short_result = get_ultra_short_term_forecast(SEOUL_NX, SEOUL_NY)
    short_term_result = get_short_term_forecast(SEOUL_NX, SEOUL_NY)
    model_data_result = get_daily_forecast_for_model(SEOUL_NX, SEOUL_NY)
    
    col1, col2 = st.columns(2)

    with col1:
        # --- 현재 날씨 카드 ---
        if live_result['success'] and live_result['data']:
            current_weather = live_result['data']
            pty_code = current_weather.get('PTY', '0')
            sky_code = current_weather.get('SKY', '1')

            if pty_code != '0':
                weather_icon = PTY_ICONS.get(pty_code)
                weather_text = PTY_DICT.get(pty_code)
            else:
                # 초단기예보에서 현재 하늘 상태 가져오기 (실시간 관측에 SKY가 없을 경우 대비)
                if ultra_short_result['success'] and ultra_short_result['data']:
                    first_forecast_time = sorted(ultra_short_result['data'].keys())[0]
                    sky_code = ultra_short_result['data'][first_forecast_time].get('SKY', sky_code) # 현재 관측값 우선
                weather_icon = SKY_ICONS.get(sky_code)
                weather_text = SKY_DICT.get(sky_code, '정보 없음')
            
            st.markdown(f"""
            <div class="liquid-card current-weather">
                <div class="current-time">{datetime.now().strftime('%Y-%m-%d %H:%M')} 기준</div>
                <img src="{weather_icon}" class="current-weather-icon" alt="{weather_text}">
                <div class="current-temp">{current_weather.get('T1H', '--')}°</div>
                <div class="current-condition">{weather_text}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='error-message'>❌ 실시간 관측 정보를 가져올 수 없습니다: {live_result.get('error', '알 수 없는 오류')}</div>", unsafe_allow_html=True)
            current_weather = {}

    with col2:
        # --- 모기 지수 예측 및 시각화 ---
        if model_data_result['success']:
            features = model_data_result['data']
            now = datetime.now()
            
            # 일사량은 예측에 큰 영향을 주지 않을 수 있으므로, 고정값 또는 평균값으로 대체
            # 여기서는 여름철 평균적인 값(15.0)을 가정하여 사용
            input_data = pd.DataFrame([[
                features['avg_temp'], features['rainfall'], features['humidity'],
                features['wind_speed'], 15.0, now.year, now.month 
            ]], columns=['평균기온(°C)', '일강수량(mm)', '평균 상대습도(%)', '평균 풍속(m/s)', '합계 일사량(MJ/m2)', 'year', 'month'])

            try:
                pred_rf = model_rf.predict(input_data)[0]
                pred_xgb = model_xgb.predict(input_data)[0]
                final_pred = (pred_rf + pred_xgb) / 2

                # --- [수정됨] 단계별 SVG 아이콘 URL 정의 ---
                mosquito_icon_url = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/bug-outline.svg"
                icon_url_good = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/happy-outline.svg"
                icon_url_watch = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/eye-outline.svg"
                icon_url_caution = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/warning-outline.svg"
                icon_url_bad = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/skull-outline.svg"
                
                # --- [수정됨] 모기 지수 4단계 분류 및 아이콘 태그 할당 ---
                if final_pred <= 25:
                    level, desc, color_class = "쾌적", "모기 활동이 거의 없어요.", "mosquito-good"
                    icon_tag = f'<img src="{icon_url_good}" class="mosquito-level-icon-svg">'
                elif final_pred <= 50:
                    level, desc, color_class = "관심", "모기 활동이 시작될 수 있어요.", "mosquito-watch"
                    icon_tag = f'<img src="{icon_url_watch}" class="mosquito-level-icon-svg">'
                elif final_pred <= 75:
                    level, desc, color_class = "주의", "모기 활동이 자주 관찰돼요.", "mosquito-caution"
                    icon_tag = f'<img src="{icon_url_caution}" class="mosquito-level-icon-svg">'
                else:
                    level, desc, color_class = "불쾌", "모기 활동이 매우 활발해요!", "mosquito-bad"
                    icon_tag = f'<img src="{icon_url_bad}" class="mosquito-level-icon-svg">'
                
                st.markdown(f"""
                <div class="liquid-card mosquito-card {color_class}">
                    <div class="mosquito-title">
                        <img src="{mosquito_icon_url}" class="mosquito-title-icon-svg">
                        오늘의 모기 활동 지수 (AI 예측)
                    </div>
                    <div class="mosquito-value">{level} {icon_tag}</div>
                    <div class="mosquito-desc">{desc}<br>(예측 지수: {final_pred:.1f})</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"모기 지수 예측에 실패했습니다: {e}")
        else:
            st.markdown(f"<div class='error-message'>❌ 모기 지수 예측 데이터를 가져올 수 없습니다: {model_data_result.get('error', '알 수 없는 오류')}</div>", unsafe_allow_html=True)

    # --- 상세 정보 (아이콘 교체) ---
    tmn = short_term_result['data'].get('TMN', '--') if short_term_result.get('success') else '--'
    tmx = short_term_result['data'].get('TMX', '--') if short_term_result.get('success') else '--'

    # SVG 아이콘 URL 정의
    icon_temp = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/thermometer-outline.svg"
    icon_humidity = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/water-outline.svg"
    icon_wind = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/flag-outline.svg"
    icon_rain = "https://cdn.jsdelivr.net/gh/ionic-team/ionicons@5.5.2/src/svg/rainy-outline.svg"

    st.markdown(f"""
    <div class="detail-grid">
        <div class="detail-item">
            <div class="detail-icon">
                <img src="{icon_temp}" class="detail-icon-svg">
            </div>
            <div class="detail-label">오늘 최고/최저</div>
            <div class="detail-value">{tmx}° / {tmn}°</div>
        </div>
        <div class="detail-item">
            <div class="detail-icon">
                <img src="{icon_humidity}" class="detail-icon-svg">
            </div>
            <div class="detail-label">습도</div>
            <div class="detail-value">{current_weather.get('REH', '--')}%</div>
        </div>
        <div class="detail-item">
            <div class="detail-icon">
                <img src="{icon_wind}" class="detail-icon-svg">
            </div>
            <div class="detail-label">풍속</div>
            <div class="detail-value">{current_weather.get('WSD', '--')} m/s</div>
        </div>
        <div class="detail-item">
            <div class="detail-icon">
                <img src="{icon_rain}" class="detail-icon-svg">
            </div>
            <div class="detail-label">1시간 강수량</div>
            <div class="detail-value">{current_weather.get('RN1', '0')} mm</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 시간별 예보 ---
    if ultra_short_result['success'] and ultra_short_result['data']:
        st.markdown("<h2 style='color: white; text-align: center; margin: 3rem 0 1rem 0; font-weight: 700;'>시간별 예보</h2>", unsafe_allow_html=True)
        forecast_data = ultra_short_result['data']
        forecast_times_to_display = sorted(list(forecast_data.keys()))[:6] # 최대 6개만 표시
        cols = st.columns(len(forecast_times_to_display))
        for i, time in enumerate(forecast_times_to_display):
            with cols[i]:
                weather = forecast_data[time]
                f_pty_code = weather.get('PTY', '0')
                f_sky_code = weather.get('SKY', '1')
                if f_pty_code != '0':
                    f_icon, f_text = PTY_ICONS.get(f_pty_code), PTY_DICT.get(f_pty_code)
                else:
                    f_icon, f_text = SKY_ICONS.get(f_sky_code), SKY_DICT.get(f_sky_code, '정보 없음')
                st.markdown(f"""
                <div class="forecast-card">
                    <div class="forecast-time">{time[:2]}:00</div>
                    <img src="{f_icon}" class="forecast-icon" alt="{f_text}">
                    <div class="forecast-temp">{weather.get('T1H', '--')}°</div>
                    <div class="forecast-condition">{f_text}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='error-message'>❌ 시간별 예보 정보를 가져올 수 없습니다: {ultra_short_result.get('error', '알 수 없는 오류')}</div>", unsafe_allow_html=True)
            
    # --- 업데이트 정보 ---
    st.markdown(f"""
    <div style="text-align: center; color: rgba(255,255,255,0.6); margin-top: 3rem; font-size: 0.8rem;">
        실시간 관측 발표: {live_result.get('base_time', 'N/A')} | 
        시간별 예보 발표: {ultra_short_result.get('base_time', 'N/A')} | 
        종합 예보 발표: {short_term_result.get('base_time', 'N/A')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY" or not API_KEY:
        st.error("오류: API_KEY를 코드에 입력해주세요. 공공데이터포털에서 발급받은 일반 인증키(Decoding)가 필요합니다.")
    else:
        main()
