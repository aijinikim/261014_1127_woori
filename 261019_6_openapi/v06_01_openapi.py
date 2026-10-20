import os                # 환경변수(ITS_API_KEY)에서 인증 키 읽는 도구
import urllib.request   # 인터넷 주소로 자료 요청하는 도구
import json             # 글자로 된 자료를 사전(dict) 모양으로 바꾸는 도구
import pandas as pd     # 자료를 엑셀 같은 표로 다루는 도구

# 1. 인증 키
key = os.getenv("ITS_API_KEY", "YOUR_API_KEY")
# 과금 우려있는 API KEY는 코드 노출 그리고 깃허브에 업로드 하지 않음
# .env 환경변수로 관리

# 2. 도로 유형(its=일반도로, ex=고속도로) -> 어느 도로 CCTV 가져올지 선택
road_type = "its"

# 3. 관심 영역(경도, 위도 범위)
minX, maxX = 120.95, 127.02
minY, maxY = 30.55, 37.69
getType = "json"    # 응답 형식 : JSON(글자로 정리된 자료)

# 4. API URL 조립
url_cctv = (
    f"https://openapi.its.go.kr:9443/cctvInfo"
    f"?apiKey={key}&type={road_type}&cctvType=1"
    f"&minX={minX}&maxX={maxX}"
    f"&minY={minY}&maxY={maxY}&getType={getType}"
)

# 5. 요청(만든 주소로 "자료 주세요!")
response = urllib.request.urlopen(url_cctv)
# print(response)
# <http.client.HTTPResponse object at 0x00000258469C9C60>

# 6. bytes -> str
json_str = response.read().decode("utf-8") # bytes -> str (사람 글자)
# print(json_str)
# Kyxk/3V2yAv0GlgUNiwkjtFe6wmPNdxP+5QhCKEuBSMS2Q="},{"roadsectionid":"","coordx":126.976723,"coordy":36.811052,"cctvresolution":"","filecreatetime":"","cctvtype":1,"cctvformat":"HLS","cctvname":"[국도 39호선] 아산 곡교교차로","cctvurl":"http://cctvsec.ktict.co.kr/4183/7/iHyNIC1UzhXRELnvzcgNSAdfPgOpvaz5A8h

json_dict = json.loads(json_str)    # str -> dict (사전 모양)
# print(json_dict)
# {'roadsectionid': '', 'coordx': 126.989589, 'coordy': 36.80039, 'cctvresolution': '', 'filecreatetime': '', 'cctvtype': 1, 'cctvformat': 'HLS', 'cctvname': '[국도 39호선] 아산 옥정교차로', 'cctvurl': 'http://cctvsec.ktict.co.kr/4182/WVAXQOaxRWYYpMmnQTumP5mSabVLMVR4et25y5LWsMraovwKUSbOF+W8YCTW3KyxED34BZf/7RPo3GNHxWwcyAuKI7xQDgPIoYgQZAK75qk='}

# 7. 데이터 프레임 변환
cctv_play = pd.json_normalize(
    json_dict["response"]["data"], sep=''
)
# print(cctv_play)
#      roadsectionid      coordx     coordy  ... cctvformat             cctvname                                            cctvurl
# 0                   126.261960  36.751058  ...        HLS    [국도38] 태안 두야교회교차로  http://cctvsec.ktict.co.kr/4027/GS9cuqRaCq9cmh...
# 1                   126.612830  36.366430  ...        HLS  [국도 21호선] 보령 봉황터널시점  http://cctvsec.ktict.co.kr/4107/YVJDetuWhH2gGu...
# 2                   126.595440  36.378530  ...        HLS  [국도 21호선] 보령 봉황터널종점  http://cctvsec.ktict.co.kr/4108/uEw2V7VUiudn1P...
# 3                   126.617068  36.506767  ...        HLS  [국도 21호선] 홍성 단아래사거리  http://cctvsec.ktict.co.kr/4109/XIgVIAd5Mc+EOX...
# 4                   126.463910  36.775370  ...        HLS   [국도 29호선] 서산 석림사거리  http://cctvsec.ktict.co.kr/4120/bUjLufPLscQPC/...

# 8. CCTV URL 출력
test_url = cctv_play["cctvurl"][999]
# print(f"선택된 CCTV URL : {test_url}")